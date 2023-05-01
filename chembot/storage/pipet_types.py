# Description of pipets, their volume and mapping to steps of motor
class BluePipet:

    def __init__(self):
        self.min_limit = 0.05
        self.max_limit = 1
        self.occupied_vol = 0

    def volume_to_steps(self, n):
        if self.min_limit <= n <= self.max_limit:
            vol = round((10e8 * n + 2793 * 10e3) / 312733)
            return vol
        else:
            raise ValueError("incorrect volume")