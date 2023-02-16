from chython import smiles as chy_smiles, ReactionContainer,MoleculeContainer
from .reaction import Reaction
from .molecule import Molecule


def smiles(smiles_str: str, data={}):
    structure = chy_smiles(smiles_str, _m_cls=Molecule, _r_cls=Reaction)
    if isinstance(structure, Reaction):
        structure.reaction_params = data
        return structure
    elif isinstance(structure, Molecule):
        return structure
