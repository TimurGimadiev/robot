from .motor import CapRemover, CapRotator
from .stepper import XAxis, ZAxis, YAxisL, YAxisR, Opener, RightPipet, LeftPipet, WS1, WS2, ES
from .data_structures import Coordinates
from .extras import Pump, WS1Cyl, WS2Cyl, VacuumTap, UVLamp, Mixer
from .heater import Thermometer, Thermostat, Heater


class Base:
    def get_states(self):
        result = {}
        for device in self.__dict__.values():
            result[device] = device.state
        return result
    
    def _get_states(self):
        result = {}
        for device in self.__dict__.values():
            result[device] = device._stepper_state()
        return result

    def init_all(self):
        for device in self.__dict__.values():
            device.init()


class Steppers(Base):

    def __init__(self, **kwargs) -> None:
        self.y_r = YAxisR(**kwargs)
        self.y_l = YAxisL(**kwargs)
        self.op = Opener(**kwargs)
        self.l_pipet = LeftPipet(**kwargs)
        self.r_pipet = RightPipet(**kwargs)
        self.ws1 = WS1(**kwargs)
        self.ws2 = WS2(**kwargs)
        self.es = ES(**kwargs)
        self.x = XAxis(**kwargs)
        self.z = ZAxis(**kwargs)


class Motors(Base):

    def __init__(self, **kwargs) -> None:
        self.cap_remover = CapRemover(**kwargs)
        self.cap_rotator = CapRotator(**kwargs)


class Extras():
    def __init__(self, **kwargs):
        self.pump = Pump(**kwargs)
        self.ws1_cyl = WS1Cyl(**kwargs)
        self.ws2_cyl = WS2Cyl(**kwargs)
        self.vacuum_tap = VacuumTap(**kwargs)
        self.uv_lamp = UVLamp(**kwargs)
        self.mixer = Mixer(**kwargs)
        self.heater = Heater(**kwargs)


# class Chembot:
#
#     def __init__(self, **kwargs) -> None:
#         self.steppers = Steppers(**kwargs)
#         self.motors = Motors(**kwargs)
#         self.extras = Extras(**kwargs)
#
#     def init_all(self):
#         self.motors.init_all()
#         self.steppers.init_all()
#
#     @property
#     def coord_initialized(self):
#         return not self.steppers.x._stepper_state and not self.steppers.z._stepper_state
#
#     def set_coordinates(self, coord: Coordinates, speed: int = 1500, x_first = True):
#         if self.coord_initialized:
#             if x_first:
#                 self.steppers.x.set_position(coord.x, speed=speed)
#                 self.steppers.z.set_position(coord.z, speed=speed)
#             else:
#                 self.steppers.z.set_position(coord.z, speed=speed)
#                 self.steppers.x.set_position(coord.x, speed=speed)
#
    # def get_eppendorf(self, tube_storage: TubeStorage, epp_position: tuple):
    #     coord = Coordinates(tube_storage.anchor.x - \
    #         (len(tube_storage.holders[0]) - epp_position[0]) * tube_storage.x_step, \
    #         tube_storage.anchor.z - (len(tube_storage.holders) - epp_position[1]) * tube_storage.z_step)
    #     self.set_coordinates(coord)
    #     self.devices.steppers.op.set_position(self.devices.steppers.op.lower)
    #     self.devices.steppers.op.set_position(0)
    
    # def drop_eppendorf(self, tube_storage: TubeStorage, epp_position: tuple):
    #     coord = Coordinates(tube_storage.anchor.x - \
    #         (len(tube_storage.holders[0]) - epp_position[0]) * tube_storage.x_step, \
    #         tube_storage.anchor.z - (len(tube_storage.holders) - epp_position[1]) * tube_storage.z_step)
    #     self.set_coordinates(coord)
    #     self.devices.steppers.op.set_position(int(self.devices.steppers.op.lower * 0.1))
    #     self.devices.motors.cap_remover.eject()
    #     self.devices.steppers.op.set_position(0)

    @property
    def coordinates(self):
        return {"x": self.steppers.x.position,
                "z": self.steppers.z.position}

    def lock_coordinates(self):
        self.steppers.x.blocked=True
        self.steppers.z.blocked=True
    
    def unlock_coordinates(self):
        self.steppers.x.blocked=False
        self.steppers.z.blocked=False
    
    def set_zero(self):
        self.set_coordinates(Coordinates(0, 0))
    
    def set_sampler_position(self):
        self.set_coordinates(Coordinates(x=2100, z=3270))

    def set_solvent_to_sampler_position(self):
        self.set_coordinates(Coordinates(x=20, z=5300))

    def eject_pipet(self):
        self.set_coordinates(Coordinates(x=2786, z=4460))
        self.steppers.y_l.set_position(36500, speed=3000)
        self.steppers.y_l.set_position(40650)
        self.set_coordinates(Coordinates(x=2786, z=4400))
        self.steppers.y_l.set_position(0, speed=3000)


#chembot = Chembot()
#chembot_fake = Chembot(fake=True)