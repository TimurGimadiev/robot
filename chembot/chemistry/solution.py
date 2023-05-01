from .molecule import Molecule
from typing import Optional
from ..units import *
from ..custom_types import *
from copy import copy


class Solution2C:

    def __init__(self, molecule: Molecule, solvent: Molecule, target_concentration=None,
                 total_volume=None):
        self.molecule = molecule
        self.solvent = solvent
        self.__initial_mols_of_target = copy(molecule.mols)
        self.__molecule_volume = None
        self.__solvent_volume = None
        self.__target_concentration = target_concentration
        self.__total_volume = total_volume



    @property
    def mol_volume(self):
        try:
            return self.__molecule_volume
        except AttributeError:
            return None

    @property
    def sol_volume(self):
        try:
            return self.__solvent_volume
        except AttributeError:
            return None

    @property
    def get_volume(self):
        if self.target_concentration and self.molecule.mols:
            volume = self.molecule.mols*self.target_concentration
            return volume

    @property
    def target_concentration(self) -> Optional[MolarConcentration]:
        return self.__target_concentration

    @target_concentration.setter
    def target_concentration(self, target_concentration):  # molar concentration c = M/L
        # solid molecules do not processed
        self.__target_concentration = target_concentration

    @property
    def total_volume(self) -> Optional[MolarConcentration]:
        return self.__total_volume

    @total_volume.setter
    def total_volume(self, concentration):  # molar concentration c = M/L
        # solid molecules do not processed
        self.__total_volume = concentration

    def prepare_solution(self, target_solvent_vol=0.00015, min_volume=0.0001,
                         v_max=0.001, tube_vol=0.0015):
        #target_mols = self.mols
        target_concentration = self.mols / (v_max * min_volume) /1000
        concentration = self.concentration
        target_solution_vol = None
        target_substance_vol = None

        if self.state is State.SOLID:
            if self.pure_mass >= (self.mols * self.molecular_mass):
                concentration = target_concentration
                target_solvent_vol = self.pure_mass / (self.molecular_mass * concentration)
                target_solution_vol = 0.000100
                target_substance_vol = 0
            else:
                target_solution_vol = 0
                target_substance_vol = 0
                target_solvent_vol = 0
                print('Not enough substance')

        elif (self.state is State.LIQUID) and (concentration is None):
            target_substance_vol = self.mols * self.molecular_mass / 1000 / self.density
            logger.info(f"target_substance_vol {Volume(target_substance_vol).show_mkl}")

            if (min_volume * 0.9) < target_substance_vol < min_volume:
                target_solution_vol = target_substance_vol * 10 / 9
                target_substance_vol = 9 * min_volume
                target_solvent_vol = min_volume
            elif (min_volume / 2) < target_substance_vol <= (min_volume * 0.9):
                target_solvent_vol = min_volume
                target_substance_vol = min_volume * target_substance_vol / (
                            min_volume - target_substance_vol)
                target_solution_vol = 0.0001
            elif target_substance_vol <= (min_volume / 2):
                concentration = target_concentration
                target_substance_vol = min_volume
                a = (min_volume * self.density * 1000)
                b = (self.molecular_mass * concentration)
                target_solvent_vol = (a / b) - min_volume
                target_solution_vol = 0.0001
            else:
                target_solution_vol = target_substance_vol
                target_solvent_vol = 0

        elif (self.state is State.LIQUID) and (concentration is not None):
            target_solution_vol = self.mols / concentration

            if (min_volume * 0.9) < target_solution_vol < min_volume:
                target_solution_vol = target_solution_vol * 10 / 9
                target_substance_vol = 9 * min_volume
                target_solvent_vol = min_volume
            elif (min_volume / 2) < target_solution_vol <= (min_volume * 0.9):
                target_solvent_vol = min_volume
                target_substance_vol = min_volume * target_solution_vol / (
                            min_volume - target_solution_vol)
                target_solution_vol = 0.0001
            elif target_solution_vol <= (min_volume / 2):
                target_substance_vol = min_volume
                target_solvent_vol = ((
                                                  min_volume * concentration) /
                                      target_concentration) - min_volume
                self.concentration = target_concentration
                target_solution_vol = 0.0001
            else:
                target_substance_vol = target_solution_vol
                target_solvent_vol = 0

        if target_solution_vol > v_max:
            print('Too much solution')

        if target_solvent_vol > v_max:
            print('Too much solvent')

        if (target_solvent_vol + target_substance_vol) > tube_vol:
            print('Not enough tube volume')

        return Volume(target_solution_vol), Volume(target_substance_vol), Volume(target_solvent_vol)


class SolutionFromSolid:
    def __init__(self, molecule: Molecule, solvent: Molecule, concentration, volume):
        self.molecule = molecule
        self.solvent = solvent
        self.__concentration = concentration


