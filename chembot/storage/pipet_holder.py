from .basic_storage import BaseStorage
from ..data_structure import Coordinates
import numpy as np
from json import load
from .pipet_types import BluePipet


class PipetHolder(BaseStorage):

    def __init__(self, chembot, z_len=30, x_len=8, anchor=Coordinates(x=920, z=3280), x_step=128,
                 z_step=128):
        super().__init__(chembot=chembot, z_len=z_len, x_len=x_len, anchor=anchor, x_step=x_step,
                         z_step=z_step)
        self.__pipet_in_operation = None

    @property
    def pipet_in_operation(self):
        if pipet := self.__pipet_in_operation:
            return pipet
        else:
            self.next_pipet()
            return

    @pipet_in_operation.setter
    def pipet_in_operation(self, value):
        if isinstance(value, BluePipet):
            self.__pipet_in_operation = value

    def read(self, file):
        with open(file) as f:
            for i in load(f):
                self.fill_slot(i["idx"], BluePipet())  # there is only one pipet type now

    def get_pipet(self, idx: int):
        self.chembot.eject_pipet()
        self.chembot.set_coordinates(self.num2position(idx))
        self.chembot.steppers.y_l.set_position(36500, speed=3000)
        self.chembot.steppers.y_l.set_position(40000)
        self.chembot.steppers.y_l.set_position(0, speed=3000)
        self.pipet_in_operation = self.get_slot(idx)
        self.flush_slot(idx)
        return self.pipet_in_operation

    # def eject_pipet(self):
    #     self.chembot.set_coordinates(Coordinates(x=2786, z=4460))
    #     self.chembot.steppers.y_l.set_position(36500, speed=3000)
    #     self.chembot.steppers.y_l.set_position(40650)
    #     self.chembot.set_coordinates(Coordinates(x=2786, z=4400))
    #     self.chembot.steppers.y_l.set_position(0, speed=3000)

    def next_pipet(self):
        idx = self.next_occupied_slot_reversed
        self.get_pipet(idx)
        return idx


    def fill_from_config(self, data):
        for k,v in data.items():
            if v == "blue_pipet":
                self.fill_slot(k, BluePipet())

