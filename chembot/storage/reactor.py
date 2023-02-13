from .tube_storage import TubeStorage
from ..data_structure import Coordinates
import numpy as np
from ..computer_vision import predict as visual_control


class Reactor(TubeStorage):
    def __init__(self, chembot, z_len=4, x_len=4, anchor=Coordinates(x=950, z=3410), x_step=256,
                 z_step=256, fake: bool = False):
        super().__init__(chembot=chembot, z_len=z_len, x_len=x_len, anchor=anchor, x_step=x_step,
                         z_step=z_step, fake=fake)
        # anchor = Coordinates(x=950, z=3410)
        # self.anchor = Coordinates(x=920, z=3280)
        #self.holders = np.ones((4, 4))
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
        if not self.fake:
            self.chembot.set_coordinates(Coordinates(3600, 3800))
            self.chembot.set_coordinates(Coordinates(4100, 4300))
            res = visual_control()
            self.x_correction, self.z_correction = sorted(res, key=lambda x: abs(x[0]) + abs(x[1]))[0]
            x = 4100 + self.x_correction / self.x_scale - 360
            z = 4300 + self.z_correction / self.z_scale + 750
            self.anchor = Coordinates(x=int(x), z=int(z))

