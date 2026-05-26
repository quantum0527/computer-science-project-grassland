from __future__ import annotations

import random
from typing import Optional

from grassland.entities.base import Entity
from grassland.geometry import Vec2, random_unit_vector


class Animal(Entity):
    def __init__(
        self,
        name: str,
        position: Vec2,
        color: tuple[int, int, int],
        health: float,
        speed: float,
        power: float,
        detect_range: float,
        radius: float = 18,
    ):
        super().__init__(name=name, position=position, radius=radius, color=color)
        self.health = health
        self.max_health = health
        self.speed = speed
        self.power = power
        self.hunger = random.uniform(12.0, 42.0)
        self.thirst = random.uniform(12.0, 42.0)
        self.is_sleeping = False
        self.stamina = 100.0
        self.stamina_recovery_rate = 7.0
        self.stress = 0.0
        self.detect_range = detect_range
        self.is_hidden = False
        self.age = 0.0
        self.kind = "animal"
        self.decision_timer = random.uniform(0.2, 1.4)
        self._carcass_spawned = False

    def update(self, world: object, dt: float) -> None:
        if not self.alive:
            return
        self.is_hidden = False
        self.tick_body(world, dt)
        if not self.alive:
            return
        self.recover_stamina(dt)
        if self.is_sleeping:
            self.velocity = self.velocity * 0.3
            return
        if not self.behave(world, dt):
            self.wander(dt)

    def tick_body(self, world: object, dt: float) -> None:
        self.age += dt
        self.hunger = min(100.0, self.hunger + dt * 0.18)
        self.thirst = min(100.0, self.thirst + dt * 0.25)
        if world.environment.weather == "drought" and world.drought_event is not None:
            world.drought_event.accelerate_thirst(self, dt)
        if self.hunger >= 100.0 or self.thirst >= 100.0 or self.health <= 0:
            self.die(world)

    def behave(self, world: object, dt: float) -> bool:
        return self.seek_water_if_needed(world) or self.seek_plants_if_needed(world)

    def move(self, direction: Vec2) -> None:
        self.velocity = direction.normalized() * self.speed

    def eat(self, food: object) -> None:
        if hasattr(food, "consume"):
            eaten = food.consume(14)
            self.hunger = max(0.0, self.hunger - eaten)
            self.action_text = "eat"

    def drink(self, source: object) -> None:
        if hasattr(source, "reduce_thirst"):
            source.reduce_thirst(self)
        elif hasattr(source, "enable_drinking"):
            source.enable_drinking(self)

    def sleep(self) -> None:
        self.is_sleeping = True
        self.action_text = "sleep"

    def wake_up(self) -> None:
        self.is_sleeping = False

    def lose_energy(self, amount: float) -> None:
        self.stamina = max(0.0, self.stamina - amount)

    def die(self, world: Optional[object] = None) -> None:
        if not self.alive:
            return
        self.alive = False
        self.solid = False
        self.stop()
        self.action_text = "dead"
        if world is not None and not self._carcass_spawned:
            self._carcass_spawned = True
            world.spawn_carcass(self)

    def attack(self, target: object, world: object) -> None:
        if not getattr(target, "alive", False):
            return
        target.health -= self.power
        target.stress = min(100.0, target.stress + 8.0)
        self.action_text = "attack"
        if target.health <= 0:
            target.die(world)

    def couple(self, one: object, other: object) -> bool:
        return getattr(one, "alive", False) and getattr(other, "alive", False)

    def recover_stamina(self, dt: float) -> None:
        self.stamina = min(100.0, self.stamina + self.stamina_recovery_rate * dt)

    def distant_to(self, target: object) -> float:
        return self.distance_to(target)

    def seek_water_if_needed(self, world: object) -> bool:
        if self.thirst < 58.0:
            return False
        water = world.nearest_water(self.position)
        if water is None:
            return False
        if self.position.distance_to(water.position) <= self.radius + water.radius + 8:
            self.drink(water)
            self.stop()
        else:
            self.move_toward(water.position, self.speed * 0.85)
            self.action_text = "water"
        return True

    def seek_plants_if_needed(self, world: object) -> bool:
        if self.hunger < 62.0:
            return False
        plant = world.nearest_plant(self.position)
        if plant is None:
            return False
        if self.position.distance_to(plant.position) <= self.radius + plant.radius + 8:
            self.eat(plant)
            self.stop()
        else:
            self.move_toward(plant.position, self.speed * 0.7)
            self.action_text = "forage"
        return True

    def wander(self, dt: float) -> None:
        self.decision_timer -= dt
        if self.decision_timer > 0:
            return
        self.decision_timer = random.uniform(0.8, 2.2)
        if random.random() < 0.22:
            self.stop()
            self.action_text = "watch"
            return
        self.velocity = random_unit_vector() * random.uniform(self.speed * 0.18, self.speed * 0.45)
        self.action_text = "move"

