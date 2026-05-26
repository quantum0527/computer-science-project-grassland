from __future__ import annotations

from grassland.entities.terrain.terrain_base import Terrain
from grassland.geometry import Vec2


class LakeSide(Terrain):
    def __init__(self, position: Vec2):
        super().__init__("Lake_Side", position, size=82, color=(79, 156, 201))
        self.water_amount = 100.0

    def enable_drinking(self, animal: object) -> None:
        animal.thirst = max(0.0, animal.thirst - 18.0)
        animal.action_text = "drink"
