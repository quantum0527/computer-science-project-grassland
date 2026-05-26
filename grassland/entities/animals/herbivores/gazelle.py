from __future__ import annotations

import math

from grassland.entities.animals.animal import Animal
from grassland.entities.animals.herbivores.herbivore import Herbivore
from grassland.geometry import Vec2


class Gazelle(Herbivore):
    def __init__(self, position: Vec2):
        super().__init__("Gazelle", position, color=(214, 162, 91), health=60, speed=96, power=0, detect_range=185)
        self.endurance = 0.62
        self.zigzag_angle = 0.9

    def can_hide_in_bush(self) -> bool:
        return True

    def fight_or_flight(self, threat: Animal, world: object, dt: float) -> None:
        self.zigzag(threat, world.elapsed)
        self.lose_energy(5.0 * self.endurance * dt)
        self.action_text = "zigzag"

    def zigzag(self, threat: Animal, elapsed: float) -> None:
        away = (self.position - threat.position).normalized()
        side = Vec2(-away.y, away.x) * math.sin(elapsed * 7.0) * self.zigzag_angle
        self.velocity = (away + side).normalized() * self.flee_speed
