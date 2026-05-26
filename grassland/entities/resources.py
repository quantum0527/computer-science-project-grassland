from __future__ import annotations

from typing import Optional

from grassland.entities.base import Entity
from grassland.geometry import Vec2


class Resource(Entity):
    def __init__(self, name: str, position: Vec2, amount: float, color: tuple[int, int, int]):
        super().__init__(name=name, position=position, radius=18, color=color)
        self.amount = amount
        self.kind = "resource"

    def consume(self, amount: float) -> float:
        taken = min(self.amount, amount)
        self.amount -= taken
        if self.amount <= 0:
            self.delete()
        return taken

    def regenerate(self, amount: float) -> None:
        self.amount = min(100.0, self.amount + amount)
        self.alive = True

    def delete(self) -> None:
        self.alive = False
        self.solid = False


class WaterPuddle(Resource):
    def __init__(self, position: Vec2):
        super().__init__("Water_Puddle", position, amount=100.0, color=(65, 145, 208))
        self.evaporation_rate = 0.9
        self.radius = 28

    def update(self, world: object, dt: float) -> None:
        if not self.alive:
            return
        drought = world.current_drought_intensity()
        self.consume(dt * self.evaporation_rate * drought)

    def reduce_thirst(self, animal: object) -> None:
        taken = self.consume(18)
        animal.thirst = max(0.0, animal.thirst - taken)
        animal.action_text = "drink"

    def fill_rain(self) -> None:
        self.regenerate(35)


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

