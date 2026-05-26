from __future__ import annotations

from grassland.entities.base import Entity
from grassland.geometry import Vec2


class Plant(Entity):
    def __init__(self, name: str, position: Vec2, health: float, color: tuple[int, int, int]):
        super().__init__(name=name, position=position, radius=20, color=color)
        self.health = health
        self.photosynthesis = 1.0
        self.spread = 0.0
        self.kind = "plant"

    def reproduce(self) -> None:
        self.spread += 1.0

    def consume(self, amount: float) -> float:
        eaten = min(self.health, amount)
        self.health -= eaten
        if self.health <= 0:
            self.die()
        return eaten

    def die(self) -> None:
        self.alive = False
        self.solid = False

