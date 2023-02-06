from ctypes import CDLL, c_ubyte, byref, c_int
from ..data_structure import LifeBotStepperPos, LifeBotDeviceInfo, bot_response
from pathlib import Path
import time

path = Path("chembot/controls/libchembot.so").absolute()

bot_lib = CDLL(path)


class Stepper:
    def __init__(self, id):
        self.id = id
        self.position = None
        self.blocked = False

    def init(self) -> None:
        if self.blocked:
            raise ValueError("device is blocked please move it manually")
        bot_lib.LB_StepperInit(c_ubyte(self.id))
        self.position = 0
        time.sleep(3)

    def _validate_position(self, position: int) -> bool:
        if self.blocked:
            raise ValueError("device is blocked please move it manually or unlock properly")
        if self.state == "NotInitialized" or position is None:
            raise ValueError("Stepper motor is not initialized")
        position = position if position > 0 else 0
        control = self.limit > position
        if control:
            return control
        else:
            raise ValueError("position is out of range")

    @property
    def _stepper_state(self):
        position = c_int()
        return bot_lib.LB_GetStepperState(c_ubyte(self.id), byref(position))

    @property
    def state(self):
        return bot_response[self._stepper_state]

    def wait(self) -> None:
        while self._stepper_state:
            #continue
            time.sleep(0.1)
            #print(r)
        #print(r)
    
    def set_position(self, position: int, speed: int = 1500, mode: int = 0,
                     soft_start_time: int = 0, blocking_processes=True):
        if self._validate_position(position):
            self.wait()
            pos = LifeBotStepperPos(c_ubyte(self.id), position, speed, mode, soft_start_time)
            bot_lib.LB_SetStepperPos(byref(pos))
            self.position = position
            if blocking_processes:
                self.wait()


class XAxis(Stepper):
    def __init__(self):
        super().__init__(id=0)
        self.limit = 4550


class ZAxis(Stepper):
    def __init__(self):
        super().__init__(id=1)
        self.limit = 5800


class YAxisL(Stepper):
    def __init__(self):
        super().__init__(id=2)
        self.limit = 41000
        

class YAxisR(Stepper):
    def __init__(self):
        super().__init__(id=3)
        self.limit = 41000


class Opener(Stepper):
    def __init__(self):
        super().__init__(id=4)
        self.limit = 15500
        self.lower = 12700


class LeftPipet(Stepper):
    def __init__(self):
        super().__init__(id=5)
        self.limit = 4200


class RightPipet(Stepper):
    def __init__(self):
        super().__init__(id=6)
        self.limit = 4000


class WS1(Stepper):
    def __init__(self): # 30000 - 0.64 g 50000 - 1.06 g
    # compensation between suction and feed of solvent 4.7% 3300 step in 70000 steps
        super().__init__(id=7)
        self.limit = 99999999


class WS2(Stepper):
    def __init__(self):
        super().__init__(id=8)
        self.limit = 99999999


class ES(Stepper):
    def __init__(self):
        super().__init__(id=9)


__all__ = ["XAxis", "ZAxis", "YAxisL", "YAxisR", "Opener", "LeftPipet", "RightPipet", "WS1",
           "WS2", "ES"]