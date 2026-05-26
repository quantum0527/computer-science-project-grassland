from __future__ import annotations

import math

from grassland.entities.animals.carnivores.carnivore import Carnivore
from grassland.entities.resources.carcass import Carcass
from grassland.geometry import Vec2


class BaldEagle(Carnivore):
    threatens_herbivores = False

    def __init__(self, position: Vec2):
        super().__init__("Bald_Eagle", position, color=(205, 205, 205), health=70, speed=92, power=6, detect_range=280)
        self.is_flying = True
        self.fly_speed = 120.0
        self.fly_time = 0.0
        self.z = 35.0
        self.radius = 17

    def behave(self, world: object, dt: float) -> bool:
        carcass = world.nearest_carcass(self.position)
        if carcass is None:
            self.fly(dt)
            return False
        nearby_lion = world.nearest_named("Lion", carcass.position, 110.0)
        if nearby_lion is not None:
            self.fly(dt)
            self.move_away_from(nearby_lion.position, self.fly_speed)
            self.action_text = "wait"
            return True
        if self.position.distance_to(carcass.position) <= self.radius + carcass.radius + 8:
            self.land()
            self.eat_carcass(carcass)
        else:
            self.fly(dt)
            self.move_toward(carcass.position, self.fly_speed)
            self.action_text = "carcass"
        return True

    def fly(self, dt: float) -> None:
        self.is_flying = True
        self.fly_time += dt
        self.z = 35.0 + math.sin(self.fly_time * 4.0) * 6.0

    def land(self) -> None:
        self.is_flying = False
        self.z = 0.0

    def eat_carcass(self, other: Carcass) -> None:
        other.reduce_hunger(self)
