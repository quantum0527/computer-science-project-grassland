from __future__ import annotations

from grassland.entities.base import Entity
from grassland.entities.terrain.terrain_base import Terrain
from grassland.geometry import Vec2


class Plain(Terrain):
    def __init__(self, width: int, height: int):
        super().__init__("Plain", Vec2(width / 2, height / 2), size=max(width, height), color=(126, 184, 92))
        self.width = width
        self.height = height
        self.movement_cost = 1.0

    def contains(self, entity: Entity) -> bool:
        return 0 <= entity.position.x <= self.width and 0 <= entity.position.y <= self.height

    def speed_modifier(self) -> float:
        return 1.0 / self.movement_cost
