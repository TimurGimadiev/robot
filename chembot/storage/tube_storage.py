from .basic_storage import BaseStorage
from ..data_structure import Coordinates
import numpy as np
import json
from time import sleep
from .pipet_types import BluePipet
from typing import Optional, List
from ..chemistry import smiles, Molecule
from loguru import logger
from ..custom_types import Slots, State



class TubeStorage(BaseStorage):

    def __init__(self, chembot, z_len=12, x_len=8, anchor=Coordinates(x=170, z=2770), x_step=256,
                 z_step=256, **kwargs):

        super().__init__(chembot=chembot, z_len=z_len, x_len=x_len, anchor=anchor, x_step=x_step,
                         z_step=z_step, **kwargs)
        self.tube_in_operation = None
        self.__pipet = None
        self.before_cap = 10000
        self.lowest = 13300
        self.before_put_tube = 11000
        self.left_pipet_get_hight = 36700   # 38000  # 36000 отбор проб из вортекса
        self.left_pipet_put_hight = 26500
        self.left_pipet_before_tube = 22000

    @property
    def pipet(self):
        return self.__pipet

    @pipet.setter
    def pipet(self, pipet):
        if isinstance(pipet, BluePipet):
            self.__pipet = pipet

    def get_tube(self, idx: int):
        # if not self.tube_available_moves(idx):
        #     raise ValueError(f"No moves available for {idx}")
        self.chembot.motors.cap_remover.pins_up()
        self.chembot.set_coordinates(self.num2position(idx))
        self.chembot.steppers.op.set_position(self.before_cap)
        self.chembot.motors.cap_rotator.close(time=2000)
        self.chembot.steppers.op.set_position(self.lowest)
        self.chembot.steppers.op.set_position(0)
        self.flush_slot(idx)
        # self.check_tube_path()
        # chembot.lock_coordinates()

    def put_tube(self, idx: int):
        # if idx not in self.tube_available_moves_by_id(self.tube_in_operation):
        #     raise ValueError(f"This moves is not available")
        self.chembot.set_coordinates(self.num2position(idx))
        self.chembot.motors.cap_rotator.close(time=8000)
        self.chembot.steppers.op.set_position(1000)
        sleep(2)
        self.chembot.steppers.op.set_position(self.before_put_tube)
        self.chembot.motors.cap_rotator.close(time=500)
        self.chembot.motors.cap_remover.eject()
        self.chembot.steppers.op.set_position(8000)
        self.chembot.steppers.op.set_position(0)
        self.chembot.motors.cap_remover.pins_up()
        self.fill_slot(idx, self.tube_in_operation)
        self.tube_in_operation = None
        # chembot.unlock_coordinates()

    def to_trash(self):
        raise NotImplemented
        self.chembot.set_coordinates(Coordinates(2400, 0))
        self.chembot.set_coordinates(Coordinates(0, 0))
        self.chembot.motors.cap_remover.eject()
        self.chembot.motors.cap_remover.pins_up()

    def cap_open(self, idx):
        self.in_operation = True
        self.chembot.motors.cap_remover.pins_up()
        self.chembot.set_coordinates(self.num2position(idx))
        self.chembot.steppers.op.set_position(self.before_cap, speed=8000)
        self.chembot.motors.cap_rotator.close(time=2000)
        self.chembot.steppers.op.set_position(self.lowest)
        self.chembot.motors.cap_rotator.open(time=4000)
        self.chembot.steppers.op.set_position(0, speed=2500)

    def cap_close(self, idx):
        self.in_operation = True
        self.chembot.set_coordinates(self.num2position(idx))
        # self.chembot.devices.motors.cap_rotator.close(time=8000)
        # self.chembot.devices.steppers.op.set_position(1000)
        # sleep(2)
        self.chembot.steppers.op.set_position(self.before_put_tube, speed=8000)
        self.chembot.motors.cap_rotator.close(time=5000)
        self.chembot.steppers.op.set_position(self.lowest)  # 12000)
        sleep(0.5)
        self.chembot.motors.cap_remover.eject()
        self.chembot.steppers.op.set_position(self.before_cap)
        self.chembot.steppers.op.set_position(0, speed=8000)
        self.chembot.motors.cap_remover.pins_up()

        self.in_operation = False

    def pipet_by_id(self, id):
        coord = self.num2position(id)
        return Coordinates(x=coord.x - 415 + 256, z=coord.z - 2700)

    def left_pipet_get(self, idx, vol=0.5, pipet: BluePipet = BluePipet()):
        self.cap_open(idx)
        self.chembot.set_coordinates(self.pipet_by_id(idx))
        self.chembot.steppers.y_l.set_position(self.left_pipet_before_tube, speed=8000)
        self.chembot.steppers.y_l.set_position(self.left_pipet_get_hight, speed=2500)
        self.chembot.steppers.l_pipet.set_position(pipet.volume_to_steps(vol))
        #self.pipet = pipet
        pipet.occupied_vol = vol
        self.chembot.steppers.y_l.set_position(self.left_pipet_before_tube, speed=2500)
        self.chembot.steppers.y_l.set_position(0, speed=8000)
        self.cap_close(idx)


    def left_pipet_put(self, idx, vol=0.5, pipet: BluePipet = BluePipet()):
        if vol > pipet.occupied_vol:
            raise ValueError("Not enough volume in left pipet")
        self.cap_open(idx)
        self.chembot.set_coordinates(self.pipet_by_id(idx))
        self.chembot.steppers.y_l.set_position(self.left_pipet_before_tube, speed=8000)
        self.chembot.steppers.y_l.set_position(self.left_pipet_put_hight, speed=2500)
        vol = pipet.occupied_vol - vol
        pipet.occupied_vol = vol
        self.chembot.steppers.l_pipet.set_position(pipet.volume_to_steps(vol), speed=1000)
        self.left_pipet_vol = vol
        self.chembot.steppers.y_l.set_position(self.left_pipet_before_tube, speed=2500)
        self.chembot.steppers.y_l.set_position(0, speed=8000)
        self.cap_close(idx)

    def left_pipet_put_till_end(self, idx, vol=0.5, pipet: BluePipet = BluePipet()):
        if vol > pipet.occupied_vol:
            raise ValueError("Not enough volume in left pipet")
        self.cap_open(idx)
        self.chembot.set_coordinates(self.pipet_by_id(idx))
        self.chembot.steppers.y_l.set_position(self.left_pipet_before_tube, speed=8000)
        self.chembot.steppers.y_l.set_position(self.left_pipet_put_hight, speed=2500)
        self.chembot.steppers.l_pipet.set_position(0, speed=1500)
        pipet.occupied_vol = 0
        self.chembot.steppers.y_l.set_position(self.left_pipet_before_tube, speed=2500)
        self.chembot.steppers.y_l.set_position(0, speed=8000)
        self.cap_close(idx)

    def left_pipet_put_and_mix(self, idx, vol=0.5, pipet: BluePipet = BluePipet()):
        if vol > pipet.occupied_vol:
            raise ValueError("Not enough volume in left pipet")
        self.cap_open(idx)
        self.chembot.set_coordinates(self.pipet_by_id(idx))
        self.chembot.steppers.y_l.set_position(self.left_pipet_before_tube, speed=8000)
        self.chembot.steppers.y_l.set_position(self.left_pipet_get_hight, speed=2500)
        self.chembot.steppers.l_pipet.set_position(0, speed=1500)
        self.chembot.steppers.l_pipet.set_position(pipet.volume_to_steps(0.8), speed=1500)
        self.chembot.steppers.l_pipet.set_position(0, speed=1500)
        self.chembot.steppers.l_pipet.set_position(pipet.volume_to_steps(0.8), speed=1500)
        self.chembot.steppers.l_pipet.set_position(0, speed=1500)
        pipet.occupied_vol = 0
        self.chembot.steppers.y_l.set_position(self.left_pipet_before_tube, speed=2500)
        self.chembot.steppers.y_l.set_position(0, speed=8000)
        self.cap_close(idx)

    def slot_from_mol_data(self, idx, data):
        # data = {"smiles": "CC(C)=O", "volume": 0.001, "moles": None, "state": "liquid", "density":
        #     0.784,
        #  "concentration": None,
        #  "solvent": {"smiles": None}}
        if isinstance(data, str):
            if data.upper() in [x.name for x in Slots]:
                self.fill_slot(idx, Slots[data.upper()])
                return
            else:
                raise ("not acceptable keyword")
        logger.info(f"mol = {data['smiles']}")
        mol = smiles(data["smiles"], substance=True)
        mol.canonicalize()
        mol.state = data["state"]
        if density := data.get("density"):
            logger.info(f"density = {density}")
            mol.density = density
            #logger.info(f"volume = {mol.density}")
        if pure_mass := data.get("mass"):
            mol.pure_mass = pure_mass
        if volume := data.get("volume"):
            if mol.state is State.LIQUID and not mol.concentration:
                if volume and mol.density:
                    mol.mols = volume * mol.density / mol.molecular_mass * 1000
                elif pure_mass and mol.density:
                    mol.mols = mol.pure_mass / mol.molecular_mass * 1000
            elif mol.state is State.LIQUID and mol.concentration and volume:
                mol.mols = volume * mol.concentration
            elif mol.state is State.LIQUID and mol.pure_mass:
                mol.mols = mol.pure_mass / mol.molecular_mass * 1000
            else:
                raise ValueError("mols or volume and density or pure mass should be provided")

        # if mols := data.get("moles"):
        #     mol.mols = mols
        # else:
        #     if mol.state is State.LIQUID and not mol.concentration:
        #         if mol.volume and mol.density:
        #             mol.mols = mol.volume / mol.density
        #         elif mol.pure_mass and mol.density:
        #             mol.moles = mol.pure_mass / mol.molecular_mass / 1000
        #     elif mol.state is State.LIQUID and mol.concentration and mol.volume:
        #         mol.mols = mol.volume * mol.concentration
        #     elif mol.state is State.LIQUID and mol.pure_mass:
        #         mol.mols = mol.pure_mass / mol.molecular_mass / 1000
        #     else:
        #         raise ValueError("mols or volume and density or pure mass sjould be provided")
        self.fill_slot(idx, mol)

    def fill_from_config(self, data):
        for k, v in data.items():
            if v:
                logger.info(f"{v}")
                self.slot_from_mol_data(k, v)

    def search_molecule(self, mol):
        slots = []
        for k, v in self.slots.items():
            if isinstance(v, Molecule) and v == mol:
                slots.append(k)
        return slots

    def fill_from_json(self, path="chembot/inputs/tubes_storage.json"):
        with open(path) as tube_storage_file:
            data = json.load(tube_storage_file)
            for k, v in data[0].items():
                if v:
                    logger.info(f"{v}")
                    self.slot_from_mol_data(int(k), v)
    # def tube_available_moves(self, idx) -> Optional[List]:
    #     position = self.num2position(idx)
    #     moves = []
    #     for i in range(position.x):  # check left moves
    #         i += 1
    #         try:
    #             tmp = Coordinates(position.x - i, position.z)
    #             if self.holders[tmp.z][tmp.x]:  # if something there
    #                 break
    #             else:
    #                 print(tmp)
    #                 moves.append(tmp)
    #         except IndexError:
    #             break
    #     for i in range(len(self.holders[0]) - position.x):  # check right moves
    #         i += 1
    #         try:
    #             tmp = Coordinates(position.x + i, position.z)
    #             if self.holders[tmp.z][tmp.x]:
    #                 break
    #             else:
    #                 moves.append(tmp)
    #         except IndexError:
    #             break
    #
    #     for i in range(position.z):  # check up moves
    #         i += 1
    #         try:
    #             tmp = Coordinates(position.x, position.z - i)
    #             if self.holders[tmp.z][tmp.x]:
    #                 break
    #             else:
    #                 moves.append(tmp)
    #         except IndexError:
    #             break
    #     for i in range(len(self.holders) - position.z):  # check down moves
    #         i += 1
    #         try:
    #             tmp = Coordinates(position.x, position.z + i)
    #             if self.holders[tmp.z][tmp.x]:
    #                 break
    #             else:
    #                 moves.append(tmp)
    #         except IndexError:
    #             break
    #     return moves
    #
    # def tube_available_moves_by_id(self, idx):
    #     return [self.position2num(x) for x in self.tube_available_moves(idx)]
    #
    # def check_tube_path(self, new_coord: Coordinates):
    #     current_coord = chembot.coordinates