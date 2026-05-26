from __future__ import annotations

from grassland.entities.plants.plant import Plant
from grassland.geometry import Vec2


class Grass(Plant):
    def __init__(self, position: Vec2):
        super().__init__("Grass", position, health=55.0, color=(83, 174, 80))
        self.growth_rate = 2.2
        self.radius = 16

    def update(self, world: object, dt: float) -> None:
        if self.alive and world.environment.weather == "rain":
            self.health = min(70.0, self.health + self.growth_rate * dt)

    def spread_seeds(self) -> None:
        self.reproduce()
