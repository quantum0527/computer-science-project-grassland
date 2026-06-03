import math
import random


class Vec2:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, value):
        return Vec2(self.x * value, self.y * value)

    __rmul__ = __mul__

    def __truediv__(self, value):
        if value == 0:
            return Vec2()
        return Vec2(self.x / value, self.y / value)

    def copy(self):
        return Vec2(self.x, self.y)

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalized(self):
        size = self.length()
        if size <= 0.0001:
            return Vec2()
        return self / size

    def distance_to(self, other):
        return (self - other).length()

    def limit(self, max_length):
        size = self.length()
        if size > max_length and size > 0:
            return self.normalized() * max_length
        return self.copy()

    def clamp(self, min_x, min_y, max_x, max_y):
        return Vec2(
            max(min_x, min(self.x, max_x)),
            max(min_y, min(self.y, max_y)),
        )

    def as_int_tuple(self):
        return int(self.x), int(self.y)


def random_unit_vector():
    angle = random.uniform(0, math.tau)
    return Vec2(math.cos(angle), math.sin(angle))

