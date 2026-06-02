from __future__ import annotations

from typing import Optional

from grassland.entities.animals.animal import Animal
from grassland.entities.resources.carcass import Carcass
from grassland.geometry import Vec2


class Carnivore(Animal):
    def __init__(
        self,
        name: str,
        position: Vec2,
        color: tuple[int, int, int],
        health: float = 100.0,
        speed: float = 78.0,
        power: float = 18.0,
        detect_range: float = 230.0,
    ):
        super().__init__(name, position, color, health, speed, power, detect_range, radius=20)
        self.stealth = 0.18
        self.acceleration = 34.0
        self.hunt_stamina_cost = 10.0

    def eat(self, food: object) -> None:
        if isinstance(food, Carcass):
            food.reduce_hunger(self)
        else:
            super().eat(food)

    def hunt(self, prey: Animal, world: object, dt: float) -> None:
        if self.stamina <= 8.0:
            self.rest()
            return
        distance = self.position.distance_to(prey.position)
        if distance <= self.radius + prey.radius + 8:
            self.attack(prey, world)
            self.lose_energy(self.hunt_stamina_cost * dt)
            return
        self.move_toward(prey.position, self.speed + self.acceleration)
        self.lose_energy(self.hunt_stamina_cost * dt)
        self.action_text = "hunt"

    def hide(self) -> None:
        self.is_hidden = True
        self.action_text = "hide"

    def rest(self) -> None:
        self.stop()
        self.recover_stamina(0.8)
        self.action_text = "rest"

    def detect(self, target: Animal) -> bool:
        if getattr(target, "is_hidden", False):
            return self.position.distance_to(target.position) < self.detect_range * (1.0 - self.stealth)
        return self.position.distance_to(target.position) <= self.detect_range

    def find_prey(self, world: object) -> Optional[Animal]:
        return world.nearest_prey_for(self, self.detect_range)
