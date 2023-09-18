from .molecule import Molecule
from typing import Union, Optional
from chython import MoleculeContainer
from ..custom_types import State
from ..units import *
from loguru import logger



class Substance(Molecule):
    __slots__ = ('__concentration', '__solvent', '__state', '__volume', '__pure_mass')
    #solvent: Molecule
    #molecule: Optional[Molecule]

    def __init__(self):
        super().__init__()
        self.__concentration: Optional[float] = None
        self.__solvent = None
        self.__state = None
        self.__volume = None

    @property
    def state(self) -> Optional[str]:
        try:
            return self.__state
        except AttributeError:
            return None


    @state.setter
    def state(self, state: Union[str, State]):
        if isinstance(state, str) and state.upper() in [State.LIQUID.name, State.GAS.name,
                         State.SOLID.name]:
            self.__state = State[state.upper()]
        elif isinstance(state, State) and state in list(State):
            self.__state = state
        else:
            raise TypeError('Should be str or State')
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
    def volume(self) -> Optional[Volume]:
        #print(self.pure_mass, self.density)
        #logger.info(f"{self.pure_mass}, {self.density}")
        try:
            if self.density:
                return Volume(self.pure_mass / self.density)
            else:
                return self.__volume
        except AttributeError:
            return None

    @volume.setter
    def volume(self, volume):
        if self.density:
            self.__mols = Molar(volume * self.density / self.molecular_mass /1000)
        else:
            if isinstance(volume, Volume):
                self.__volume = volume
            elif  isinstance(volume, float):
                self.__volume = Volume(volume)

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

    def solution_from_solid(self, target_mols,
                            target_concentration):
        if self.pure_mass and (self.pure_mass * 1000) >= (target_mols * self.molecular_mass):
            target_solvent_vol = self.pure_mass * 1000 / (self.molecular_mass * target_concentration)
            target_substance_vol = 0
        else:
            raise ValueError("pure_mass should be provided and it should be enough to prepare "
                             "target solution")
        return (target_substance_vol,
                target_solvent_vol)

    def solution_from_pure_liquid_substance(self, target_mols,
                                            target_concentration,
                                            min_volume=0.0001):
        target_substance_vol = target_mols * self.molecular_mass / (1000 * self.density)
        if (min_volume * 0.9) < target_substance_vol < min_volume:
            target_solution_vol = target_substance_vol * 10 / 9
            target_substance_vol = 9 * min_volume
            target_solvent_vol = min_volume
            concentration = target_substance_vol * self.density * 1000 / \
                            (self.molecular_mass * (target_substance_vol + target_solvent_vol))
        elif (min_volume / 2) < target_substance_vol <= (min_volume * 0.9):
            concentration = target_concentration
            target_solvent_vol = min_volume
            target_solution_vol = min_volume
            target_substance_vol = target_solvent_vol * target_substance_vol / \
                                   (target_solution_vol - target_substance_vol)
        elif target_substance_vol <= (min_volume / 2):
            concentration = target_concentration
            target_substance_vol = min_volume
            target_solution_vol = min_volume
            target_solvent_vol = \
                ((min_volume * self.density * 1000) /
                 (self.molecular_mass * concentration)) - min_volume
        else:
            concentration = None
            target_solution_vol = target_substance_vol
            target_solvent_vol = 0
        return (target_solution_vol,
                target_substance_vol,
                target_solvent_vol,
                concentration)

    def iterative_selection(self):

        pass

    def solution_from_liquid_mixture(self, target_mols,
                                     target_concentration,
                                     min_volume=0.0001, final_solution_vol = None):

        target_solution_vol = target_mols / self.concentration
        logger.info(f"target_mols is {str(target_mols)} \n"
                    f"target_solution_vol is {target_solution_vol}")
        # if target solution volume between 90µL and 100 µL
        if (min_volume * 0.9) < target_solution_vol < min_volume:
            target_solution_vol = target_solution_vol * 10 / 9
            target_substance_vol = 9 * min_volume
            target_solvent_vol = min_volume
            concentration = target_substance_vol * self.concentration / \
                            (target_substance_vol + target_solvent_vol)
        # if target solution volume between 50µL and 90 µL
        elif (min_volume / 2) < target_solution_vol <= (min_volume * 0.9):
            #raise NotImplemented("(min_volume / 2) < target_solution_vol <= (min_volume * 0.9)")
            target_solvent_vol = min_volume
            target_substance_vol = min_volume * target_solution_vol / (min_volume - target_solution_vol)
            target_solution_vol = min_volume
            concentration = target_concentration
        # high concentration of solution or small amount needed
        # if target solution volume less than 50µL
        elif target_solution_vol <= (min_volume / 2):
            #raise NotImplemented("target_solution_vol <= (min_volume / 2)")
            target_substance_vol = min_volume
            target_solution_vol = final_solution_vol
            #                      mols of substance
            target_solvent_vol = ((target_substance_vol * self.concentration) /
            #                       new concentration    subsVol
                                  target_concentration) - min_volume

            concentration = target_concentration
        # amount of target solution volume more than 100µL
        else:
            target_substance_vol = target_solution_vol
            target_solvent_vol = 0
            concentration = None
        return (target_solution_vol,
                target_substance_vol,
                target_solvent_vol,
                concentration)

    def prepare_solution(self, target_mols,
                         min_volume=0.0001,
                         v_max=0.001,
                         tube_vol=0.0015, target_solution_vol=None):
        # define how much solution will be used in reaction
        target_solution_vol = target_solution_vol if target_solution_vol else min_volume
        # volume of substance
        target_substance_vol = None
        # volume of solvent
        target_solvent_vol = None
        # target concentration for the final solution
        target_concentration = target_mols / target_solution_vol
        new = self.copy()
        logger.info(f"started {self}")
        # pure solid compound in tube
        if self.state is State.SOLID:
            logger.info(f"it is pure solid")
            target_substance_vol, target_solvent_vol = \
                self.solution_from_solid(target_mols, target_concentration)

            new.volume = Volume(target_solvent_vol)
            new.concentration = target_concentration

        # pure liquid compound in tube
        elif (self.state is State.LIQUID) and (self.concentration is None):
            logger.info(f"it is pure liquid")
            target_solution_vol, target_substance_vol, target_solvent_vol, new.concentration = \
                self.solution_from_pure_liquid_substance(target_mols, target_concentration)
            new.volume = Volume(target_solvent_vol + target_substance_vol)

        # liquid mixture in tube
        elif (self.state is State.LIQUID) and (self.concentration is not None):
            logger.info(f"it is mixture")
            target_solution_vol, target_substance_vol, target_solvent_vol, new.concentration = \
                self.solution_from_liquid_mixture(target_mols, target_concentration,
                                                  final_solution_vol=target_solution_vol)
            new.volume = Volume(target_solvent_vol + target_substance_vol)

        if target_solution_vol > v_max:
            print(f'Too much solution, target_vol '
                  f'{ target_substance_vol + target_solvent_vol}')
            return None
        if target_solvent_vol > v_max:
            print('Too much solvent , target_solvent_vol '
                  f'{ target_solvent_vol}')
            return None

        if (target_solvent_vol + target_substance_vol) > tube_vol:
            print('Not enough tube volume')
            return None

        return (target_solution_vol,
                target_substance_vol,
                target_solvent_vol,
                new)





