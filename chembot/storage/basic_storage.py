import numpy as np
from ..chemistry import Molecule
from typing import Union
from ..data_structure import Coordinates


class BaseStorage:

    def __init__(self, z_len, x_len, anchor, x_step, z_step):
        self.__slots = dict(enumerate(np.zeros((z_len, x_len)).flatten(), 1))
        self.z_len = z_len
        self.x_len = x_len
        self.anchor = anchor
        self.x_step = x_step
        self.z_step = z_step

    def step(self, z: int = 0, x: int = 0) -> Coordinates:
        if x >= 0:                                                      # +right, -left
            new_x = self.anchor.x + self.x_step * x
        else:
            new_x = self.anchor.x - self.x_step * x
        if z >= 0:                                                      # +forward, -backward
            new_z = self.anchor.z + self.z_step * z
        else:
            new_z = self.anchor.z - self.z_step * z
        return Coordinates(z=new_z, x=new_x)


    def num2position(self, n) -> Coordinates:
        if max(self.slots) > n > 0:
            n -= 1
            z, x = n // self.x_len, n % self.x_len
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
        for k, v in self.slots.items():
            if v:
                return k

    @property
    def next_occupied_slot_reversed(self):
        for row in np.array_split(np.array(list(self.slots)), self.z_len):
            for value in row[::-1]:
                return value





