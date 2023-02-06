from ..chemistry.reaction import Reaction
from ..chemistry.smiles_parse import smiles

data = {
    "stoichiometry": {"reactants": {1: 1, 2: 1}, "products": {1: 1}},
    "target": {"product": True, "idx": 1, "mols": 0.05, "mass": None}
}

a = smiles("[CH2:7]([OH:6])[CH2:8][Br:9].[O:4]=[S:3](=[O:5])([CH2:2][CH3:1])[Cl:10]>>[O:4]=[S:3](=[O:5])([CH2:2][CH3:1])[O:6][CH2:7][CH2:8][Br:9]", data=data)


from chembot.chemistry import Molecule, Reaction, Solution2C, smiles
a = smiles("[CH2:7]([OH:6])[CH2:8][Br:9]")
b = smiles("O")
b.density = 1.
a.density = 0.8
c = Solution2C(a,b, 0.5)