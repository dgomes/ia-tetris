from common import Dimensions
import random

S = ('S', [
    [".....", ".....", "..11.", ".11..", "....."],
    [".....", "..1..", "..11.", "...1.", "....."],
])

Z = ('Z', [
    [".....", ".....", ".11..", "..11.", "....."],
    [".....", "..1..", ".11..", ".1...", "....."],
])

I = ('I', [
    ["..1..", "..1..", "..1..", "..1..", "....."],
    [".....", "1111.", ".....", ".....", "....."],
])

O = ('O', [[".....", ".....", ".11..", ".11..", "....."]])


J = ('J', [
    [".....", ".1...", ".111.", ".....", "....."],
    [".....", "..11.", "..1..", "..1..", "....."],
    [".....", ".....", ".111.", "...1.", "....."],
    [".....", "..1..", "..1..", ".11..", "....."],
])

L = ('L', [
    [".....", "...1.", ".111.", ".....", "....."],
    [".....", "..1..", "..1..", "..11.", "....."],
    [".....", ".....", ".111.", ".1...", "....."],
    [".....", ".11..", "..1..", "..1..", "....."],
])

T = ('T', [
    [".....", "..1..", ".111.", ".....", "....."],
    [".....", "..1..", "..11.", "..1..", "....."],
    [".....", ".....", ".111.", "..1..", "....."],
    [".....", "..1..", ".11..", "..1..", "....."],
])

Plan_dict = {"T": T, "L": L, "J": J, "O": O, "I": I, "Z": Z, "S": S}

class Shape:
    def __init__(self, plan) -> None:
        self.plan = plan[1]
        self.letter = plan[0]
        self.rotation = 0
        self.dimensions = Dimensions(5, 5)

        self._x = 0
        self._y = 0
        self.rotate()
    
    @staticmethod
    def FromLetter(letter):
        return Shape(Plan_dict[letter])

    def set_pos(self, x, y):
        x = int(x)
        y = int(y)
        self.positions = [
            (cx + x - self._x, cy + y - self._y) for cx, cy in self.positions
        ]
        self._x = x
        self._y = y

    def rotate(self, step=1):
        self.rotation = (self.rotation + step) % len(self.plan)
        self.set_rotation(self.rotation)

    def set_rotation(self, rotation):
        self.rotation = rotation % len(self.plan)
        self.positions = [
            (self._x + x, self._y + y)
            for y, line in enumerate(self.plan[self.rotation])
            for x, pos in enumerate(line)
            if pos == "1"
        ]

    def translate(self, x, y):
        self.set_pos(self._x + x, self._y + y)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self.set_pos(x, self._y)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self.set_pos(self._x, y)

    def __str__(self) -> str:
        return f"Shape({self._x},{self._y}) -> {self.positions}"


SHAPES = [Shape(s) for s in [S, Z, I, O, J, T, L]]

if __name__ == "__main__":
    s = Shape(S)
    print(random.choice(SHAPES))
