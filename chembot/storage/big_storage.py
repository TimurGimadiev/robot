from .basic_storage import BaseStorage
from ..data_structure import Coordinates
import numpy as np
from ..controls import chembot


class BigTubes(BaseStorage):
    def __init__(self):

        anchor = Coordinates(1350 ,3360)
        x_step = 420
        z_step = 420
        super().__init__(anchor, x_step, z_step)
        self.holders = np.ones((1 ,6))
        self.pipet_in_operation = None
        self.before_cap = 10000
        self.lowest = 12700
        self.left_pipet_vol = 0
        self.left_pipet_get_hight = 36000
        self.max_id = len([x for x in self.holders for x in x])

    def pipet_coordinate(self, position: Coordinates) -> Coordinates:
        return Coordinates(self.step_right(position.x).x, self.step_forward(position.z).z)

    def pipet_by_id(self, id: int) -> Coordinates:
        return self.pipet_coordinate(self.num2position(id))

    def num2position(self, n) -> tuple[int, int]:
        n -= 1 # ids starts from 1
        x, z = n // 6, n % 6
        return Coordinates(x, z)

    def position2num(self, position: Coordinates) -> int:
        return position.z + position.x + 1

    def left_pipet_get(self, id, vol=1500):
        if self.max_id + 1 < id:
            raise ValueError(f"Max id {self.max_id}")
        chembot.set_coordinates(self.pipet_by_id(id))
        chembot.devices.steppers.y_l.set_position(self.left_pipet_get_hight, speed=2500)
        chembot.devices.steppers.l_pipet.set_position(vol)
        self.left_pipet_vol = vol
        chembot.devices.steppers.y_l.set_position(0, speed=2500)

    def left_pipet_put(self ,id, vol=1500):
        if self.max_id +1 < id:
            raise ValueError(f"Max id {self.max_id}")
        if vol > self.left_pipet_vol:
            raise ValueError("Not enough volume in left pipet")
        chembot.set_coordinates(self.pipet_by_id(id))
        chembot.devices.steppers.y_l.set_position(self.left_pipet_put_hight, speed=2500)
        vol = self.left_pipet_vol - vol
        chembot.devices.steppers.l_pipet.set_position(vol, speed = 1000)
        self.left_pipet_vol = vol
        chembot.devices.steppers.y_l.set_position(0, speed=2500)