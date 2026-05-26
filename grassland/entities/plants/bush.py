from __future__ import annotations

from grassland.entities.plants.plant import Plant
from grassland.geometry import Vec2


class Bush(Plant):
    def __init__(self, position: Vec2):
        super().__init__("Bush", position, health=80.0, color=(47, 119, 67))
        self.current_foliage = 80.0
        self.stealth_factor = 0.65
        self.radius = 30

    def hide_entity(self, entity: object) -> None:
        entity.is_hidden = True
        entity.stress = max(0.0, entity.stress - self.stealth_factor)
        entity.action_text = "hide"

    def consume(self, amount: float) -> float:
        eaten = super().consume(amount)
        self.current_foliage = max(0.0, self.current_foliage - eaten)
        return eaten
