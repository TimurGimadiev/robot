# from chembot.controls import chembot
from chembot.robot import chembot
from loguru import logger
from chembot.custom_types import State
from chembot.units import *
from copy import deepcopy, copy
from chembot.custom_types import Slots
from json import load
from chembot.chemistry import smiles
from threading import Thread
from time import time


class Synthesis:

    def __init__(self, reaction, reactor_id, temperature, time):
        self.reaction = reaction
        self.reactor_id = reactor_id
        self.temperature = temperature
        self.time = time
        self.start_time = None
        self.logs = {}


    def __repr__(self):
        return f'{self.reaction} at {self.temperature} degree, time: {self.time}'

    def test(self, verbose=False):
        test_tube_storage = copy(chembot.storages.tube_storage)
        test_pipet_storage = copy(chembot.storages.pipet_holder)
        required_number_of_tubes = 0
        available_number_of_tubes = 0
        required_number_of_pipettes = 0
        available_number_of_pipettes = 0
        results = {}
        target_solvent_vol = None
        for num, reactant in enumerate(self.reaction.reactants):
            tube_id = test_tube_storage.search_molecule(reactant)
            solvent = self.reaction.solvent
            solv_id = test_tube_storage.search_molecule(solvent)
            if tube_id == []:
                raise ValueError(f'{reactant} missing')
            for molecule_id in tube_id:
                molecule = test_tube_storage.slots[molecule_id]
                logger.info(
                    f"mol id {str(molecule_id)}  in stock {str(molecule.mols)} needed "
                    f"{str(reactant.mols)}")
                # print("hey")
                # print(molecule.mols)
                # print(reactant.mols)
                # print(molecule.mols  > reactant.mols)
                #logger.info(f'sada {molecule.mols} > {reactant.mols}')
                if molecule.mols < reactant.mols:
                    if molecule_id == tube_id[-1]:
                        logger.info(f"Not enough in storage needed {str(reactant.mols)}")
                        raise ValueError
                    continue

                for solution_vol in range(10):
                    try:
                        target_solution_vol, target_substance_vol, target_solvent_vol, target_concentration = \
                        molecule.prepare_solution(reactant.mols, target_solution_vol=0.1 + 0.1
                                                  * solution_vol)
                    except TypeError:
                        continue
                    break
                if not target_solution_vol:
                    raise ValueError(f"target_solution_vol not calculated")

                if target_solvent_vol > 0:
                    if solv_id == []:
                        raise ValueError('solvent missing')

                    for solvent_id in solv_id:
                        solvent = test_tube_storage.slots[solvent_id]
                        logger.info(
                            f"mol id {str(solvent_id)}  in stock {str(solvent.volume)} needed "
                            f"{str(target_solvent_vol)}")
                        if target_solvent_vol > solvent.volume:
                            if solvent_id == solv_id[-1]:
                                raise ValueError(f'Not enough {solvent} in storage')
                            continue
                    if molecule.state == State.LIQUID:
                        required_number_of_tubes += 1
                        required_number_of_pipettes += 1
                    required_number_of_pipettes += 1
                results[f"reactant_{num}"] = {'reactant': reactant,
                     'target_solution_vol': Volume(target_solution_vol),
                     'target_substance_vol': Volume(target_substance_vol),
                     'target_solvent_vol': Volume(target_solvent_vol)}

                break

        for tubes_id, state in test_tube_storage.slots.items():
            if state == Slots.AVAILABLE:
                available_number_of_tubes += 1

        if available_number_of_tubes < required_number_of_tubes:
            raise ValueError('Not enough tubes')

        if self.reaction.reagents != ():
            for num, reagent in enumerate(self.reaction.reagents):
                tube_id = chembot.storages.tube_storage.search_molecule(reagent)
                if tube_id == []:
                    raise ValueError(f'{reagent} missing')
                for reagent_id in tube_id:
                    molecule = test_tube_storage.slots[reagent_id]
                    if molecule.mols < reagent.mols:
                        if reagent_id == tube_id[-1]:
                            raise ValueError(f'Not enough {reagent} in storage')
                        continue

                    reagent_solution_vol, reagent_substance_vol, reagent_solvent_vol, reagent_concentration = \
                        molecule.prepare_solution(reagent.mols)
                    logger.info(f'reagent_solution_vol: {reagent_solution_vol}\n'
                                f'reagent_substance_vol: {reagent_substance_vol}\n'
                                f'reagent_solvent_vol: {reagent_solvent_vol}\n'
                                f'reagent_concentration: {reagent_concentration}')
                    results[f"reagent_{num}"] = {'reagent_solution_vol': Volume(
                        reagent_solution_vol),
                         'reagent_substance_vol': Volume(reagent_substance_vol),
                         'reagent_solvent_vol': Volume(reagent_solvent_vol),
                         'reagent_concentration': MolarConcentration(reagent_concentration)}
                    break
                required_number_of_pipettes += 1

        for pipet_id, item in test_pipet_storage.slots.items():
            if item != Slots.EMPTY:
                available_number_of_pipettes += 1

        if available_number_of_pipettes < required_number_of_pipettes:
            raise ValueError('Not enough pipettes')
        results.update({'required number of tubes': required_number_of_tubes,
                        'required number of pipettes': required_number_of_pipettes})
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

    def molecule_search_and_calc(self, molecule, chembot_local=chembot):
        tube_id = chembot_local.storages.tube_storage.search_molecule(molecule)
        solvent = self.reaction.solvent
        solv_id = chembot_local.storages.tube_storage.search_molecule(solvent)
        if tube_id == []:
            raise ValueError(f'{molecule} missing')
        pipet = None
        for molecule_id in tube_id:
            # searching molecule in storage
            molecule = chembot_local.storages.tube_storage.slots[molecule_id]
            if (molecule.pure_mass * 1000) < (molecule.mols * molecule.molecular_mass):
                if molecule_id == tube_id[-1]:
                    raise ValueError(f'Not enough {molecule} in storage')
                continue

            target_solution_vol, target_substance_vol, target_solvent_vol, target_concentration = \
                molecule.prepare_solution(molecule.mols)
            # logger.info(target_solution_vol, target_substance_vol, target_solvent_vol)

            if target_solvent_vol > 0:
                if solv_id == []:
                    raise ValueError('solvent missing')

                for solvent_id in solv_id:
                    solvent = chembot_local.storages.tube_storage.slots[solvent_id]
                    if target_solvent_vol > solvent.volume:
                        if solvent_id == solv_id[-1]:
                            raise ValueError(f'Not enough {solvent} in storage')
                        continue

            return target_solution_vol, target_substance_vol, target_solvent_vol, \
                   target_concentration, solvent_id


    def prepare_molecule_for_reaction(self, molecule):
        tube_id = chembot.storages.tube_storage.search_molecule(molecule)
        solvent = self.reaction.solvent
        solv_id = chembot.storages.tube_storage.search_molecule(solvent)
        if tube_id == []:
            raise ValueError(f'{molecule} missing')
        pipet = None
        for molecule_id in tube_id:
            # searching molecule in storage
            molecule = chembot.storages.tube_storage.slots[molecule_id]
            if (molecule.pure_mass * 1000) < (molecule.mols * molecule.molecular_mass):
                if molecule_id == tube_id[-1]:
                    raise ValueError(f'Not enough {molecule} in storage')
                continue

            target_solution_vol, target_substance_vol, target_solvent_vol, target_concentration = \
                molecule.prepare_solution(molecule.mols)
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
            # actual actions
            if not pipet:
                _, pipet = chembot.storages.pipet_holder.next_pipet()
            chembot.storages.tube_storage.left_pipet_get(molecule_id,
                                                         (target_solution_vol * 1000),
                                                         pipet=pipet)
            chembot.stop_mix()
            if not chembot.storages.reactor.anchor_status:
                chembot.storages.reactor.anchor_correct()
            chembot.storages.reactor.left_pipet_put_and_mix(self.reactor_id,
                                                            (target_solution_vol * 1000),
                                                            pipet=pipet)
            # chembot.storages.reactor.left_pipet_put_till_end(reactor_id,
            #                                                 (target_solution_vol * 1000),
            #                                                 pipet=pipet)

            logger.info(f'reactant is ready {molecule}')
            break

    def do_synthesys(self):
        self.logs.update(self.test(verbose=True))
        # prepare reactants
        for reactant in self.reaction.reactants:
            self.prepare_molecule_for_reaction(reactant)
            # tube_id = chembot.storages.tube_storage.search_molecule(reactant)
            # solvent = self.reaction.solvent
            # solv_id = chembot.storages.tube_storage.search_molecule(solvent)
            # if tube_id == []:
            #     raise ValueError(f'{reactant} missing')
            # pipet = None
            # for molecule_id in tube_id:
            #     molecule = chembot.storages.tube_storage.slots[molecule_id]
            #     if (molecule.pure_mass * 1000) < (reactant.mols * molecule.molecular_mass):
            #         if molecule_id == tube_id[-1]:
            #             raise ValueError(f'Not enough {reactant} in storage')
            #         continue
            #
            #     target_solution_vol, target_substance_vol, target_solvent_vol, target_concentration = \
            #         molecule.prepare_solution(reactant.mols)
            #     # logger.info(target_solution_vol, target_substance_vol, target_solvent_vol)
            #
            #     if target_solvent_vol > 0:
            #         if solv_id == []:
            #             raise ValueError('solvent missing')
            #
            #         for solvent_id in solv_id:
            #             solvent = chembot.storages.tube_storage.slots[solvent_id]
            #             if target_solvent_vol > solvent.volume:
            #                 if solvent_id == solv_id[-1]:
            #                     raise ValueError(f'Not enough {solvent} in storage')
            #                 continue
            #
            #             molecule_id, pipet, new = self.substance_solution(molecule_id,
            #                                                               solvent_id,
            #                                                               target_substance_vol,
            #                                                               target_solvent_vol,
            #                                                               target_concentration)
            #     if not pipet:
            #          _, pipet = chembot.storages.pipet_holder.next_pipet()
            #     chembot.storages.tube_storage.left_pipet_get(molecule_id,
            #                                                  (target_solution_vol * 1000),
            #                                                  pipet=pipet)
            #     chembot.stop_mix()
            #     if not chembot.storages.reactor.anchor_status:
            #         chembot.storages.reactor.anchor_correct()
            #     chembot.storages.reactor.left_pipet_put_and_mix(self.reactor_id,
            #                                                     (target_solution_vol * 1000),
            #                                                     pipet=pipet)
            #     # chembot.storages.reactor.left_pipet_put_till_end(reactor_id,
            #     #                                                 (target_solution_vol * 1000),
            #     #                                                 pipet=pipet)
            #
            #     logger.info(f'reactant is ready {reactant}')
            #     break
        # prepare reagents
        if self.reaction.reagents != ():
            for reagent in self.reaction.reagents:
                self.prepare_molecule_for_reaction(reagent)
                # tube_id = chembot.storages.tube_storage.search_molecule(reagent)
                # if tube_id == []:
                #     raise ValueError(f'{reagent} missing')
                # for molecule_id in tube_id:
                #     molecule = chembot.storages.tube_storage.slots[molecule_id]
                #     _, pipet = chembot.storages.pipet_holder.next_pipet()
                #     molecule.
                #     chembot.storages.tube_storage.left_pipet_get(molecule_id,
                #                                                  0.1,
                #                                                  pipet=pipet)
                #     molecule.volume -= 0.1
                #     chembot.stop_mix()
                #     if not chembot.storages.reactor.anchor_status:
                #         chembot.storages.reactor.anchor_correct()
                #     chembot.storages.reactor.left_pipet_put_and_mix(self.reactor_id,
                #                                                     0.1,
                #                                                     pipet=pipet)
                #     logger.info(f'ragent is ready {reagent}' )
                #     break
        logger.info(f'reaction is started at {self.start_time} {self.reaction} ')
        # reaction.meta.update({"temperature": 40, "time": 50})
        # fix start time
        self.start_time = time()
        # start mixing
        chembot.mix()
        return None


#def prepeare_synthesis():


def synthesys_queue_from_json(path="chembot/inputs/reactions.json", canonicalize=True):
    synthesys_queue = []
    with open(path) as reactions_config_file:
        data = load(reactions_config_file)
        #reactor_id = chembot.storages.reactor.next_avilable_slot
        #if not reactor_id:
        #    raise ValueError("not enough tubes for reactions")
        for reaction, reactor_id in zip(data, chembot.storages.reactor.avilable_slots):
            logger.info(f"started to process {reaction['reaction']}")
            temperature = reaction["temperature"] if reaction.get("temperature") else 20
            time = reaction["time"] if reaction.get("time") else 600
            temp_reaction = smiles(reaction["reaction"], data=reaction)
            if canonicalize:
                temp_reaction.canonicalize()
            synthesys = Synthesis(reaction=temp_reaction,
                                  reactor_id=reactor_id, temperature=temperature, time=time)
            synthesys_queue.append(synthesys)
        if len(data) != len(synthesys_queue):
            logger.info(f"Not all the reactions were enqueued because of available space in "
                        f"reactor; \n"
                        f"{len(data)} reactions in config file and "
                        f"{len(synthesys_queue)} reactioins in resulted queue")

    return synthesys_queue






