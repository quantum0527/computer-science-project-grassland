from __future__ import annotations

import random
from typing import Callable, Iterable, List, Optional, Type

from grassland.config import WORLD_HEIGHT, WORLD_WIDTH
from grassland.entities.environment import DroughtEvent, Environment
from grassland.entities.plants import AcaciaTree, BaobabTree, Bush, Grass, Plant
from grassland.entities.resources import Carcass, WaterPuddle
from grassland.entities.terrain import Cave, LakeSide, Plain, Terrain
from grassland.geometry import Vec2
from grassland.physics import PhysicsEngine


class World:
    def __init__(self, width: int = WORLD_WIDTH, height: int = WORLD_HEIGHT):
        self.width = width
        self.height = height
        self.environment = Environment()
        self.physics = PhysicsEngine(width, height)
        self.elapsed = 0.0
        self.animals: List[object] = []
        self.plants: List[Plant] = []
        self.resources: List[object] = []
        self.terrains: List[Terrain] = []
        self.drought_event: Optional[DroughtEvent] = None

    @classmethod
    def seed_default(cls) -> "World":
        world = cls()
        world.terrains.extend(
            [
                Plain(world.width, world.height),
                LakeSide(Vec2(310, 260)),
                Cave(Vec2(1470, 890)),
            ]
        )
        world.plants.extend(
            [
                Grass(Vec2(520, 300)),
                Grass(Vec2(780, 360)),
                Grass(Vec2(1080, 460)),
                Grass(Vec2(1350, 700)),
                Grass(Vec2(620, 900)),
                Bush(Vec2(900, 260)),
                Bush(Vec2(1160, 760)),
                Bush(Vec2(420, 820)),
                AcaciaTree(Vec2(760, 660)),
                AcaciaTree(Vec2(1230, 360)),
                BaobabTree(Vec2(1010, 930)),
            ]
        )
        world.resources.extend(
            [
                WaterPuddle(Vec2(410, 360)),
                WaterPuddle(Vec2(1330, 980)),
                Carcass(Vec2(1120, 540), source_name="initial"),
            ]
        )
        return world

    def update(self, dt: float) -> None:
        if self.environment.ended:
            return
        self.elapsed += dt
        new_day = self.environment.update(dt)
        if new_day:
            self.on_new_day()

        if self.environment.weather == "drought":
            if self.drought_event is None:
                self.drought_event = DroughtEvent(random.uniform(0.5, 1.0))
            self.drought_event.dry_up_map(self, dt)
        else:
            self.drought_event = None

        for plant in self.plants:
            plant.update(self, dt)
        for animal in self.animals:
            if hasattr(animal, "update"):
                animal.update(self, dt)

        self.physics.update(self.living_animals(), dt)

        for resource in self.resources:
            resource.update(self, dt)

        self.check_end_conditions()

    def on_new_day(self) -> None:
        if self.environment.weather == "rain":
            for water in self.water_puddles():
                water.fill_rain()
            for plant in self.plants:
                if hasattr(plant, "produce_leaves"):
                    plant.produce_leaves()
        if self.environment.weather == "drought":
            self.drought_event = DroughtEvent(random.uniform(0.55, 1.0))

    def check_end_conditions(self) -> None:
        if self.environment.weather == "drought" and self.environment.day >= 3:
            water_left = sum(water.amount for water in self.water_puddles() if water.alive)
            if water_left <= 2:
                self.environment.ended = True
                self.environment.end_reason = "가뭄으로 물이 말라 생태계가 종료되었습니다."

    def spawn_carcass(self, animal: object) -> None:
        name = getattr(animal, "name", "animal")
        position = getattr(animal, "position", Vec2(self.width / 2, self.height / 2))
        self.resources.append(Carcass(position.copy(), source_name=name))

    def living_animals(self) -> List[object]:
        return [animal for animal in self.animals if getattr(animal, "alive", True)]

    def alive_plants(self) -> List[Plant]:
        return [plant for plant in self.plants if plant.alive]

    def water_puddles(self) -> List[WaterPuddle]:
        return [resource for resource in self.resources if isinstance(resource, WaterPuddle) and resource.alive]

    def carcasses(self) -> List[Carcass]:
        return [resource for resource in self.resources if isinstance(resource, Carcass) and resource.alive]

    def nearest_alive(
        self,
        items: Iterable[object],
        position: Vec2,
        predicate: Optional[Callable[[object], bool]] = None,
        max_distance: Optional[float] = None,
    ) -> Optional[object]:
        nearest = None
        best_distance = float("inf")
        for item in items:
            if not getattr(item, "alive", True):
                continue
            if predicate is not None and not predicate(item):
                continue
            distance = position.distance_to(item.position)
            if max_distance is not None and distance > max_distance:
                continue
            if distance < best_distance:
                best_distance = distance
                nearest = item
        return nearest

    def nearest_plant(self, position: Vec2) -> Optional[Plant]:
        return self.nearest_alive(self.plants, position)

    def nearest_bush(self, position: Vec2, max_distance: float) -> Optional[Bush]:
        result = self.nearest_alive(self.plants, position, lambda item: isinstance(item, Bush), max_distance)
        return result

    def nearest_carcass(self, position: Vec2) -> Optional[Carcass]:
        return self.nearest_alive(self.carcasses(), position, lambda item: item.carried_by is None)

    def nearest_water(self, position: Vec2) -> Optional[object]:
        water_items = self.water_puddles() + [terrain for terrain in self.terrains if isinstance(terrain, LakeSide)]
        return self.nearest_alive(water_items, position)

    def nearest_predator(self, animal: object, max_distance: float) -> Optional[object]:
        def is_threat(item: object) -> bool:
            role = getattr(item, "role", getattr(item, "diet_type", ""))
            return (
                item is not animal
                and role == "carnivore"
                and getattr(item, "alive", True)
                and getattr(item, "threatens_herbivores", True)
            )

        return self.nearest_alive(self.animals, animal.position, is_threat, max_distance)

    def nearest_prey_for(self, predator: object, max_distance: float) -> Optional[object]:
        def is_prey(item: object) -> bool:
            role = getattr(item, "role", getattr(item, "diet_type", ""))
            if item is predator or role not in ("herbivore", "omnivore"):
                return False
            if getattr(item, "is_hidden", False):
                if hasattr(predator, "detect"):
                    return predator.detect(item)
                return False
            return True

        return self.nearest_alive(self.animals, predator.position, is_prey, max_distance)

    def nearest_named(self, name: str, position: Vec2, max_distance: float) -> Optional[object]:
        return self.nearest_alive(self.animals, position, lambda item: getattr(item, "name", "") == name, max_distance)

    def nearest_terrain_type(self, terrain_type: Type[Terrain], position: Vec2) -> Optional[Terrain]:
        return self.nearest_alive(self.terrains, position, lambda item: isinstance(item, terrain_type))

    def carcass_eaten_by_lion_near(self, position: Vec2, max_distance: float) -> Optional[Carcass]:
        def matches(carcass: Carcass) -> bool:
            eater = carcass.being_eaten_by
            return eater is not None and getattr(eater, "name", "") == "Lion"

        return self.nearest_alive(self.carcasses(), position, matches, max_distance)

    def expel_meerkats_from_cave(self, cave: Cave) -> None:
        for animal in self.living_animals():
            if getattr(animal, "name", "") == "Meerkat" and cave.contains(animal):
                if hasattr(animal, "move_away_from"):
                    animal.move_away_from(cave.position, animal.speed * 1.3)
                animal.action_text = "expelled"
                animal.is_hidden = False

    def current_drought_intensity(self) -> float:
        if self.environment.weather != "drought" or self.drought_event is None:
            return 0.0
        return self.drought_event.drought_intensity

    def counts_by_name(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for animal in self.living_animals():
            counts[animal.name] = counts.get(animal.name, 0) + 1
        return counts
