from __future__ import annotations

import random
from typing import Optional

from grassland.entities.animals.carnivores.carnivore import Carnivore
from grassland.entities.resources.carcass import Carcass
from grassland.geometry import Vec2


class Hyena(Carnivore):
    def __init__(self, position: Vec2):
        super().__init__("Hyena", position, color=(128, 118, 83), health=88, speed=82, power=13, detect_range=215)
        self.steal_prey_chance = 0.25
        self.stolen_prey: Optional[Carcass] = None
        self.steal_pray_cooltime = 0.0

    def behave(self, world: object, dt: float) -> bool:
        self.steal_pray_cooltime = max(0.0, self.steal_pray_cooltime - dt)
        lion = world.nearest_named("Lion", self.position, 130.0)
        if lion is not None and self.stolen_prey is not None and lion.action_text == "roar":
            self.stolen_prey.carried_by = None
            self.stolen_prey = None
            self.move_away_from(lion.position, self.speed * 1.3)
            self.action_text = "drop"
            return True
        if self.stolen_prey is not None:
            return self.stolen_prey_eat(world)
        if self.steal_pray_cooltime <= 0:
            carcass = world.carcass_eaten_by_lion_near(self.position, 150.0)
            if carcass is not None:
                return self.steal_prey(carcass)
        return super().behave(world, dt)

    def steal_prey(self, carcass: Carcass) -> bool:
        chance = self.steal_prey_chance + (self.health / self.max_health) * 0.25
        if random.random() <= chance:
            self.stolen_prey = carcass
            carcass.carried_by = self
            carcass.being_eaten_by = None
            self.steal_pray_cooltime = 8.0
            self.action_text = "steal"
            return True
        self.steal_pray_cooltime = 5.0
        return False

    def stolen_prey_eat(self, world: object) -> bool:
        predator = world.nearest_predator(self, 130.0)
        if predator is not None and predator is not self:
            self.move_away_from(predator.position, self.speed)
            self.action_text = "carry"
            return True
        if self.stolen_prey is not None:
            self.stolen_prey.reduce_hunger(self)
            if not self.stolen_prey.alive:
                self.stolen_prey = None
            return True
        return False
