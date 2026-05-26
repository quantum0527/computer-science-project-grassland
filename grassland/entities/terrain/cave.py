from __future__ import annotations

from grassland.entities.terrain.terrain_base import Terrain
from grassland.geometry import Vec2


class Cave(Terrain):
    def __init__(self, position: Vec2):
        super().__init__("Cave", position, size=64, color=(82, 75, 67))
        self.camouflage_rate = 0.75
        self.owner = None

    def hide_entity(self, entity: object) -> None:
        entity.is_hidden = True
        entity.stress = max(0.0, entity.stress - self.camouflage_rate)
        entity.action_text = "cave"
