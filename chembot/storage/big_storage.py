from .basic_storage import BaseStorage
from ..data_structure import Coordinates
import numpy as np
from loguru import logger
from ..custom_types import Slots,State
from ..chemistry import smiles


class BigTubes(BaseStorage):
    def __init__(self, chembot, z_len=1, x_len=8, anchor=Coordinates(x=1350, z=3360), x_step=420,
                 z_step=420, **kwargs):

        super().__init__(chembot=chembot, z_len=z_len, x_len=x_len, anchor=anchor, x_step=x_step,
                         z_step=z_step, **kwargs)
        self.pipet_in_operation = None
        self.__pipet = None
        self.before_cap = 10000
        self.lowest = 12700
        self.left_pipet_vol = 0
        self.left_pipet_get_hight = 36000
        self.left_pipet_put_hight = 33000

    def left_pipet_get(self, idx, vol=1500):
        # if self.max_id + 1 < id:
        #     raise ValueError(f"Max id {self.max_id}")
        self.chembot.set_coordinates(self.num2position(idx))
        self.chembot.devices.steppers.y_l.set_position(self.left_pipet_get_hight, speed=2500)
        self.chembot.devices.steppers.l_pipet.set_position(vol)
        self.left_pipet_vol = vol
        self.chembot.devices.steppers.y_l.set_position(0, speed=2500)

    def left_pipet_put(self, idx, vol=1500):
        # if self.max_id +1 < id:
        #     raise ValueError(f"Max id {self.max_id}")
        if vol > self.left_pipet_vol:
            raise ValueError("Not enough volume in left pipet")
        self.chembot.set_coordinates(self.num2position(idx))
        self.chembot.devices.steppers.y_l.set_position(self.left_pipet_put_hight, speed=2500)
        vol = self.left_pipet_vol - vol
        self.chembot.devices.steppers.l_pipet.set_position(vol, speed=1000)
        self.left_pipet_vol = vol
        self.chembot.devices.steppers.y_l.set_position(0, speed=2500)

    def slot_from_mol_data(self, idx, data):
        # data = {"smiles": "CC(C)=O", "volume": 0.001, "moles": None, "state": "liquid", "density":
        #     0.784,
        #  "concentration": None,
        #  "solvent": {"smiles": None}}
        if isinstance(data, str):
            if data.upper() in [x.name for x in Slots]:
                self.fill_slot(idx, Slots[data.upper()])
                return
            else:
                raise ("not acceptable keyword")
        logger.info(f"mol = {data['smiles']}")
        mol = smiles(data["smiles"], substance=True)
        mol.canonicalize()
        mol.state = data["state"]
        if density := data.get("density"):
            logger.info(f"density = {density}")
            mol.density = density
            #logger.info(f"volume = {mol.density}")
        if pure_mass := data.get("mass"):
            mol.pure_mass = pure_mass
        if volume := data.get("volume"):
            if mol.state is State.LIQUID and not mol.concentration:
                if volume and mol.density:
                    mol.mols = volume * mol.density / mol.molecular_mass * 1000
                elif pure_mass and mol.density:
                    mol.mols = mol.pure_mass / mol.molecular_mass * 1000
            elif mol.state is State.LIQUID and mol.concentration and volume:
                mol.mols = volume * mol.concentration
            elif mol.state is State.LIQUID and mol.pure_mass:
                mol.mols = mol.pure_mass / mol.molecular_mass * 1000
            else:
                raise ValueError("mols or volume and density or pure mass should be provided")
    def fill_from_config(self, data):
        for k, v in data.items():
            if v:
                logger.info(f"{v}")
                self.slot_from_mol_data(k, v)
