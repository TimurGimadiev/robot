from chembot.chemistry import Reaction, Molecule, Solution2C, smiles
data = {
    "stoichiometry": {"reactants": {1: 1, 2: 1}, "products": {1: 1}},
    "target": {"product": False, "idx": 1, "mols": 0.0005, "mass": None},
    "states": {"reactants": {1: "liquid", 2: "liquid"}, "product": {1: None}},
    "density": {"reactants": {1: 0.784, 2: 1.43}, "product": {1: None}},
    "solvent": {"density": 1.0, "smiles": "O"}
}


a = smiles("CC(C)=O.CC(=O)C1=CC=C(C=C1)[N+]([O-])=O>>CC(=O)CC(O)C1=CC=C(C=C1)[N+]([O-])=O",
           data=data)

# v = smiles("O")
# v.density = 1.0
# a.reactants[0].solvent = v
# a.reactants[0].density = 0.784
# a.reactants[1].density = 1.433
# a.reactants[0].concentration = None
# a.reactants[0].state = "liquid"
# a.reactants[1].state = "liquid"
trgt_solution_vol, trgt_substance_vol, trgt_solvent_vol = a.reactants[0].prepare_solution()

print(trgt_solution_vol)
