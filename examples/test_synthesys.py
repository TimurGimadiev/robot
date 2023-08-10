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
        "stoichiometry": {"reactants": {"1": 1, "2": 2}, "products": {"1": 1}},
        "target": {"product": False, "idx": 1, "mols": 0.0005, "mass": None},
        "states": {"reactants": {"1": "liquid", "2": "liquid"}, "product": {"1": None}},
        "density": {"reactants": {"1": 1.62, "2": 0.7851}, "product": {"1": None}},
        "solvent": {"density": 1.0, "smiles": "O"}
    }

    reaction = smiles("OC(=O)CC(O)=O.CCO>>CCOC(=O)CC(=O)OCC",
                      data=data)
    #v = smiles("O")
    #v.density = 1.0
    #reaction.reactants[0].solvent = v
    #reaction.reactants[1].solvent = v
    synthesis = Synthesis(reaction, 1, 20, 180)
    #synthesis.test()
    #synthesis.do_synthesys()
    return synthesis
#start_synthesys()