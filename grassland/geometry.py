from __future__ import annotations

from dataclasses import dataclass
import math
import random


@dataclass
class Vec2:
    x: float = 0.0
    y: float = 0.0

    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, value: float) -> "Vec2":
        return Vec2(self.x * value, self.y * value)

    __rmul__ = __mul__

    def __truediv__(self, value: float) -> "Vec2":
        if value == 0:
            return Vec2()
        return Vec2(self.x / value, self.y / value)

    def copy(self) -> "Vec2":
        return Vec2(self.x, self.y)

    def length_squared(self) -> float:
        return self.x * self.x + self.y * self.y

    def length(self) -> float:
        return math.sqrt(self.length_squared())

    def normalized(self) -> "Vec2":
        size = self.length()
        if size <= 0.0001:
            return Vec2()
        return self / size

    def distance_to(self, other: "Vec2") -> float:
        return (self - other).length()

    def limit(self, max_length: float) -> "Vec2":
        size = self.length()
        if size > max_length and size > 0:
            return self.normalized() * max_length
        return self.copy()

    def clamp(self, min_x: float, min_y: float, max_x: float, max_y: float) -> "Vec2":
        return Vec2(
            max(min_x, min(self.x, max_x)),
            max(min_y, min(self.y, max_y)),
        )

    def as_int_tuple(self) -> tuple[int, int]:
        return int(self.x), int(self.y)


def random_unit_vector() -> Vec2:
    angle = random.uniform(0, math.tau)
    return Vec2(math.cos(angle), math.sin(angle))

