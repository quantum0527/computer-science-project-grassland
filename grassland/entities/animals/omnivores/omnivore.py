from __future__ import annotations

import random
from typing import Optional

from grassland.entities.animals.animal import Animal
from grassland.entities.resources.carcass import Carcass
from grassland.geometry import Vec2


class Omnivore(Animal):
    def __init__(
        self,
        name: str,
        position: Vec2,
        color: tuple[int, int, int],
        health: float,
        speed: float,
        power: float,
    ):
        super().__init__(name, position, color, health, speed, power, detect_range=150.0, radius=17)
        self.diet_preference = 0.5
        self.aggression = 0.4

    def behave(self, world: object, dt: float) -> bool:
        threat = world.nearest_predator(self, self.detect_range)
        if threat is not None:
            self.flee_or_fight(threat, world, dt)
            return True
        if self.seek_water_if_needed(world):
            return True
        if self.hunger > 58.0:
            food = self.decide_food(world)
            if food is not None:
                if self.position.distance_to(food.position) <= self.radius + food.radius + 8:
                    self.eat(food)
                    self.stop()
                else:
                    self.move_toward(food.position, self.speed * 0.75)
                    self.action_text = "forage"
                return True
        return False

    def forage(self, world: object) -> Optional[object]:
        return self.decide_food(world)

    def decide_food(self, world: object) -> Optional[object]:
        if random.random() < self.diet_preference:
            return world.nearest_carcass(self.position)
        return world.nearest_plant(self.position)

    def eat(self, other: object) -> None:
        if isinstance(other, Carcass):
            other.reduce_hunger(self)
        else:
            super().eat(other)

    def flee_or_fight(self, threat: Animal, world: object, dt: float) -> None:
        if random.random() < self.aggression and self.position.distance_to(threat.position) < 42:
            self.attack(threat, world)
        else:
            self.move_away_from(threat.position, self.speed * 1.15)
            self.action_text = "flee"
        self.lose_energy(6.0 * dt)
