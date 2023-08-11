from chembot.actions.synthesys import Synthesis
from chembot.controls import chembot
from chembot.storage import Storages
from chembot.robot import chembot
from chembot.chemistry import substance
from chembot import Substance
from chython import smiles
from chembot.storage import pipet_holder
from chembot.storage import tube_storage
from loguru import logger
from chembot.custom_types import State
from chembot.chemistry import Reaction, Molecule, Solution2C, smiles


def prepare_synthesys():
    data = {
        "stoichiometry": {"reactants": {"1": 1., "2": 1.5}, "products": {"1": 1.}, "reagents": {"1": 0.05}},
        "target": {"product": False, "idx": 1, "mols": 0.001, "mass": None},
        "states": {"reactants": {"1": "liquid", "2": "liquid"}, "products": {"1": None}, "reagents": {"1": "liquid"}},
        "density": {"reactants": {"1": 0.78, "2": 0.784}, "reagents": {"1": 1.}},
        "solvent": {"density": 1.0, "smiles": "O"}
    }

    reaction = smiles("CC(=O)C1=CC=C(C=C1)[N+]([O-])=O.CC(C)=O>O=C(O[Zn]OC(=O)C1CCCN1)C1CCCN1>CC(=O)CC(O)C1=CC=C("
                      "C=C1)[N+]([O-])=O",
                      data=data)
    reaction.canonicalize()

    #v = smiles("O")
    #v.density = 1.0
    #reaction.reactants[0].solvent = v
    #reaction.reactants[1].solvent = v
    synthesis = Synthesis(reaction, 1, 20, 180)
    #synthesis.test()
    #synthesis.do_synthesys()
    return synthesis


# prepare_synthesys()
