import pathlib
from ctypes import CDLL, byref, c_int, c_ubyte, c_uint
from pathlib import Path
from time import sleep
from ..data_structure import LifeBotDriveMotor, bot_response

path = Path("chembot/controls/libchembot.so").absolute()
bot_lib = CDLL(path)


class Motor:
    def __init__(self, id):
        self.id = id
    
    def init(self):
        bot_lib.LB_InitMotor(self.id)
        sleep(3)

    def drive(self, power=100, dir=0, time=100):
        drive = LifeBotDriveMotor(self.id, power, dir, time)
        bot_lib.LB_DriveMotor(byref(drive))
    
    @property
    def _motor_state(self):
        time_val = c_uint()
        return bot_lib.LB_GetMotorState(c_ubyte(self.id), byref(time_val))

    @property
    def state(self):
        return bot_response[self._motor_state]


class CapRotator(Motor):
    def __init__(self):
        super().__init__(id=145)

    def open(self, power=100, time=1000):
        self.drive(power=power, dir=0, time=time)
    
    def close(self, power=100, time=1000):
        self.drive(power=power, dir=1, time=time)


class CapRemover(Motor):
    def __init__(self):
        super().__init__(id=17)

    def eject(self, time = 3000):
        self.drive(power=50, dir=0, time=time)
        
    def pins_up(self):
        self.drive(power=100, dir=1, time=2000)