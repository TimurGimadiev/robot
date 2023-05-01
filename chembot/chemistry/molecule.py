from chython import MoleculeContainer
from typing import Optional, Union
from ..units import *
from ..custom_types import State
from loguru import logger


class Molecule(MoleculeContainer):
    __slots__ = ('__mols', '__density', '__target', '__concentration', '__solvent', '__state')

    def __init__(self):
        super().__init__()
        self.__mols = None
        self.__target = None
        self.__density = None
        #self.__concentration: Optional[float] = None
        #self.__solvent = None
        #self.__state = None
        #self.__volume = None

    # @property
    # def state(self) -> Optional[str]:
    #     try:
    #         return self.__state
    #     except AttributeError:
    #         return None
    #
    #
    # @state.setter
    # def state(self, state: Union[str, State]):
    #     if isinstance(state, str) and state.upper() in [State.LIQUID.name, State.GAS.name,
    #                      State.SOLID.name]:
    #         self.__state = State[state.upper()]
    #     elif isinstance(state, State) and state in list(State):
    #         self.__state = state
    #     else:
    #         raise TypeError('Should be str or State')
    # @property
    # def solvent(self) -> Optional['Molecule']:
    #     try:
    #         return self.__solvent
    #     except AttributeError:
    #         return None
    #
    #
    # @solvent.setter
    # def solvent(self, sol: Union['Molecule', None]):
    #     if not isinstance(sol, Molecule) and not sol:
    #         raise TypeError('Should be Molecule')
    #     self.__solvent = sol

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
            return Mass(self.mols * self.molecular_mass/1000)


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

    # @property
    # def volume(self) -> Optional[Volume]:
    #     try:
    #         if self.__density:
    #             return Volume(self.pure_mass / self.density)
    #     except AttributeError:
    #         return None
    #
    # @volume.setter
    # def volume(self, volume):
    #     #if self.density:
    #         self.__mols = Molar(volume * self.density / self.molecular_mass)
    #     #else:
    #     #    self.__density = self.pure_mass / volume


    @property
    def target(self) -> Optional[float]:
        try:
            return self.__target_mol  # {"is_target":False, "target_mols":0.01}
        except AttributeError:
            return None

    @target.setter
    def target(self, target):
        if not isinstance(target, bool):
            raise TypeError('value should be boolean')
            # if target_mol.get("is_target") and not isinstance(target_mol["is_target"], bool):
            #     raise TypeError('is_target key should present in dictionary target_mol,'
            #                     'value should be boolean')
            # if target_mol.get("target_mols") and not isinstance(target_mol["target_mols"], float):
            #     raise TypeError('target_mols key should present in dictionary target_mol,'
            #                     'value should be float (amount of Mols)')
        self.__target = target

    # @property
    # def concentration(self) -> Optional[float]:
    #     try:
    #         return self.__concentration
    #     except AttributeError:
    #         return None
    #
    # @concentration.setter
    # def concentration(self, concentration):  # molar concentration c = M/L
    #     # solid molecules do not processed
    #     self.__concentration = concentration

# TO-DO
# cases for different absent information

    # def calculate_per_volume(self, volume):
    #     if self.concentration:
    #         self.mols = self.concentration * volume
    #         self.solvent.volume = volume - self.volume
    #     elif self.mols and self.solvent.volume and self.volume:
    #         self.solvent.volume = volume - self.volume
    #         self.concentration = self.mols / volume

    # def prepare_solution(self, mols, target_solvent_vol=0.00015, min_volume=0.0001,
    #                      v_max=0.001, tube_vol=0.0015):
    #     #target_mols = self.mols
    #     target_concentration = self.mols / (v_max * min_volume) /1000
    #     concentration = self.concentration
    #     target_solution_vol = None
    #     target_substance_vol = None
    #
    #     if self.state is State.SOLID:
    #         if self.pure_mass >= (self.mols * self.molecular_mass):
    #             concentration = target_concentration
    #             target_solvent_vol = self.pure_mass / (self.molecular_mass * concentration)
    #             target_solution_vol = 0.000100
    #             target_substance_vol = 0
    #         else:
    #             target_solution_vol = 0
    #             target_substance_vol = 0
    #             target_solvent_vol = 0
    #             print('Not enough substance')
    #
    #     elif (self.state is State.LIQUID) and (concentration is None):
    #         target_substance_vol = self.mols * self.molecular_mass / 1000 / self.density
    #         logger.info(f"target_substance_vol {Volume(target_substance_vol).show_mkl}")
    #
    #         if (min_volume * 0.9) < target_substance_vol < min_volume:
    #             target_solution_vol = target_substance_vol * 10 / 9
    #             target_substance_vol = 9 * min_volume
    #             target_solvent_vol = min_volume
    #         elif (min_volume / 2) < target_substance_vol <= (min_volume * 0.9):
    #             target_solvent_vol = min_volume
    #             target_substance_vol = min_volume * target_substance_vol / (
    #                         min_volume - target_substance_vol)
    #             target_solution_vol = 0.0001
    #         elif target_substance_vol <= (min_volume / 2):
    #             concentration = target_concentration
    #             target_substance_vol = min_volume
    #             a = (min_volume * self.density * 1000)
    #             b = (self.molecular_mass * concentration)
    #             target_solvent_vol = (a / b) - min_volume
    #             target_solution_vol = 0.0001
    #         else:
    #             target_solution_vol = target_substance_vol
    #             target_solvent_vol = 0
    #
    #     elif (self.state is State.LIQUID) and (concentration is not None):
    #         target_solution_vol = self.mols / concentration
    #
    #         if (min_volume * 0.9) < target_solution_vol < min_volume:
    #             target_solution_vol = target_solution_vol * 10 / 9
    #             target_substance_vol = 9 * min_volume
    #             target_solvent_vol = min_volume
    #         elif (min_volume / 2) < target_solution_vol <= (min_volume * 0.9):
    #             target_solvent_vol = min_volume
    #             target_substance_vol = min_volume * target_solution_vol / (
    #                         min_volume - target_solution_vol)
    #             target_solution_vol = 0.0001
    #         elif target_solution_vol <= (min_volume / 2):
    #             target_substance_vol = min_volume
    #             target_solvent_vol = ((
    #                                               min_volume * concentration) /
    #                                   target_concentration) - min_volume
    #             self.concentration = target_concentration
    #             target_solution_vol = 0.0001
    #         else:
    #             target_substance_vol = target_solution_vol
    #             target_solvent_vol = 0
    #
    #     if target_solution_vol > v_max:
    #         print('Too much solution')
    #
    #     if target_solvent_vol > v_max:
    #         print('Too much solvent')
    #
    #     if (target_solvent_vol + target_substance_vol) > tube_vol:
    #         print('Not enough tube volume')
    #
    #     return Volume(target_solution_vol), Volume(target_substance_vol), Volume(target_solvent_vol)


