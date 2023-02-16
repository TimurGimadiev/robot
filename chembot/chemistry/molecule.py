from chython import MoleculeContainer
from typing import Optional


class Molecule(MoleculeContainer):
    __slots__ = ("__mols", "__density", "__target_mol", "__concentration")

    def __init__(self):
        super().__init__()
        self.__mols = None
        self.__target_mol = None
        self.__density = None
        self.__concentration = None
        self.__solvent = None

    @property
    def solvent(self):
        return self.__solvent

    @solvent.setter
    def solvent(self, sol: "Molecule"):
        if not isinstance(sol, Molecule):
            raise TypeError('Should be Molecule')
        self.__solvent = sol

    @property
    def mols(self) -> Optional[float]:
        return self.__mols

    @mols.setter
    def mols(self, mols):
        if not isinstance(mols, float):
            raise TypeError('Amount of Mols should be float')
        self.__mols = mols

    @property
    def pure_mass(self):
        return self.mols * self.molecular_mass / 1000

    @property
    def density(self):
        return self.__density

    @density.setter
    def density(self, density):
        if not isinstance(density, float):
            raise TypeError('value should be float')
        self.__density = density

    @property
    def volume(self):
        if self.__density:
            return self.pure_mass / self.density

    @volume.setter
    def volume(self, volume):
        #if self.density:
            self.__mols = volume * 1000 * self.density / self.molecular_mass
        #else:
        #    self.__density = self.pure_mass / volume


    @property
    def target_mol(self) -> Optional[float]:
        return self.__target_mol  # {"is_target":False, "target_mols":0.01}

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
        return self.__concentration

    @concentration.setter
    def concentration(self, concentration):  # molar concentration c = M/L
        # solid molecules do not processed
        self.__concentration = concentration

    def calculate_per_volume(self, volume):
        if self.concentration:
            self.mols = self.concentration * volume
            self.solvent.volume = volume - self.volume
        elif self.mols:
            self.solvent.volume = volume - self.volume
            self.concentration = self.mols / volume





