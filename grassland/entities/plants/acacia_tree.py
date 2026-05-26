from __future__ import annotations

from grassland.entities.plants.plant import Plant
from grassland.geometry import Vec2


class AcaciaTree(Plant):
    def __init__(self, position: Vec2):
        super().__init__("Acacia_Tree", position, health=130.0, color=(97, 142, 63))
        self.thorn_damage = 4.0
        self.leaf_amount = 90.0
        self.max_leaf = 100.0
        self.radius = 34

    def produce_leaves(self) -> None:
        self.leaf_amount = min(self.max_leaf, self.leaf_amount + 8)
        self.health = min(140.0, self.health + 5)
