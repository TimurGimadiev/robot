from ..data_structure import Coordinates
from itertools import chain
from chembot import chembot
from time import sleep
from typing import List, Optional, Dict
#from image_process import predict
import numpy as np
from json import load

# def ml2steps(self, n):
#     if 0.05<=n<=1:
#         vol = round((10e8*n+2793*10e3)/312733)
#             return vol
#         else:
#             raise ValueError("incorrect volume")

# class Storages:
#     def __init__(self):
#         self.tubestorage = TubeStorage()
#         self.pipet_storage = PipetHolder()
#         self.reactor = Reactor()
#         self.bigtubes = BigTubes()
