

class CustomFloat(float):

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


class Molar(CustomFloat):

    def __repr__(self):
        return f"{self.real} M"


class Volume(CustomFloat):

    def __repr__(self):
        return f"{self.real} L"


class Mass(CustomFloat):

    def __repr__(self):
        return f"{self.real} KG"


class MolarConcentration(CustomFloat):

    def __repr__(self):
        return f"{self.real} M/L"


class Density(CustomFloat):

    def __repr__(self):
        return f"{self.real} KG/L"
