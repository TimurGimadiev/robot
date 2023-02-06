from molecule import OrganicMolecule, InorganincMolecule
from typing import Union


class Substance:
    #solvent: list[Union[OrganicMolecule, InorganincMolecule]]
    molecule: list[Union[OrganicMolecule, InorganincMolecule]]
    mass: float


class Solution:
    solvent: list[Union[OrganicMolecule, InorganincMolecule]]
    concentration: float
    volume: float

