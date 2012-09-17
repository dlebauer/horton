# -*- coding: utf-8 -*-
# Horton is a Density Functional Theory program.
# Copyright (C) 2011-2012 Toon Verstraelen <Toon.Verstraelen@UGent.be>
#
# This file is part of Horton.
#
# Horton is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# Horton is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
#--
"""Wavefunction implementations

   The essential part of the wavefunction consists of the expansion coefficients
   in a certain basis.
"""


import numpy as np

from horton.log import log
from horton.exceptions import ElectronCountError


__all__ = ['BaseWFN', 'ClosedShellWFN', 'OpenShellWFN']


class BaseWFN(object):
    def __init__(self, lf, nbasis, norb=None):
        """
           **Arguments:**

           lf
                A LinalgFactory instance.

           nbasis
                The number of basis functions.

           **Optional arguments:**

           norb
               the number of orbitals (occupied + virtual). When not given,
               it is set to nbasis.
        """
        self._lf = lf
        self._nbasis = nbasis
        if norb is None:
            self._norb = nbasis
        else:
            self._norb = norb

    @classmethod
    def from_hdf5(cls, grp, lf):
        clsname = grp.attrs['class']
        if clsname == 'ClosedShellWFN':
            return ClosedShellWFN.from_hdf5(grp, lf)
        elif clsname == 'OpenShellWFN':
            return OpenShellWFN.from_hdf5(grp, lf)
        else:
            raise TypeError('Can not load wavefunction of class %s from HDF5.' % clsname)

    def _get_nbasis(self):
        '''The number of basis functions.'''
        return self._nbasis

    nbasis = property(_get_nbasis)

    def _get_norb(self):
        '''The number of orbitals in the expansion(s)'''
        return self._norb

    norb = property(_get_norb)

    def log(self):
        '''Write a summary of the wavefunction to the screen logger'''
        with log.section('WFN'):
            log('Wavefunction object: %s' % self)
            log('Number of electrons: %i' % self.nel)
            labels = ['alpha', 'beta']
            for expansion, nocc, scale in self.iter_expansions('full'):
                log('Expansion for %s electrons:' % labels.pop(0))
                log('  Number of orbitals:          %i' % expansion.nfn)
                log('  Number of occupied orbitals: %i' % nocc)

    def iter_expansions(self):
        raise NotImplementedError

    def apply_basis_permutation(self, permutation):
        """Reorder the expansion coefficients"""
        for expansion, nocc, scale in self.iter_expansions():
            expansion.apply_basis_permutation(permutation)

    def compute_density_matrix(self, dm, select='full'):
        """Compute the density matrix

           **Arguments:**

           dm
                An output density matrix. This must be an instance of the
                One-body operator class of the linalg factory, self._lf.

           **Optional arguments:**

           select
                'alpha', 'beta', 'full' or 'spin'. ('full' is the default.)
        """
        dm.reset()
        for expansion, nocc, scale in self.iter_expansions(select):
            expansion.compute_density_matrix(nocc, dm, factor=scale)

    def check_normalization(self, olp, eps=1e-4):
        '''Run an internal test to see if the orbitals are normalized

           **Arguments:**

           olp
                The overlap one_body operators

           **Optional arguments:**

           eps
                The allowed deviation from unity, very loose by default.
        '''
        for expansion, nocc, scale in self.iter_expansions('full'):
            expansion.check_normalization(olp, nocc, eps)


class ClosedShellWFN(BaseWFN):
    closed_shell = True

    def __init__(self, nep, lf, nbasis, norb=None):
        """
           **Arguments:**

           nep
                The number of electron pairs in the wave function.

           lf
                A LinalgFactory instance

           nbasis
                The number of basis functions.

           **Optional arguments:**

           norb
               the number of orbitals (occupied + virtual). When not given,
               it is set to nbasis.
        """
        BaseWFN.__init__(self, lf, nbasis, norb)
        self._nep = nep

        if self.nep <= 0:
            raise ElectronCountError('At least one pair of electrons is required.')
        if self.nbasis < self.nep:
            raise ElectronCountError('The number of spatial basis functions must not be lower than the number of electron pairs.')

        self._expansion = lf.create_expansion(self.nbasis, self.norb, do_energies=True)

    @classmethod
    def from_hdf5(cls, grp, lf):
        result = ClosedShellWFN(grp['nep'][()], lf, nbasis=grp['nbasis'][()], norb=grp['norb'][()])
        result._expansion.read_from_hdf5(grp['expansion'])
        return result

    def to_hdf5(self, grp):
        grp['nep'] = self._nep
        grp['nbasis'] = self._nbasis
        grp['norb'] = self._norb
        grp_expansion = grp.create_group('expansion')
        self._expansion.to_hdf5(grp_expansion)

    def _get_nel(self):
        '''The number of electrons'''
        return self._nep*2

    nel = property(_get_nel)

    def _get_nep(self):
        '''The number of electron pairs'''
        return self._nep

    nep = property(_get_nep)

    def _get_expansion(self):
        '''The expansion of the orbitals'''
        return self._expansion

    expansion = property(_get_expansion)

    def iter_expansions(self, select='full'):
        '''Iterate over all expansions

           **Optional arguments:**

           select
                'alpha', 'beta', 'full' or 'spin'. ('full' is the default.)

           Yields records (expansion, nocc, scale) where:

           expansion
                An expansion of the orbitals.

           nocc
                The number of occupied orbitals.

           scale
                The occupancy of each orbital.
        '''
        if select == 'alpha':
            yield self._expansion, self._nep, 1
        elif select == 'beta':
            yield self._expansion, self._nep, 1
        elif select == 'full':
            yield self._expansion, self._nep, 2
        elif select == 'spin':
            return
        else:
            raise ValueError('select has to be one of alpha, beta, full or spin.')


class OpenShellWFN(BaseWFN):
    closed_shell = False

    def __init__(self, nalpha, nbeta, lf, nbasis, norb=None):
        """
           An unrestricted open-shell wavefunction.

           **Arguments:**

           nalpha
                The number of alpha electrons in the wave function.

           nbeta
                The number of beta electrons in the wave function.

           lf
                A LinalgFactory instance

           nbasis
                The number of basis functions.

           **Optional arguments:**

           norb
               the number of orbitals (occupied + virtual). When not given,
               it is set to nbasis.
        """
        BaseWFN.__init__(self, lf, nbasis, norb)
        self._nalpha = nalpha
        self._nbeta = nbeta

        if self.nalpha < 0 or self.nbeta < 0:
            raise ElectronCountError('Negative number of electrons is not allowed.')
        if self.nalpha == 0 and self.nbeta == 0:
            raise ElectronCountError('At least one alpha or beta electron is required.')
        if self.nbasis < self.nalpha or self.nbasis < self.nbeta:
            raise ElectronCountError('The number of spatial basis functions must not be lower than the number of alpha or beta electrons.')

        self._alpha_expansion = lf.create_expansion(self.nbasis, self.norb, do_energies=True)
        self._beta_expansion = lf.create_expansion(self.nbasis, self.norb, do_energies=True)

    @classmethod
    def from_hdf5(cls, grp, lf):
        result = OpenShellWFN(grp['nalpha'][()], grp['nbeta'][()], lf, nbasis=grp['nbasis'][()], norb=grp['norb'][()])
        result._alpha_expansion.read_from_hdf5(grp['alpha_expansion'])
        result._beta_expansion.read_from_hdf5(grp['beta_expansion'])
        return result

    def to_hdf5(self, grp):
        grp['nalpha'] = self._nalpha
        grp['nbeta'] = self._nbeta
        grp['nbasis'] = self._nbasis
        grp['norb'] = self._norb
        grp_alpha_expansion = grp.create_group('alpha_expansion')
        self._alpha_expansion.to_hdf5(grp_alpha_expansion)
        grp_beta_expansion = grp.create_group('beta_expansion')
        self._beta_expansion.to_hdf5(grp_beta_expansion)

    def _get_nel(self):
        '''The number of electrons'''
        return self._nalpha + self._nbeta

    nel = property(_get_nel)

    def _get_nalpha(self):
        '''The number of alpha electrons'''
        return self._nalpha

    nalpha = property(_get_nalpha)

    def _get_nbeta(self):
        '''The number of beta electrons'''
        return self._nbeta

    nbeta = property(_get_nbeta)

    def _get_alpha_expansion(self):
        '''The expansion of the alpha electrons'''
        return self._alpha_expansion

    alpha_expansion = property(_get_alpha_expansion)

    def _get_beta_expansion(self):
        '''The expansion of the beta electrons'''
        return self._beta_expansion

    beta_expansion = property(_get_beta_expansion)

    def iter_expansions(self, select='full'):
        '''Iterate over all expansions

           **Optional arguments:**

           select
                'alpha', 'beta', 'full' or 'spin'. ('full' is the default.)

           Yields records (expansion, nocc, scale) where:

           expansion
                An expansion of the orbitals.

           nocc
                The number of occupied orbitals.

           scale
                The occupancy of each orbital.
        '''
        if select == 'alpha':
            yield self._alpha_expansion, self._nalpha, 1
        elif select == 'beta':
            yield self._beta_expansion, self._nbeta, 1
        elif select == 'full':
            yield self._alpha_expansion, self._nalpha, 1
            yield self._beta_expansion, self._nbeta, 1
        elif select == 'spin':
            yield self._alpha_expansion, self._nalpha, 1
            yield self._beta_expansion, self._nbeta, -1
        else:
            raise ValueError('select has to be one of alpha, beta, full or spin.')
