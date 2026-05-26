from __future__ import annotations

from grassland.entities.plants.plant import Plant
from grassland.geometry import Vec2


class BaobabTree(Plant):
    def __init__(self, position: Vec2):
        super().__init__("Baobab_Tree", position, health=180.0, color=(151, 120, 72))
        self.stored_water = 80.0
        self.radius = 42

    def provide_shade(self, animal: object) -> None:
        animal.stress = max(0.0, animal.stress - 2.0)
