from .basic_storage import BaseStorage
from ..data_structure import Coordinates
import numpy as np
from ..controls.chembot import chembot
from json import load
from .pipet_types import BluePipet


class PipetHolder(BaseStorage):

    def __init__(self, z_len, x_len, anchor=Coordinates(x=920, z=3280), x_step=128,
                 z_step=128):
        super().__init__(z_len, x_len, anchor, x_step, z_step)
        self.pipet_in_operation = None

    def read(self, file):
        with open(file) as f:
            for i in load(f):
                self.fill_slot(i["idx"], BluePipet())  # there is only one pipet type now

    def get_pipet(self, idx: int):
        chembot.set_coordinates(self.num2position(idx))
        chembot.steppers.y_l.set_position(36500, speed=3000)
        chembot.steppers.y_l.set_position(40000)
        chembot.steppers.y_l.set_position(0, speed=3000)
        self.pipet_in_operation = self.get_slot(idx)
        self.flush_slot(idx)

    # def eject_pipet(self):
    #     chembot.set_coordinates(Coordinates(x=2786, z=4460))
    #     chembot.steppers.y_l.set_position(36500, speed=3000)
    #     chembot.steppers.y_l.set_position(40650)
    #     chembot.set_coordinates(Coordinates(x=2786, z=4400))
    #     chembot.steppers.y_l.set_position(0, speed=3000)

    def next_pipet(self):
        idx = self.next_occupied_slot_reversed
        self.get_pipet(idx)

