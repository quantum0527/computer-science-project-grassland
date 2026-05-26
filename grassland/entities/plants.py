from __future__ import annotations

from grassland.entities.base import Entity
from grassland.geometry import Vec2


class Plant(Entity):
    def __init__(self, name: str, position: Vec2, health: float, color: tuple[int, int, int]):
        super().__init__(name=name, position=position, radius=20, color=color)
        self.health = health
        self.photosynthesis = 1.0
        self.spread = 0.0
        self.kind = "plant"

    def reproduce(self) -> None:
        self.spread += 1.0

    def consume(self, amount: float) -> float:
        eaten = min(self.health, amount)
        self.health -= eaten
        if self.health <= 0:
            self.die()
        return eaten

    def die(self) -> None:
        self.alive = False
        self.solid = False


class Grass(Plant):
    def __init__(self, position: Vec2):
        super().__init__("Grass", position, health=55.0, color=(83, 174, 80))
        self.growth_rate = 2.2
        self.radius = 16

    def update(self, world: object, dt: float) -> None:
        if self.alive and world.environment.weather == "rain":
            self.health = min(70.0, self.health + self.growth_rate * dt)

    def spread_seeds(self) -> None:
        self.reproduce()


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


class BaobabTree(Plant):
    def __init__(self, position: Vec2):
        super().__init__("Baobab_Tree", position, health=180.0, color=(151, 120, 72))
        self.stored_water = 80.0
        self.radius = 42

    def provide_shade(self, animal: object) -> None:
        animal.stress = max(0.0, animal.stress - 2.0)

