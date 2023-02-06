from chython import MoleculeContainer
from typing import Optional


class Molecule(MoleculeContainer):
    __slots__ = ("__mols", "__density", "__target_mol")

    def __init__(self):
        super().__init__()
        self.__mols = None
        self.__target_mol = None
        self.__density = None

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
        self.__mols = volume * 1000 * self.density / self.molecular_mass


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





