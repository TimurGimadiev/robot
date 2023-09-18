from chembot import chembot
from threading import Thread
from chembot.actions.synthesys import Synthesis
from time import time, sleep
from loguru import logger


class Watcher:

    def __init__(self, synthesys_queue: list[Synthesis], override_conditions=False,
                 temperature=None, time=None):
        # for now all conditions should be the same
        self.synthesys_queue = synthesys_queue
        self.time = 5 #synthesys_queue[0].time
        self.temperature = synthesys_queue[0].temperature

    def start(self):
        for synthesys in self.synthesys_queue:
            synthesys.do_synthesys()
        if self.synthesys_queue:
            chembot.thermostart.target_temp = self.temperature
            while time() - self.synthesys_queue[0].start_time < self.synthesys_queue[0].time:
                sleep(5)
                logger.info(f"current temperature {chembot.thermostart.cur_temp}"
                            f"mixing ")


            chembot.stop_mix()
            chembot.thermostart.pause()
        logger.info(f"all tasks finished")




