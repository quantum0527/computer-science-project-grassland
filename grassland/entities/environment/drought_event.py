from __future__ import annotations


class DroughtEvent:
    def __init__(self, drought_intensity: float):
        self.drought_intensity = drought_intensity

    def dry_up_map(self, world: object, dt: float) -> None:
        for water in world.water_puddles():
            water.consume(dt * self.drought_intensity * 3.0)

    def accelerate_thirst(self, animal: object, dt: float) -> None:
        animal.thirst = min(100.0, animal.thirst + dt * self.drought_intensity * 0.35)

