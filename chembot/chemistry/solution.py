from .molecule import Molecule
from typing import Optional


class Solution2C:

    def __init__(self, molecule: Molecule, solvent: Molecule, concentration):
        self.molecule = molecule
        self.solvent = solvent
        self.__concentration = concentration

    @property
    def concentration(self) -> Optional[float]:
        return self.__concentration

    @concentration.setter
    def concentration(self, concentration):  # molar concentration c = M/L
        # solid molecules do not processed
        self.__concentration = concentration

    def calculate_per_volume(self, volume):
        if self.concentration:
            self.molecule.mols = self.concentration * volume
            self.solvent.volume = volume - self.molecule.volume


class SolutionFromSolid:
    def __init__(self, molecule: Molecule, solvent: Molecule, concentration, volume):
        self.molecule = molecule
        self.solvent = solvent
        self.__concentration = concentration
