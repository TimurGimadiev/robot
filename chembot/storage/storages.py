from .basic_storage import BaseStorage
from .big_storage import BigTubes
from .pipet_types import BluePipet
from .pipet_holder import PipetHolder
from .reactor import Reactor
from .tube_storage import TubeStorage


class Storages:

    def __init__(self, chembot, fake=False):
        self.big_tubes = BigTubes(chembot=chembot)
        self.pipet_holder = PipetHolder(chembot=chembot)
        self.reactor = Reactor(chembot=chembot, fake=fake)
        self.tube_storage = TubeStorage(chembot=chembot)