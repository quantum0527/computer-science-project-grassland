from __future__ import annotations

import random

from grassland.entities.animals.carnivores.carnivore import Carnivore
from grassland.entities.animals.herbivores.zebra import Zebra
from grassland.geometry import Vec2


class Lion(Carnivore):
    def __init__(self, position: Vec2):
        super().__init__("Lion", position, color=(204, 154, 67), health=125, speed=76, power=21, detect_range=240)
        self.mane_size = 1.0
        self.mane_exist = True
        self.roar_cooldown = random.uniform(4.0, 9.0)

    def behave(self, world: object, dt: float) -> bool:
        self.roar_cooldown -= dt
        if self.roar_cooldown <= 0:
            self.Roar(world)
            self.roar_cooldown = random.uniform(8.0, 16.0)
            return True
        return super().behave(world, dt)

    def Roar(self, world: object) -> None:
        self.action_text = "roar"
        for animal in world.living_animals():
            if isinstance(animal, Zebra) and self.position.distance_to(animal.position) <= 190:
                animal.panic_boost_timer = max(animal.panic_boost_timer, 6.0)
            if animal.name in ("Bald_Eagle", "Hyena") and self.position.distance_to(animal.position) <= 115:
                animal.move_away_from(self.position, animal.speed * 1.2)
                animal.action_text = "pushed"
        for carcass in world.carcasses():
            if self.position.distance_to(carcass.position) <= 120:
                carcass.carried_by = None

    def hide(self) -> None:
        self.is_hidden = True
        self.stealth = 0.35
        self.action_text = "hide"
