from ..data_structure.basic_structures import LifeBotInput, BaseDevice


class Inputs(BaseDevice):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inputs = LifeBotInput()

    def get_status(self, num):
        if 9 < num < 0:
            raise ValueError("out of index")
        if not self.fake:
            self.bot_lib.LB_GetAnalogInputs(self.inputs)
        return self.inputs[num]

