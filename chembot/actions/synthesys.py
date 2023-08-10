#from chembot.controls import chembot
from chembot.robot import chembot
from loguru import logger
from chembot.custom_types import State
from chembot.units import *
from copy import deepcopy, copy
from chembot.custom_types import Slots


class Synthesis:

    def __init__(self, reaction, reactor_id, temperature, time):
        self.reaction = reaction
        self.reactor_id = reactor_id
        self.temperature = temperature
        self.time = time

    def test(self, verbose=False):
        test_tube_storage = copy(chembot.storages.tube_storage)
        test_pipet_storage = copy(chembot.storages.pipet_holder)
        required_number_of_tubes = 0
        available_number_of_tubes = 0
        required_number_of_pipettes = 0
        available_number_of_pipettes = 0
        results = ''

        for reactant in self.reaction.reactants:
            tube_id = test_tube_storage.search_molecule(reactant)
            solvent = self.reaction.solvent
            solv_id = test_tube_storage.search_molecule(solvent)

            if tube_id == []:
                raise ValueError(f'{reactant} missing')

            for molecule_id in tube_id:
                molecule = test_tube_storage.slots[molecule_id]
                if (molecule.pure_mass * 1000) < (reactant.mols * molecule.molecular_mass):
                    if molecule_id == tube_id[-1]:
                        raise ValueError(f'Not enough {reactant} in storage')
                    continue

                target_solution_vol, target_substance_vol, target_solvent_vol, target_concentration = \
                    molecule.prepare_solution(reactant.mols)

                if target_solvent_vol > 0:
                    if solv_id == []:
                        raise ValueError('solvent missing')

                    for solvent_id in solv_id:
                        solvent = test_tube_storage.slots[solvent_id]
                        if target_solvent_vol > solvent.volume:
                            if solvent_id == solv_id[-1]:
                                raise ValueError(f'Not enough {solvent} in storage')
                            continue
                    if molecule.state == State.LIQUID:
                        required_number_of_tubes += 1
                        required_number_of_pipettes += 1
                    required_number_of_pipettes += 1
                results += f'reactant {reactant}:  \n' \
                           f'target_solution_vol = {target_solution_vol} \n' \
                           f'target_substance_vol = {target_substance_vol} \n' \
                           f'target_solvent_vol = {target_solvent_vol} \n'
                break

        for tubes_id, state in test_tube_storage.slots.items():
            if state == Slots.AVAILABLE:
                available_number_of_tubes += 1

        if available_number_of_tubes < required_number_of_tubes:
            raise ValueError('Not enough tubes')

        if self.reaction.reagents != ():
            for reagent in self.reaction.reagents:
                tube_id = chembot.storages.tube_storage.search_molecule(reagent)
                if tube_id == []:
                    raise ValueError(f'{reagent} missing')
                required_number_of_pipettes += 1

        for pipet_id, item in test_pipet_storage.slots.items():
            if item != Slots.EMPTY:
                available_number_of_pipettes += 1

        if available_number_of_pipettes < required_number_of_pipettes:
            raise ValueError('Not enough pipettes')
        results += f'required number of tubes = {required_number_of_tubes}\n' \
                   f'required number of pipettes = {required_number_of_pipettes}'
        if verbose:
            return results
        else:
            return True

    def substance_solution(self,
                           molecule_id: int,
                           solvent_id: int,
                           target_substance_vol: float,
                           target_solvent_vol: float,
                           target_concentration: float):
        molecule = chembot.storages.tube_storage.slots[molecule_id]
        solvent = chembot.storages.tube_storage.slots[solvent_id]
        state = molecule.state

        if state == State.LIQUID:
            _, pipet = chembot.storages.pipet_holder.next_pipet()
            chembot.storages.tube_storage.left_pipet_get(molecule_id,
                                                         (target_substance_vol * 1000),
                                                         pipet=pipet)

            molecule_id = chembot.storages.tube_storage.next_avilable_slot
            chembot.storages.tube_storage.left_pipet_put_till_end(molecule_id,
                                                                  (target_substance_vol * 1000),
                                                                  pipet=pipet)
            molecule.volume -= target_substance_vol

            logger.info('liquid mixture is ready')

        _, pipet = chembot.storages.pipet_holder.next_pipet()
        chembot.storages.tube_storage.left_pipet_get(solvent_id,
                                                     (target_solvent_vol * 1000),
                                                     pipet=pipet)

        chembot.storages.tube_storage.left_pipet_put_and_mix(molecule_id,
                                                             (target_solvent_vol * 1000),
                                                             pipet=pipet)

        solvent.volume -= target_solvent_vol
        # logger.info(molecule_id)

        new = molecule.copy()
        new.volume = Volume(target_solvent_vol + target_substance_vol)
        new.concentration = target_concentration
        new.state = State.LIQUID
        new.mols = new.concentration * new.volume
        new.solvent = solvent
        chembot.storages.tube_storage.slots[molecule_id] = new
        # chembot.storages.tube_storage.fill_slot(molecule_id, new)

        return molecule_id, pipet, new

    def do_synthesys(self):
        if not chembot.storages.reactor.anchor_status:
            chembot.storages.reactor.anchor_correct()
        for reactant in self.reaction.reactants:
            tube_id = chembot.storages.tube_storage.search_molecule(reactant)
            solvent = reactant.solvent
            solv_id = chembot.storages.tube_storage.search_molecule(solvent)
            if tube_id == []:
                raise ValueError(f'{reactant} missing')

            for molecule_id in tube_id:
                molecule = chembot.storages.tube_storage.slots[molecule_id]
                if (molecule.pure_mass * 1000) < (reactant.mols * molecule.molecular_mass):
                    if molecule_id == tube_id[-1]:
                        raise ValueError(f'Not enough {reactant} in storage')
                    continue

                target_solution_vol, target_substance_vol, target_solvent_vol, target_concentration = \
                    molecule.prepare_solution(reactant.mols)
                # logger.info(target_solution_vol, target_substance_vol, target_solvent_vol)

                if target_solvent_vol > 0:
                    if solv_id == []:
                        raise ValueError('solvent missing')

                    for solvent_id in solv_id:
                        solvent = chembot.storages.tube_storage.slots[solvent_id]
                        if target_solvent_vol > solvent.volume:
                            if solvent_id == solv_id[-1]:
                                raise ValueError(f'Not enough {solvent} in storage')
                            continue

                        molecule_id, pipet, new = self.substance_solution(molecule_id,
                                                                          solvent_id,
                                                                          target_substance_vol,
                                                                          target_solvent_vol,
                                                                          target_concentration)

                # _, pipet = chembot.storages.pipet_holder.next_pipet()
                chembot.storages.tube_storage.left_pipet_get(molecule_id,
                                                             (target_solution_vol * 1000),
                                                             pipet=pipet)

                if not chembot.storages.reactor.anchor_status:
                    chembot.storages.reactor.anchor_correct()
                chembot.storages.reactor.left_pipet_put_and_mix(self.reactor_id,
                                                                (target_solution_vol * 1000),
                                                                pipet=pipet)
                # chembot.storages.reactor.left_pipet_put_till_end(reactor_id,
                #                                                 (target_solution_vol * 1000),
                #                                                 pipet=pipet)

                logger.info(f'{reactant} is ready')
                break

        if self.reaction.reagents != ():
            for reagent in self.reaction.reagents:
                tube_id = chembot.storages.tube_storage.search_molecule(reagent)
                if tube_id == []:
                    raise ValueError(f'{reagent} missing')
                for molecule_id in tube_id:
                    molecule = chembot.storages.tube_storage.slots[molecule_id]
                    _, pipet = chembot.storages.pipet_holder.next_pipet()
                    chembot.storages.tube_storage.left_pipet_get(molecule_id,
                                                                 0.1,
                                                                 pipet=pipet)
                    molecule.volume -= 0.1

                    if not chembot.storages.reactor.anchor_status:
                        chembot.storages.reactor.anchor_correct()
                    chembot.storages.reactor.left_pipet_put_and_mix(self.reactor_id,
                                                                    0.1,
                                                                    pipet=pipet)
                    logger.info(f'{reagent} is ready')
                    break

        logger.info(f'reaction {self.reaction} is ready to start')
        # reaction.meta.update({"temperature": 40, "time": 50})
        return None
