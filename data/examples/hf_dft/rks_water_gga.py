#!/usr/bin/env python
#JSON {"lot": "RKS/6-31G*",
#JSON  "scf": "CDIISSCFSolver",
#JSON  "linalg": "CholeskyLinalgFactory",
#JSON  "difficulty": 4,
#JSON  "description": "Basic RKS DFT example with GGA exhange-correlation functional (PBE)"}

from horton import *

# Load the coordinates from file.
# Use the XYZ file from HORTON's test data directory.
fn_xyz = context.get_fn('test/water.xyz')
mol = IOData.from_file(fn_xyz)

# Create a Gaussian basis set
obasis = get_gobasis(mol.coordinates, mol.numbers, '6-31g*')

# Create a linalg factory
lf = CholeskyLinalgFactory(obasis.nbasis)

# Compute Gaussian integrals
olp = obasis.compute_overlap(lf)
kin = obasis.compute_kinetic(lf)
na = obasis.compute_nuclear_attraction(mol.coordinates, mol.pseudo_numbers, lf)
er = obasis.compute_electron_repulsion(lf)

# Define a numerical integration grid needed the XC functionals
grid = BeckeMolGrid(mol.coordinates, mol.numbers, mol.pseudo_numbers)

# Create alpha orbitals
exp_alpha = lf.create_expansion()

# Initial guess
guess_core_hamiltonian(olp, kin, na, exp_alpha)

# Construct the restricted HF effective Hamiltonian
external = {'nn': compute_nucnuc(mol.coordinates, mol.pseudo_numbers)}
terms = [
    RTwoIndexTerm(kin, 'kin'),
    RDirectTerm(er, 'hartree'),
    RGridGroup(obasis, grid, [
        RLibXCGGA('x_pbe'),
        RLibXCGGA('c_pbe'),
    ]),
    RTwoIndexTerm(na, 'ne'),
]
ham = REffHam(terms, external)

# Decide how to occupy the orbitals (5 alpha electrons)
occ_model = AufbauOccModel(5)

# Converge WFN with CDIIS SCF
# - Construct the initial density matrix (needed for CDIIS).
occ_model.assign(exp_alpha)
dm_alpha = exp_alpha.to_dm()
# - SCF solver
scf_solver = CDIISSCFSolver(1e-6)
scf_solver(ham, lf, olp, occ_model, dm_alpha)

# Derive orbitals (coeffs, energies and occupations) from the Fock and density
# matrices. The energy is also computed to store it in the output file below.
fock_alpha = lf.create_two_index()
ham.reset(dm_alpha)
ham.compute_energy()
ham.compute_fock(fock_alpha)
exp_alpha.from_fock_and_dm(fock_alpha, dm_alpha, olp)

# Assign results to the molecule object and write it to a file, e.g. for
# later analysis. Note that the CDIIS algorithm can only really construct an
# optimized density matrix and no orbitals.
mol.title = 'RKS computation on water'
mol.energy = ham.cache['energy']
mol.obasis = obasis
mol.exp_alpha = exp_alpha
mol.dm_alpha = dm_alpha

# useful for post-processing (results stored in double precision):
mol.to_file('water.h5')


# CODE BELOW IS FOR horton-regression-test.py ONLY. IT IS NOT PART OF THE EXAMPLE.
rt_results = {
    'energy': ham.cache['energy'],
    'exp_alpha': exp_alpha.energies,
    'nn': ham.cache["energy_nn"],
    'kin': ham.cache["energy_kin"],
    'ne': ham.cache["energy_ne"],
    'grid': ham.cache["energy_grid_group"],
    'hartree': ham.cache["energy_hartree"],
}
# BEGIN AUTOGENERATED CODE. DO NOT CHANGE MANUALLY.
import numpy as np  # pylint: disable=wrong-import-position
rt_previous = {
    'nn': 9.1571750364299866,
    'energy': -76.319084427488619,
    'ne': -199.04148828027468,
    'grid': -9.267855936139593,
    'exp_alpha': np.array([
        -18.741672978950461, -0.90374530546849496, -0.47272952595437728,
        -0.29901662535828072, -0.22546093120826446, 0.047113391069072683,
        0.12992415962063619, 0.75421776755224246, 0.79452689228743334,
        0.84502433953276623, 0.8744012627954636, 1.0198907802886903, 1.3210060346115535,
        1.6703880093651589, 1.6760834760065273, 1.717079633954907, 2.2301060022659764,
        2.514325612661326
    ]),
    'hartree': 46.845521667482906,
    'kin': 75.98756308501275,
}
