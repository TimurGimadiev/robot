from enum import Enum, auto


class Scale(Enum):
    MICRO = auto()
    MILLI = auto()
    DECI = auto()


class CustomFloat(float):
    scaledict = {Scale.DECI: {"multiplier": 1e1, "prefix": "d"},
                 Scale.MICRO: {"multiplier": 1e6, "prefix": "µ"},
                 Scale.MILLI: {"multiplier": 1e3, "prefix": "m"}}
    mapping = {value["prefix"]: key.name for key, value in scaledict.items()}

    def __format__(self, scale):
        scale = scale.upper()
        if scale in [x.name for x in Scale]:
            return f"{self.real * self.scaledict[Scale[scale]]['multiplier']}" \
                   f" {self.scaledict[Scale[scale]]['prefix']}{self.unit}"

    def __add__(self, other):
        return type(self)(self.real + other)

    def __mul__(self, other):
        return type(self)(self.real * other)

    def __imul__(self, other):
        return type(self)(self.real * other)

    def __iadd__(self, other):
        return type(self)(self.real + other)

    def __rmul__(self, other):
        return type(self)(self.real * other)

    def __radd__(self, other):
        return type(self)(self.real + other)

    def show_units(self, prefix):
        return self.__format__(self.mapping[prefix].name.lower())

    def get_units(self, prefix):
        return self.real * self.scaledict[self.mapping[prefix]]["multiplier"]


class Molar(CustomFloat):

    unit = "M"

    def __repr__(self):
        return f"{self.real} {self.unit}"

    def __str__(self):
        return f"{self.real} {self.unit}"


class Volume(CustomFloat):

    unit = "L"

    def __repr__(self):
        return f"{self.real} {self.unit}"

    def __str__(self):
        return f"{self.real} {self.unit}"

    @property
    def show_mk(self):
        return self.__format__(Scale.MICRO.name)

    @property
    def show_ml(self):
        return self.__format__(Scale.MILLI.name)

    def convert_to(self, scale):
        return self.__format__(self.mapping[scale])


class Mass(CustomFloat):

    def __repr__(self):
        return f"{self.real} KG"

    def __str__(self):
        return f"{self.real} {self.unit}"


class MolarConcentration(CustomFloat):

    def __repr__(self):
        return f"{self.real} M/L"

    def __str__(self):
        return f"{self.real} {self.unit}"


class Density(CustomFloat):

    def __repr__(self):
        return f"{self.real} KG/L"

    def __str__(self):
        return f"{self.real} {self.unit}"
