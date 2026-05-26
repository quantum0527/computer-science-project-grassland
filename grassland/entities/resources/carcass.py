from __future__ import annotations

from typing import Optional

from grassland.entities.resources.resource import Resource
from grassland.geometry import Vec2


class Carcass(Resource):
    def __init__(self, position: Vec2, source_name: str = "prey"):
        super().__init__("Carcass", position, amount=85.0, color=(118, 72, 44))
        self.decomposition_timer = 80.0
        self.source_name = source_name
        self.carried_by: Optional[object] = None
        self.being_eaten_by: Optional[object] = None
        self.radius = 20

    def update(self, world: object, dt: float) -> None:
        if not self.alive:
            return
        if self.carried_by is not None and getattr(self.carried_by, "alive", False):
            self.position = self.carried_by.position.copy()
        self.decomposition_timer -= dt
        if self.decomposition_timer <= 0:
            self.delete()

    def reduce_hunger(self, animal: object) -> None:
        taken = self.consume(20)
        animal.hunger = max(0.0, animal.hunger - taken)
        animal.action_text = "eat carcass"
        self.being_eaten_by = animal
