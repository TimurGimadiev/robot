from chython import smiles as chy_smiles, ReactionContainer, MoleculeContainer
from .reaction import Reaction
from .molecule import Molecule
from .substance import Substance
from typing import Union


def smiles(smiles_str: str, substance=False, data={}) -> Union[Reaction, Molecule, Substance]:
    if not substance:
        structure = chy_smiles(smiles_str, _m_cls=Molecule, _r_cls=Reaction)
        if isinstance(structure, Reaction):
            structure.reaction_params = data
            solvent = smiles(data["solvent"]["smiles"])
            solvent.density = data["solvent"]["density"]
            structure.solvent = solvent
            return structure
        elif isinstance(structure, Molecule):
            return structure
    else:
        structure = chy_smiles(smiles_str, _m_cls=Substance, _r_cls=Reaction)
        if isinstance(structure, Reaction):
            raise ValueError("Only molecules in reaction")
        if isinstance(structure, Substance):
            return structure
