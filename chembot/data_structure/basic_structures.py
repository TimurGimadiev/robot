from ctypes import c_ubyte, c_uint, c_ushort, c_int, c_ulonglong, Structure
from collections import namedtuple


class LifeBotStepperPos(Structure):
    _fields_ = [("idx", c_ubyte),
                ("iPos", c_uint),
                ("nSpeed", c_ushort),
                ("mode", c_int),
                ("nSoftStartTime", c_ushort)]


class LifeBotDeviceInfo(Structure):
    _fields_ = [("nProtocolVersion", c_ushort),
                ("nHardwareVersion", c_ushort),
                ("nFirmwareVersion", c_ushort),
                ("nSerial", c_ulonglong),
                ("nRevision", c_uint)]


class LifeBotDriveMotor(Structure):
    _fields_ = [("idx", c_ubyte),
                ("nPower", c_ubyte),
                ("nDir", c_ubyte),
                ("nTime", c_uint)]


bot_response = {
    0: "Success",
    1: "Ordered",
    2: "NotReady",
    129: "InvalidData",
    130: "InvalidRType",
    131: "IntercomFault",
    132: "NotInitialized",
    253: "DeviceError",
    254: "TransactError",
    255: "Disconnect",
}

Coordinates = namedtuple("Coordinates", ["x", "z"])

Compound = namedtuple("Compound", ["storage_type", "tube", "amount", "ingredients"])


class SubstanceStructure:
    def __init__(self, molecule, volume, solvent, concentration=None, mass=None, density = None):
        self.concentration = concentration
        self.molecule = molecule
        self.mass = mass
        self.density = density
        self.volume = volume
        self.solvent = solvent
        if self.concentration and self.mass or not self.concentration and self.mass:
            raise "mass or concentration should be provided"
        if not self.concentration:
            moles = self.mass / self.molecule.molecular_mass
            self.concentration = moles / volume
        if not self.mass:
            moles = self.concentration * self.volume
            self.mass = moles / self.molecule.molecular_mass

    @property
    def mols(self):
        return self.mass / self.molecule.molecular_mass


class Solution:

    def __init__(self, components: list[SubstanceStructure], solvent):
        self.components = [{"component": x} for x in components]
        self.solvent = solvent
        #self._len = len(self.components)

    def _calculate_concentrations(self):
        for substance in self.components:
            substance["concentration"] = 10


Component = namedtuple("Component", ["storage_type", "tube", "amount", "compounds"])


#__all__ = ["LifeBotStepperPos", "Coordinates","bot_response", "LifeBotDeviceInfo",
#"LifeBotDriveMotor"]