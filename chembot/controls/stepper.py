from ctypes import CDLL, c_ubyte, byref, c_int
from ..data_structure.basic_structures import LifeBotStepperPos, LifeBotDeviceInfo, bot_response,\
    BaseDevice
from pathlib import Path
import time
from ctypes import CDLL


class Stepper(BaseDevice):
    def __init__(self, id, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.position = None
        self.blocked = False
        self.limit = None

    def init(self) -> None:
        if not self.fake:
            if self.blocked:
                raise ValueError("device is blocked please move it manually")
            self.bot_lib.LB_StepperInit(c_ubyte(self.id))
            time.sleep(3)
        self.position = 0

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
        if not self.fake:
            position = c_int()
            return self.bot_lib.LB_GetStepperState(c_ubyte(self.id), byref(position))
        else:
            return 0

    @property
    def state(self):
        return bot_response[self._stepper_state]

    def wait(self) -> None:
        while self._stepper_state:
            #continue
            time.sleep(0.1)
            #print(r)
        #print(r)
    
    def set_position(self, position: int, speed: int = 5000, mode: int = 1,
                     #speed=5000, mode=1, soft_start_time=500
                     soft_start_time: int = 500, blocking_processes=True):
        if self._validate_position(position):
            self.wait()
            if not self.fake:
                pos = LifeBotStepperPos(c_ubyte(self.id), position, speed, mode, soft_start_time)
                self.bot_lib.LB_SetStepperPos(byref(pos))
            self.position = position
            if blocking_processes:
                self.wait()


class XAxis(Stepper):
    def __init__(self, **kwargs):
        super().__init__(id=0, **kwargs)
        self.limit = 4550


class ZAxis(Stepper):
    def __init__(self, **kwargs):
        super().__init__(id=1, **kwargs)
        self.limit = 6080


class YAxisL(Stepper):
    def __init__(self, **kwargs):
        super().__init__(id=2, **kwargs)
        self.limit = 41000
        

class YAxisR(Stepper):
    def __init__(self, **kwargs):
        super().__init__(id=3, **kwargs)
        self.limit = 41000


class Opener(Stepper):
    def __init__(self, **kwargs):
        super().__init__(id=4, **kwargs)
        self.limit = 15500
        self.lower = 12700


class LeftPipet(Stepper):
    def __init__(self, **kwargs):
        super().__init__(id=5, **kwargs)
        self.limit = 4200


class RightPipet(Stepper):
    def __init__(self, **kwargs):
        super().__init__(id=6, **kwargs)
        self.limit = 4000


class WS1(Stepper):
    def __init__(self, **kwargs): # 30000 - 0.64 g 50000 - 1.06 g
    # compensation between suction and feed of solvent 4.7% 3300 step in 70000 steps
        super().__init__(id=7, **kwargs)
        self.limit = 99999999


class WS2(Stepper):
    def __init__(self, **kwargs):
        super().__init__(id=8, **kwargs)
        self.limit = 99999999


class ES(Stepper):
    def __init__(self, **kwargs):
        super().__init__(id=9, **kwargs)


class External(Stepper):
    def __init__(self, **kwargs):
        super().__init__(id=13, **kwargs)


__all__ = ["XAxis", "ZAxis", "YAxisL", "YAxisR", "Opener", "LeftPipet", "RightPipet", "WS1",
           "WS2", "ES", "External"]