from enum import Enum, auto


class State(Enum):
    LIQUID = auto()
    GAS = auto()
    SOLID = auto()


class Slots(Enum):
    EMPTY = auto()
    AVAILABLE = auto()
    USED = auto()
    PROCESSING = auto()