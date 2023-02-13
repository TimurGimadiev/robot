from .basic_storage import BaseStorage
from ..data_structure import Coordinates
import numpy as np


class BigTubes(BaseStorage):
    def __init__(self, chembot, z_len=12, x_len=8, anchor=Coordinates(x=1350, z=3360), x_step=420,
                 z_step=420, **kwargs):

        super().__init__(chembot=chembot, z_len=z_len, x_len=x_len, anchor=anchor, x_step=x_step,
                         z_step=z_step, **kwargs)
        self.pipet_in_operation = None
        self.__pipet = None
        self.before_cap = 10000
        self.lowest = 12700
        self.left_pipet_vol = 0
        self.left_pipet_get_hight = 36000
        self.left_pipet_put_hight = 33000

    def left_pipet_get(self, idx, vol=1500):
        # if self.max_id + 1 < id:
        #     raise ValueError(f"Max id {self.max_id}")
        self.chembot.set_coordinates(self.num2position(idx))
        self.chembot.devices.steppers.y_l.set_position(self.left_pipet_get_hight, speed=2500)
        self.chembot.devices.steppers.l_pipet.set_position(vol)
        self.left_pipet_vol = vol
        self.chembot.devices.steppers.y_l.set_position(0, speed=2500)

    def left_pipet_put(self, idx, vol=1500):
        # if self.max_id +1 < id:
        #     raise ValueError(f"Max id {self.max_id}")
        if vol > self.left_pipet_vol:
            raise ValueError("Not enough volume in left pipet")
        self.chembot.set_coordinates(self.num2position(idx))
        self.chembot.devices.steppers.y_l.set_position(self.left_pipet_put_hight, speed=2500)
        vol = self.left_pipet_vol - vol
        self.chembot.devices.steppers.l_pipet.set_position(vol, speed=1000)
        self.left_pipet_vol = vol
        self.chembot.devices.steppers.y_l.set_position(0, speed=2500)
