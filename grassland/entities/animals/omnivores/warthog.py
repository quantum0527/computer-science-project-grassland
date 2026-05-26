from __future__ import annotations

from typing import Optional

from grassland.entities.animals.omnivores.omnivore import Omnivore
from grassland.entities.terrain.cave import Cave
from grassland.geometry import Vec2


class Warthog(Omnivore):
    def __init__(self, position: Vec2):
        super().__init__("Warthog", position, color=(142, 100, 74), health=82, speed=68, power=11)
        self.tusk_power = 14.0
        self.burrow_location: Optional[Vec2] = None
        self.diet_preference = 0.35
        self.aggression = 0.45
        self.radius = 18

    def behave(self, world: object, dt: float) -> bool:
        threat = world.nearest_predator(self, self.detect_range)
        if threat is not None:
            cave = world.nearest_terrain_type(Cave, self.position)
            if cave is not None:
                self.burrow_location = cave.position.copy()
                self.move_toward(cave.position, self.speed * 1.05)
                if cave.contains(self):
                    self.burrow(cave, world)
                return True
        return super().behave(world, dt)

    def dig(self) -> None:
        self.action_text = "dig"

    def burrow(self, cave: Cave, world: object) -> None:
        cave.owner = self
        cave.hide_entity(self)
        world.expel_meerkats_from_cave(cave)
        self.action_text = "burrow"
