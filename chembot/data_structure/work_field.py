import numpy as np
from ..chemistry import Molecule
from typing import Union
from .basic_structures import Coordinates


class WorkField:

    def __init__(self, height, width, anchor, x_step, z_step):
        self.__slots = dict(enumerate(np.zeros((height, width)).flatten(), 1))
        self.height = height
        self.width = width
        self.anchor = anchor
        self.x_step = x_step
        self.z_step = z_step

    def step(self, z: int = 0, x: int = 0) -> Coordinates:  # +right, -left
        if x >= 0:
            new_x = self.anchor.x + self.x_step * x
        else:
            new_x = self.anchor.x - self.x_step * x
        if z >= 0:
            new_z = self.anchor.z + self.z_step * z
        else:
            new_z = self.anchor.z - self.z_step * z
        return Coordinates(z=new_z, x=new_x)

    def num2position(self, n) -> Coordinates:
        if max(self.slots) > n > 0:
            n -= 1
            z, x = n // self.width, n % self.width
            return self.step(z, x)
        raise ValueError("outside acceptable numbers")

    # def position2num(self, position: Coordinates) -> int:
    #     return position.z * 8 + position.x

    def fill_slot(self, slot_id, obj_x):
        self.__slots[slot_id] = obj_x

    def get_slot(self, slot_id):
        return self.__slots[slot_id]

    @property
    def slots(self):
        return self.__slots

    @property
    def next_free_slot(self):
        for k, v in self.__slots.items():
            if not v:
                return k

    def flush_slot(self, slot_id):
        self.__slots[slot_id] = .0

    @property
    def next_occupied_slot(self):
        for k, v in self.__slots.items():
            if v:
                return k

    # def ____(self):
    #     return max(self.__slots)




