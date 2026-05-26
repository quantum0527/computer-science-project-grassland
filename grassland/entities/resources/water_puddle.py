from __future__ import annotations

from grassland.entities.resources.resource import Resource
from grassland.geometry import Vec2


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
