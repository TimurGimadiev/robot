from .basic_storage import BaseStorage
from ..data_structures import Coordinates
import numpy as np
from ..controls.chembot import chembot
from time import sleep
from .pipet_types import BluePipet
from typing import Optional, List


class TubeStorage(BaseStorage):

    def __init__(self, z_len=12, x_len=8, anchor=Coordinates(x=1205, z=5410), x_step=256,
                 z_step=256):

        super().__init__(z_len, x_len, anchor, x_step, z_step)
        self.tube_in_operation = None
        self.__pipet = None
        self.before_cap = 10000
        self.lowest = 13300
        self.left_pipet_get_hight = 38000  # 36000 отбор проб из вортекса
        self.left_pipet_put_hight = 26500

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
        chembot.motors.cap_remover.pins_up()
        chembot.set_coordinates(self.num2position(idx))
        chembot.steppers.op.set_position(self.before_cap)
        chembot.motors.cap_rotator.close(time=2000)
        chembot.steppers.op.set_position(self.lowest)
        chembot.steppers.op.set_position(0)
        self.flush_slot(idx)
        # self.check_tube_path()
        # chembot.lock_coordinates()

    def put_tube(self, idx: int):
        # if idx not in self.tube_available_moves_by_id(self.tube_in_operation):
        #     raise ValueError(f"This moves is not available")
        chembot.set_coordinates(self.num2position(idx))
        chembot.motors.cap_rotator.close(time=8000)
        chembot.steppers.op.set_position(1000)
        sleep(2)
        chembot.steppers.op.set_position(11000)
        chembot.motors.cap_rotator.close(time=500)
        chembot.motors.cap_remover.eject()
        chembot.steppers.op.set_position(8000)
        chembot.steppers.op.set_position(0)
        chembot.motors.cap_remover.pins_up()
        self.fill_slot(idx, self.tube_in_operation)
        self.tube_in_operation = None
        # chembot.unlock_coordinates()

    def to_trash(self):
        raise NotImplemented
        chembot.set_coordinates(Coordinates(2400, 0))
        chembot.set_coordinates(Coordinates(0, 0))
        chembot.motors.cap_remover.eject()
        chembot.motors.cap_remover.pins_up()

    def cap_open(self, idx):
        chembot.motors.cap_remover.pins_up()
        chembot.set_coordinates(self.num2position(idx))
        chembot.steppers.op.set_position(self.before_cap, speed=2500)
        chembot.motors.cap_rotator.close(time=2000)
        chembot.steppers.op.set_position(self.lowest)
        chembot.motors.cap_rotator.open(time=4000)
        chembot.steppers.op.set_position(0, speed=2500)

    def cap_close(self, idx):
        chembot.set_coordinates(self.num2position(idx))
        # chembot.devices.motors.cap_rotator.close(time=8000)
        # chembot.devices.steppers.op.set_position(1000)
        # sleep(2)
        chembot.steppers.op.set_position(11000, speed=2500)
        chembot.motors.cap_rotator.close(time=5000)
        chembot.steppers.op.set_position(self.lowest)  # 12000)
        sleep(0.5)
        chembot.motors.cap_remover.eject()
        chembot.steppers.op.set_position(10000)
        chembot.steppers.op.set_position(0, speed=2500)
        chembot.motors.cap_remover.pins_up()

    def pipet_by_id(self, id):
        coord = self.num2position(id)
        return Coordinates(x=coord.x - 415 + 256, z=coord.z - 2700)

    def left_pipet_get(self, idx, vol=0.5, pipet: BluePipet = BluePipet()):
        self.cap_open(idx)
        chembot.set_coordinates(self.pipet_by_id(idx))
        chembot.steppers.y_l.set_position(self.left_pipet_get_hight, speed=2500)
        chembot.steppers.l_pipet.set_position(pipet.volume_to_steps(vol))
        pipet.occupied_vol = vol
        chembot.steppers.y_l.set_position(0, speed=2500)
        self.cap_close(idx)

    def left_pipet_put(self, idx, vol=0.5, pipet: BluePipet = BluePipet()):
        if vol > pipet.occupied_vol:
            raise ValueError("Not enough volume in left pipet")
        self.cap_open(idx)
        chembot.set_coordinates(self.pipet_by_id(idx))
        chembot.steppers.y_l.set_position(self.left_pipet_put_hight, speed=2500)
        vol = pipet.occupied_vol - vol
        chembot.steppers.l_pipet.set_position(vol, speed=1000)
        self.left_pipet_vol = vol
        chembot.steppers.y_l.set_position(0, speed=2500)
        self.cap_close(idx)

    def left_pipet_put_and_mix(self, idx, vol=0.5, pipet: BluePipet = BluePipet()):
        if vol > pipet.occupied_vol:
            raise ValueError("Not enough volume in left pipet")
        self.cap_open(idx)
        chembot.set_coordinates(self.pipet_by_id(idx))
        chembot.steppers.y_l.set_position(self.left_pipet_get_hight, speed=2500)
        chembot.steppers.l_pipet.set_position(0, speed=1500)
        chembot.steppers.l_pipet.set_position(vol, speed=1500)
        chembot.steppers.l_pipet.set_position(0, speed=1500)
        chembot.steppers.l_pipet.set_position(vol, speed=1500)
        chembot.steppers.l_pipet.set_position(0, speed=1500)
        pipet.occupied_vol = 0
        chembot.steppers.y_l.set_position(0, speed=2500)
        self.cap_close(idx)

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