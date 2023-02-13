import pathlib
from ctypes import CDLL, byref, c_int, c_ubyte, c_uint
from pathlib import Path
from time import sleep
from ..data_structure.basic_structures import LifeBotDriveMotor, bot_response, BaseDevice


class Motor(BaseDevice):
    def __init__(self, idx: int, **kwargs):
        super().__init__(**kwargs)
        self.id = idx
    
    def init(self):
        if not self.fake:
            self.bot_lib.LB_InitMotor(self.id)
            sleep(3)

    def drive(self, power=100, dir=0, time=100):
        if not self.fake:
            drive = LifeBotDriveMotor(self.id, power, dir, time)
            self.bot_lib.LB_DriveMotor(byref(drive))
    
    @property
    def _motor_state(self):
        if not self.fake:
            time_val = c_uint()
            return self.bot_lib.LB_GetMotorState(c_ubyte(self.id), byref(time_val))
        else:
            return 0

    @property
    def state(self):
        return bot_response[self._motor_state]


class CapRotator(Motor):
    def __init__(self, **kwargs):
        super().__init__(idx=145, **kwargs)

    def open(self, power=100, time=1000):
        self.drive(power=power, dir=0, time=time)
    
    def close(self, power=100, time=1000):
        self.drive(power=power, dir=1, time=time)


class CapRemover(Motor):
    def __init__(self, **kwargs):
        super().__init__(idx=17, **kwargs)

    def eject(self, time: int = 3000):
        self.drive(power=50, dir=0, time=time)
        
    def pins_up(self):
        self.drive(power=100, dir=1, time=2000)