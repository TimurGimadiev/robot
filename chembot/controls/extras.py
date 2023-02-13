from ctypes import CDLL
from pathlib import Path
from ..data_structure.basic_structures import BaseDevice


class BaseSwitch(BaseDevice):
    def __init__(self, id: int, **kwargs):
        super().__init__(**kwargs)
        self.id = id
    
    def power_on(self):
        if not self.fake:
            self.bot_lib.LB_SetOutputState(self.id, 1)
    
    def power_off(self):
        if not self.fake:
            self.bot_lib.LB_SetOutputState(self.id, 0)


class Pump(BaseSwitch):
    def __init__(self, **kwargs):
        super().__init__(id=6, **kwargs)


class WS1Cyl(BaseSwitch):
    def __init__(self, **kwargs):
        super().__init__(id=4, **kwargs)


class WS2Cyl(BaseSwitch):
    def __init__(self, **kwargs):
        super().__init__(id=3, **kwargs)


class VacuumRight(BaseSwitch):
    def __init__(self, **kwargs):
        super().__init__(id=1, **kwargs)


class VacuumLeft(BaseSwitch):
    def __init__(self, **kwargs):
        super().__init__(id=0, **kwargs)


class UVLamp(BaseSwitch):
    def __init__(self, **kwargs):
        super().__init__(id=7, **kwargs)


class Mixer(BaseSwitch):
    def __init__(self, **kwargs):
        super().__init__(id=5, **kwargs)


class VacuumTap:
    def __init__(self, **kwargs):
        self._left = VacuumLeft(**kwargs)
        self._right = VacuumRight(**kwargs)
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




