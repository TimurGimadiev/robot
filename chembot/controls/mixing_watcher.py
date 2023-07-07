from time import time, sleep
from .extras import Mixer
from threading import Thread, Event
from typing import Optional

class MixWatcher(Thread):

    def __init__(self, target_time: float, mixer: Optional[Mixer] = None,
                 period: int = 30, fake: bool = False):
        super().__init__()
        self.__target_time = target_time
        self.start_time = None
        self.pause_event = Event()
        self.pause()
        self.period = period
        if not fake:
            self.mixer = mixer if mixer else Mixer()
        else:
            self.mixer = Mixer(fake=True)
        self.fake = fake
        self.__shake_periods = 0

    def pause(self):
        self.pause_event.set()

    def unpause(self):
        self.pause_event.clear()

    @property
    def target_time(self):
        return self.__target_time

    @target_time.setter
    def target_time(self, target_time):
        self.__target_time = target_time

    @property
    def remaining_time(self):
        return self.target_time - self.start_time

    @property
    def finished_shakes(self):
        return self.__shake_periods

    def run(self):
        self.start_time = time()
        while True:
            #if time() - self.start_time >= self.target_time:
            #    self.pause_event.set()
            #    break
            if self.pause_event.is_set():
                sleep(30)
            else:
                #sleep_time = self.period
                self.mixer.power_on()
                sleep(self.period)
                self.mixer.power_off()
                self.__shake_periods += 1
                sleep(self.period)

