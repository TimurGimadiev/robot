from chembot.controls import chembot
from chembot.storage import Storages
from chembot.robot import chembot
from chembot.chemistry import substance
from chembot import Substance
from chython import smiles
from chembot.storage import pipet_holder
from chembot.storage import tube_storage
from loguru import logger
from chembot.custom_types import State
from chembot.units import *


def substance_solution(molecule_id: int,
                       solvent_id: int,
                       target_substance_vol: float,
                       target_solvent_vol: float,
                       new):
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

    new.state = State.LIQUID
    new.mols = new.concentration * new.volume
    new.solvent = solvent
    chembot.storages.tube_storage.slots[molecule_id] = new
    # chembot.storages.tube_storage.fill_slot(molecule_id, new)

    return molecule_id, pipet


def do_synthesys(reaction, reactor_id, temperature, time):
    if not chembot.storages.reactor.anchor_status:
        chembot.storages.reactor.anchor_correct()
    for id_x in range(len(reaction.reactants)):
        tube_id = chembot.storages.tube_storage.search_molecule(reaction.reactants[id_x])
        solvent = reaction.reactants[id_x].solvent
        solv_id = chembot.storages.tube_storage.search_molecule(solvent)
        if tube_id is None:
            raise ValueError(f'{reaction.reactants[id_x]} missing')

        for molecule_id in tube_id:
            molecule = chembot.storages.tube_storage.slots[molecule_id]
            if (molecule.pure_mass * 1000) < (reaction.reactants[id_x].mols * molecule.molecular_mass):
                if molecule_id == tube_id[-1]:
                    raise ValueError(f'Not enough {reaction.reactants[id_x]} in storage')
                continue

            target_solution_vol, target_substance_vol, target_solvent_vol, new = \
                molecule.prepare_solution(reaction.reactants[id_x].mols)
            # logger.info(target_solution_vol, target_substance_vol, target_solvent_vol)

            if target_solvent_vol > 0:
                if solv_id is None:
                    raise ValueError('solvent missing')

                for solvent_id in solv_id:
                    solvent = chembot.storages.tube_storage.slots[solvent_id]
                    if target_solvent_vol > solvent.volume:
                        if solvent_id == solv_id[-1]:
                            raise ValueError(f'Not enough {solvent} in storage')
                        continue

                    molecule_id, pipet = substance_solution(molecule_id,
                                                            solvent_id,
                                                            target_substance_vol,
                                                            target_solvent_vol,
                                                            new)

            #_, pipet = chembot.storages.pipet_holder.next_pipet()
            chembot.storages.tube_storage.left_pipet_get(molecule_id,
                                                         (target_solution_vol * 1000),
                                                         pipet=pipet)

            if not chembot.storages.reactor.anchor_status:
                chembot.storages.reactor.anchor_correct()
            # chembot.storages.reactor.left_pipet_put_and_mix(reactor_id,
            #                                                  (target_solution_vol * 1000),
            #                                                  pipet=pipet)
            chembot.storages.reactor.left_pipet_put_till_end(reactor_id,
                                                             (target_solution_vol * 1000),
                                                             pipet=pipet)

            logger.info(f'{reaction.reactants[id_x]} is ready')
            break
    logger.info(f'reaction {reaction} is ready to start')
    # reaction.meta.update({"temperature": 40, "time": 50})
    return None
