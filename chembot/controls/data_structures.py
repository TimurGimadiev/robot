from ctypes import c_ubyte, c_uint, c_ushort, c_int, c_ulonglong, Structure, CDLL
from collections import namedtuple
from pathlib import Path


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

class LifeBotInput(Structure):
    _fields_ = [("ananlogInputs", c_ushort * 10)]


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
