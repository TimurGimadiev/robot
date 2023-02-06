from .tube_storage import TubeStorage
from ..data_structure import Coordinates
import numpy as np
from ..controls import chembot


class Reactor(TubeStorage):
    def __init__(self):
        super().__init__()
        # anchor = Coordinates(x=950, z=3410)
        # self.anchor = Coordinates(x=920, z=3280)
        self.holders = np.ones((4, 4))
        self.pipet_in_operation = None
        self.x_correction = None
        self.z_correction = None
        self.x_scale = 3.8
        self.z_scale = 6.5
        self.anchor_correct()
        self.before_cap = 10000
        self.lowest = 12700
        self.left_pipet_vol = 0
        self.left_pipet_get_hight = 36000  # 36000 отбор проб из вортекса

    def anchor_correct(self):
        chembot.set_coordinates(Coordinates(3600, 3800))
        chembot.set_coordinates(Coordinates(4100, 4300))
        res = predict()
        self.x_correction, self.z_correction = sorted(res, key=lambda x: abs(x[0]) + abs(x[1]))[0]
        x = 4100 + self.x_correction / self.x_scale - 360
        z = 4300 + self.z_correction / self.z_scale + 750
        self.anchor = Coordinates(x=int(x), z=int(z))

    def holder_coordinate(self, position) -> Coordinates:
        return Coordinates(self.step_right(position.x).x, self.step_forward(position.z).z)

    def holder_by_number(self, id: int) -> Coordinates:
        return self.holder_coordinate(self.num2position(id))

    def num2position(self, n) -> tuple[int, int]:
        n -= 1  # ids starts from 1
        z, x = n // 4, n % 4
        return Coordinates(x, z)

    def position2num(self, position: Coordinates) -> int:
        return position.z * 8 + position.x + 1