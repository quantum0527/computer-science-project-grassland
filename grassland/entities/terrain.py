from __future__ import annotations

from grassland.entities.base import Entity
from grassland.geometry import Vec2


class Terrain(Entity):
    def __init__(self, name: str, position: Vec2, size: float, color: tuple[int, int, int]):
        super().__init__(name=name, position=position, radius=size, color=color)
        self.size = size
        self.kind = "terrain"
        self.solid = False

    def contains(self, entity: Entity) -> bool:
        return self.position.distance_to(entity.position) <= self.size

    def give_effect(self, entity: Entity) -> None:
        return None


class Plain(Terrain):
    def __init__(self, width: int, height: int):
        super().__init__("Plain", Vec2(width / 2, height / 2), size=max(width, height), color=(126, 184, 92))
        self.width = width
        self.height = height
        self.movement_cost = 1.0

    def contains(self, entity: Entity) -> bool:
        return 0 <= entity.position.x <= self.width and 0 <= entity.position.y <= self.height

    def speed_modifier(self) -> float:
        return 1.0 / self.movement_cost


class LakeSide(Terrain):
    def __init__(self, position: Vec2):
        super().__init__("Lake_Side", position, size=82, color=(79, 156, 201))
        self.water_amount = 100.0

    def enable_drinking(self, animal: object) -> None:
        animal.thirst = max(0.0, animal.thirst - 18.0)
        animal.action_text = "drink"


class Cave(Terrain):
    def __init__(self, position: Vec2):
        super().__init__("Cave", position, size=64, color=(82, 75, 67))
        self.camouflage_rate = 0.75
        self.owner = None

    def hide_entity(self, entity: object) -> None:
        entity.is_hidden = True
        entity.stress = max(0.0, entity.stress - self.camouflage_rate)
        entity.action_text = "cave"

