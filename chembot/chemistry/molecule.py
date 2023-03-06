from chython import MoleculeContainer
from typing import Optional, Union
from ..units import *


class Molecule(MoleculeContainer):
    __slots__ = ('__mols', '__density', '__target_mol', '__concentration', '__solvent')

    def __init__(self):
        super().__init__()
        self.__mols = None
        self.__target_mol = None
        self.__density = None
        self.__concentration: Optional[float] = None
        self.__solvent = None

    @property
    def solvent(self) -> Optional['Molecule']:
        try:
            return self.__solvent
        except AttributeError:
            return None


    @solvent.setter
    def solvent(self, sol: Union['Molecule', None]):
        if not isinstance(sol, Molecule) and not sol:
            raise TypeError('Should be Molecule')
        self.__solvent = sol

    @property
    def mols(self) -> Optional[Molar]:
        try:
            return self.__mols
        except AttributeError:
            return None

    @mols.setter
    def mols(self, mols):
        if not isinstance(mols, float) and not isinstance(mols, Molar):
            raise TypeError('Amount of Mols should be Molar or float')
        elif isinstance(mols, float):
            self.__mols = Molar(mols)
        else:
            self.__mols = mols

    @property
    def pure_mass(self) -> Optional[Mass]:
        if self.mols and self.molecular_mass:
            return Mass(self.mols * self.molecular_mass / 1000)


    @property
    def density(self) -> Optional[Density]:
        try:
            return self.__density
        except AttributeError:
            return None

    @density.setter
    def density(self, density):
        if not isinstance(density, float) and not isinstance(density, Density):
            raise TypeError('value should be float or Density')
        elif isinstance(density, float):
            self.__density = Density(density)
        else:
            self.__density = density

    @property
    def volume(self) -> Optional[Volume]:
        try:
            if self.__density:
                return Volume(self.pure_mass / self.density)
        except AttributeError:
            return None

    @volume.setter
    def volume(self, volume):
        #if self.density:
            self.__mols = Molar(volume * 1000 * self.density / self.molecular_mass)
        #else:
        #    self.__density = self.pure_mass / volume


    @property
    def target_mol(self) -> Optional[float]:
        try:
            return self.__target_mol  # {"is_target":False, "target_mols":0.01}
        except AttributeError:
            return None

    @target_mol.setter
    def target_mol(self, target_mol):
        if not isinstance(target_mol, bool):
            raise TypeError('value should be boolean')
            # if target_mol.get("is_target") and not isinstance(target_mol["is_target"], bool):
            #     raise TypeError('is_target key should present in dictionary target_mol,'
            #                     'value should be boolean')
            # if target_mol.get("target_mols") and not isinstance(target_mol["target_mols"], float):
            #     raise TypeError('target_mols key should present in dictionary target_mol,'
            #                     'value should be float (amount of Mols)')
        self.__target_mol = target_mol

    @property
    def concentration(self) -> Optional[float]:
        try:
            return self.__concentration
        except AttributeError:
            return None

    @concentration.setter
    def concentration(self, concentration):  # molar concentration c = M/L
        # solid molecules do not processed
        self.__concentration = concentration

# TO-DO
# cases for different absent information

    def calculate_per_volume(self, volume):
        if self.concentration:
            self.mols = self.concentration * volume
            self.solvent.volume = volume - self.volume
        elif self.mols and self.solvent.volume and self.volume:
            self.solvent.volume = volume - self.volume
            self.concentration = self.mols / volume





