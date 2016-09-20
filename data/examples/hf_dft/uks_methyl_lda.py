#!/usr/bin/env python
#JSON {"lot": "UKS/6-31G*",
#JSON  "scf": "ODASCFSolver",
#JSON  "linalg": "CholeskyLinalgFactory",
#JSON  "difficulty": 3,
#JSON  "description": "Basic UKS DFT example with LDA exhange-correlation functional (Dirac+VWN)"}

from horton import *

# Load the coordinates from file.
# Use the XYZ file from HORTON's test data directory.
fn_xyz = context.get_fn('test/methyl.xyz')
mol = IOData.from_file(fn_xyz)

# Create a Gaussian basis set
obasis = get_gobasis(mol.coordinates, mol.numbers, '6-31g*')

# Create a linalg factory
lf = DenseLinalgFactory(obasis.nbasis)

# Compute Gaussian integrals
olp = obasis.compute_overlap(lf)
kin = obasis.compute_kinetic(lf)
na = obasis.compute_nuclear_attraction(mol.coordinates, mol.pseudo_numbers, lf)
er = obasis.compute_electron_repulsion(lf)

# Define a numerical integration grid needed the XC functionals
grid = BeckeMolGrid(mol.coordinates, mol.numbers, mol.pseudo_numbers)

# Create alpha orbitals
exp_alpha = lf.create_expansion()
exp_beta = lf.create_expansion()

# Initial guess
guess_core_hamiltonian(olp, kin, na, exp_alpha, exp_beta)

# Construct the restricted HF effective Hamiltonian
external = {'nn': compute_nucnuc(mol.coordinates, mol.pseudo_numbers)}
terms = [
    UTwoIndexTerm(kin, 'kin'),
    UDirectTerm(er, 'hartree'),
    UGridGroup(obasis, grid, [
        ULibXCLDA('x'),
        ULibXCLDA('c_vwn'),
    ]),
    UTwoIndexTerm(na, 'ne'),
]
ham = UEffHam(terms, external)

# Decide how to occupy the orbitals (5 alpha electrons, 4 beta electrons)
occ_model = AufbauOccModel(5, 4)

# Converge WFN with Optimal damping algorithm (ODA) SCF
# - Construct the initial density matrix (needed for ODA).
occ_model.assign(exp_alpha, exp_beta)
dm_alpha = exp_alpha.to_dm()
dm_beta = exp_beta.to_dm()
# - SCF solver
scf_solver = ODASCFSolver(1e-6)
scf_solver(ham, lf, olp, occ_model, dm_alpha, dm_beta)

# Derive orbitals (coeffs, energies and occupations) from the Fock and density
# matrices. The energy is also computed to store it in the output file below.
fock_alpha = lf.create_two_index()
fock_beta = lf.create_two_index()
ham.reset(dm_alpha, dm_beta)
ham.compute_energy()
ham.compute_fock(fock_alpha, fock_beta)
exp_alpha.from_fock_and_dm(fock_alpha, dm_alpha, olp)
exp_beta.from_fock_and_dm(fock_beta, dm_beta, olp)

# Assign results to the molecule object and write it to a file, e.g. for
# later analysis. Note that the ODA algorithm can only really construct an
# optimized density matrix and no orbitals.
mol.title = 'UKS computation on methyl'
mol.energy = ham.cache['energy']
mol.obasis = obasis
mol.exp_alpha = exp_alpha
mol.exp_beta = exp_beta
mol.dm_alpha = dm_alpha
mol.dm_beta = dm_beta

# useful for visualization:
mol.to_file('methyl.molden')
# useful for post-processing (results stored in double precision):
mol.to_file('methyl.h5')

# CODE BELOW IS FOR horton-regression-test.py ONLY. IT IS NOT PART OF THE EXAMPLE.
rt_results = {
    'energy': ham.cache['energy'],
    'exp_alpha': exp_alpha.energies,
    'exp_beta': exp_beta.energies,
    'nn': ham.cache["energy_nn"],
    'kin': ham.cache["energy_kin"],
    'ne': ham.cache["energy_ne"],
    'grid': ham.cache["energy_grid_group"],
    'hartree': ham.cache["energy_hartree"],
}
# BEGIN AUTOGENERATED CODE. DO NOT CHANGE MANUALLY.
import numpy as np  # pylint: disable=wrong-import-position
rt_previous = {
    'nn': 9.0797849426636361,
    'energy': -39.413025846094278,
    'ne': -109.7979633321572,
    'grid': -6.002800973876951,
    'exp_alpha': np.array([
        -9.7986717922940638, -0.59038619578699925, -0.35715161266281265,
        -0.35713348345481349, -0.17897253692346748, 0.064422601329650386,
        0.12860582095430861, 0.12861343153310045, 0.48643133185477, 0.51815860365885591,
        0.51816446230008006, 0.64798888536406629, 0.81867946255020918, 0.8186998889668996,
        0.87717994515860886, 1.5932848272231379, 1.5933055160629088, 1.8896540822304329,
        2.0356210447605054, 2.0356887764338354
    ]),
    'hartree': 28.075938726368882,
    'exp_beta': np.array([
        -9.7834499694035912, -0.55781805110515448, -0.3426968308625043,
        -0.34267821755588118, -0.10289964154575663, 0.079722914609173509,
        0.13852507520336682, 0.13853244356450239, 0.53435519917642083,
        0.53436088607770116, 0.54849233019821353, 0.66761915300525365,
        0.82656187947383009, 0.82658381529781322, 0.90749566753300315, 1.6581060770404645,
        1.6581271407011235, 1.9652558550976635, 2.0561276471176364, 2.0561962562802054
    ]),
    'kin': 39.23201479090735,
}
