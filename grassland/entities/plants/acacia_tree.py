from __future__ import annotations

from grassland.entities.plants.plant import Plant
from grassland.geometry import Vec2


class AcaciaTree(Plant):
    """
    가시가 있는 아카시아 나무. 잎을 재생산하며 천천히 체력을 회복.

    속성:
        thorn_damage: 이 나무를 섭취하는 동물에게 가시로 입히는 피해량.
        leaf_amount : 현재 잎 양.
        max_leaf    : 잎 최대량.
    """

    def __init__(self, position: Vec2):
        super().__init__(
            name="Acacia_Tree",
            position=position,
            health=130.0,
            max_health=150.0,
            color=(97, 142, 63),
            photosynthesis=0.4,
        )
        self.thorn_damage = 4.0  # 섭취하는 동물에게 가하는 가시 피해
        self.leaf_amount = 90.0
        self.max_leaf = 100.0
        self.radius = 34

    def produce_leaves(self) -> None:
        """잎을 재생산하고 체력을 소량 회복."""
        self.leaf_amount = min(self.max_leaf, self.leaf_amount + 8)
        self.health = min(self.max_health, self.health + 5)
