from ctypes import CDLL
from pathlib import Path

path = Path("chembot/controls/libchembot.so").absolute()

bot_lib = CDLL(path)


class BaseSwitch:
    def __init__(self, id: int):
        self.id = id
    
    def power_on(self):
        bot_lib.LB_SetOutputState(self.id, 1)
    
    def power_off(self):
        bot_lib.LB_SetOutputState(self.id, 0)

class Pump(BaseSwitch):
    def __init__(self):
        super().__init__(id=6)

class WS1Cyl(BaseSwitch):
    def __init__(self):
        super().__init__(id=4)

class WS2Cyl(BaseSwitch):
    def __init__(self):
        super().__init__(id=3)

class VacuumRight(BaseSwitch):
    def __init__(self):
        super().__init__(id=1)

class VacuumLeft(BaseSwitch):
    def __init__(self):
        super().__init__(id=0)

class UVLamp(BaseSwitch):
    def __init__(self):
        super().__init__(id=7)

class Mixer(BaseSwitch):
    def __init__(self):
        super().__init__(id=5)

class VacuumTap:
    def __init__(self):
        self._left = VacuumLeft()
        self._right = VacuumRight()
        self._left.power_off()
        self._right.power_off()
        self._state = 0   

    def right(self):
        self._right.power_off()
        self._left.power_on()
        self._state = 0
    
    def left(self):
        self._left.power_off()
        self._right.power_on()
        self._state = 1

    def state(self):
        return "left" if self._state else "right"




