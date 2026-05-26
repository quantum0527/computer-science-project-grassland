from __future__ import annotations

import random

from grassland.entities.animals.omnivores.omnivore import Omnivore
from grassland.entities.terrain.cave import Cave
from grassland.geometry import Vec2


class Meerkat(Omnivore):
    def __init__(self, position: Vec2):
        super().__init__("Meerkat", position, color=(192, 154, 96), health=45, speed=72, power=4)
        self.is_sentinel = False
        self.sentinel_height = 22.0
        self.radius = 14
        self.diet_preference = 0.25
        self.aggression = 0.15

    def behave(self, world: object, dt: float) -> bool:
        threat = world.nearest_predator(self, self.detect_range)
        if threat is not None:
            cave = world.nearest_terrain_type(Cave, self.position)
            if cave is not None:
                self.move_toward(cave.position, self.speed)
                if cave.contains(self):
                    cave.owner = self
                    cave.hide_entity(self)
                return True
        if random.random() < 0.01:
            self.stand()
            return True
        return super().behave(world, dt)

    def stand(self) -> None:
        self.is_sentinel = True
        self.stop()
        self.action_text = "sentinel"
