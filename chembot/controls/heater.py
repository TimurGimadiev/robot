import os
import glob
from time import sleep
from threading import Thread, Event
from .extras import BaseSwitch
 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')


class Heater(BaseSwitch):
    def __init__(self):
        super().__init__(id=2)


class Thermometer:

    def __init__(self, id: str):
        self.device_file = f'/sys/bus/w1/devices/{id}/w1_slave' #28-000004e712b7
 
    def read_temp_raw(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines
    
    @property
    def temp_c(self):
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c


class Thermostat(Thread):
    
    def __init__(self, target_temp: float, heater: Heater = Heater(), thermometer: str =
    "28-000004e712b7",
                 period: int = 10):
        super().__init__()
        self.__taget_temp = round(target_temp, 1)
        self.thermometer = Thermometer(id=thermometer)
        self.event = Event()
        self.period = period
        self.heater = heater

    @property
    def taget_temp(self):
        return self.__taget_temp

    @taget_temp.setter
    def taget_temp(self, target_temp):
        self.__taget_temp = target_temp

    @property
    def cur_temp(self):
        return self.thermometer.temp_c

    def calc_pulse(self):
        dif = self.taget_temp - self.cur_temp
        if dif > 20:
            return self.period * 1
        elif 10 <= dif < 20:
            return self.period * 0.8
        elif 3 <= dif < 10:
            return self.period * 0.4
        elif 0 <= dif < 3:
            return self.period * 0.2
        elif -1 <= dif < 0:
            return self.period * 0.1
        else:
            return 0

    def run(self):
        while True:
            if self.event.is_set():
                break
            sleep_time = self.calc_pulse()
            self.heater.power_on()
            sleep(sleep_time)
            self.heater.power_off()
            sleep(self.period-sleep_time)



