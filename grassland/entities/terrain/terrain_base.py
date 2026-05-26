from __future__ import annotations

from grassland.entities.base import Entity
from grassland.geometry import Vec2


class Terrain(Entity):
    def __init__(self, name: str, position: Vec2, size: float, color: tuple[int, int, int]):
        super().__init__(name=name, position=position, radius=size, color=color)
        self.size = size
        self.kind = "terrain"
        self.solid = False

    def contains(self, entity: Entity) -> bool:
        return self.position.distance_to(entity.position) <= self.size

    def give_effect(self, entity: Entity) -> None:
        return None

