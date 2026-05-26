from __future__ import annotations

import math
import random
from typing import Optional

from grassland.entities.base import Entity
from grassland.entities.plants import AcaciaTree, Bush, Plant
from grassland.entities.resources import Carcass
from grassland.entities.terrain import Cave
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


class Carnivore(Animal):
    threatens_herbivores = True

    def __init__(
        self,
        name: str,
        position: Vec2,
        color: tuple[int, int, int],
        health: float = 100.0,
        speed: float = 78.0,
        power: float = 18.0,
        detect_range: float = 230.0,
    ):
        super().__init__(name, position, color, health, speed, power, detect_range, radius=20)
        self.stealth = 0.18
        self.acceleration = 34.0
        self.hunt_stamina_cost = 10.0

    def behave(self, world: object, dt: float) -> bool:
        if self.seek_water_if_needed(world):
            return True
        if self.hunger > 48.0:
            carcass = world.nearest_carcass(self.position)
            if carcass is not None:
                if self.position.distance_to(carcass.position) <= self.radius + carcass.radius + 10:
                    self.eat(carcass)
                    return True
                self.move_toward(carcass.position, self.speed * 0.75)
                self.action_text = "carcass"
                return True
            prey = self.find_prey(world)
            if prey is not None:
                self.hunt(prey, world, dt)
                return True
        return False

    def eat(self, food: object) -> None:
        if isinstance(food, Carcass):
            food.reduce_hunger(self)
        else:
            super().eat(food)

    def hunt(self, prey: Animal, world: object, dt: float) -> None:
        if self.stamina <= 8.0:
            self.rest()
            return
        distance = self.position.distance_to(prey.position)
        if distance <= self.radius + prey.radius + 8:
            self.attack(prey, world)
            self.lose_energy(self.hunt_stamina_cost * dt)
            return
        self.move_toward(prey.position, self.speed + self.acceleration)
        self.lose_energy(self.hunt_stamina_cost * dt)
        self.action_text = "hunt"

    def hide(self) -> None:
        self.is_hidden = True
        self.action_text = "hide"

    def rest(self) -> None:
        self.stop()
        self.recover_stamina(0.8)
        self.action_text = "rest"

    def detect(self, target: Animal) -> bool:
        if getattr(target, "is_hidden", False):
            return self.position.distance_to(target.position) < self.detect_range * (1.0 - self.stealth)
        return self.position.distance_to(target.position) <= self.detect_range

    def find_prey(self, world: object) -> Optional[Animal]:
        return world.nearest_prey_for(self, self.detect_range)


class Herbivore(Animal):
    def __init__(
        self,
        name: str,
        position: Vec2,
        color: tuple[int, int, int],
        health: float,
        speed: float,
        power: float,
        detect_range: float = 160.0,
    ):
        super().__init__(name, position, color, health, speed, power, detect_range)
        self.flee_speed = speed * 1.25
        self.panic_range = detect_range
        self.base_panic_range = detect_range
        self.is_chased = False
        self.panic_boost_timer = 0.0

    def update(self, world: object, dt: float) -> None:
        if self.panic_boost_timer > 0:
            self.panic_boost_timer = max(0.0, self.panic_boost_timer - dt)
            self.panic_range = self.base_panic_range * 2.0
            self.stamina_recovery_rate = 3.5
        else:
            self.panic_range = self.base_panic_range
            self.stamina_recovery_rate = 7.0
        super().update(world, dt)

    def behave(self, world: object, dt: float) -> bool:
        threat = world.nearest_predator(self, self.panic_range)
        self.is_chased = threat is not None
        if threat is not None:
            bush = world.nearest_bush(self.position, 95.0)
            if bush is not None and self.can_hide_in_bush():
                self.move_toward(bush.position, self.flee_speed)
                if self.position.distance_to(bush.position) < bush.radius + self.radius:
                    bush.hide_entity(self)
                return True
            self.fight_or_flight(threat, world, dt)
            return True
        return self.seek_water_if_needed(world) or self.seek_plants_if_needed(world)

    def can_hide_in_bush(self) -> bool:
        return False

    def heal(self) -> None:
        self.health = min(self.max_health, self.health + 3.0)

    def fight_or_flight(self, threat: Animal, world: object, dt: float) -> None:
        self.move_away_from(threat.position, self.flee_speed)
        self.lose_energy(8.0 * dt)
        self.action_text = "flee"


class Omnivore(Animal):
    def __init__(
        self,
        name: str,
        position: Vec2,
        color: tuple[int, int, int],
        health: float,
        speed: float,
        power: float,
    ):
        super().__init__(name, position, color, health, speed, power, detect_range=150.0, radius=17)
        self.diet_preference = 0.5
        self.aggression = 0.4

    def behave(self, world: object, dt: float) -> bool:
        threat = world.nearest_predator(self, self.detect_range)
        if threat is not None:
            self.flee_or_fight(threat, world, dt)
            return True
        if self.seek_water_if_needed(world):
            return True
        if self.hunger > 58.0:
            food = self.decide_food(world)
            if food is not None:
                if self.position.distance_to(food.position) <= self.radius + food.radius + 8:
                    self.eat(food)
                    self.stop()
                else:
                    self.move_toward(food.position, self.speed * 0.75)
                    self.action_text = "forage"
                return True
        return False

    def forage(self, world: object) -> Optional[object]:
        return self.decide_food(world)

    def decide_food(self, world: object) -> Optional[object]:
        if random.random() < self.diet_preference:
            return world.nearest_carcass(self.position)
        return world.nearest_plant(self.position)

    def eat(self, other: object) -> None:
        if isinstance(other, Carcass):
            other.reduce_hunger(self)
        else:
            super().eat(other)

    def flee_or_fight(self, threat: Animal, world: object, dt: float) -> None:
        if random.random() < self.aggression and self.position.distance_to(threat.position) < 42:
            self.attack(threat, world)
        else:
            self.move_away_from(threat.position, self.speed * 1.15)
            self.action_text = "flee"
        self.lose_energy(6.0 * dt)


class BaldEagle(Carnivore):
    threatens_herbivores = False

    def __init__(self, position: Vec2):
        super().__init__("Bald_Eagle", position, color=(205, 205, 205), health=70, speed=92, power=6, detect_range=280)
        self.is_flying = True
        self.fly_speed = 120.0
        self.fly_time = 0.0
        self.z = 35.0
        self.radius = 17

    def behave(self, world: object, dt: float) -> bool:
        carcass = world.nearest_carcass(self.position)
        if carcass is None:
            self.fly(dt)
            return False
        nearby_lion = world.nearest_named("Lion", carcass.position, 110.0)
        if nearby_lion is not None:
            self.fly(dt)
            self.move_away_from(nearby_lion.position, self.fly_speed)
            self.action_text = "wait"
            return True
        if self.position.distance_to(carcass.position) <= self.radius + carcass.radius + 8:
            self.land()
            self.eat_carcass(carcass)
        else:
            self.fly(dt)
            self.move_toward(carcass.position, self.fly_speed)
            self.action_text = "carcass"
        return True

    def fly(self, dt: float) -> None:
        self.is_flying = True
        self.fly_time += dt
        self.z = 35.0 + math.sin(self.fly_time * 4.0) * 6.0

    def land(self) -> None:
        self.is_flying = False
        self.z = 0.0

    def eat_carcass(self, other: Carcass) -> None:
        other.reduce_hunger(self)


class Zebra(Herbivore):
    def __init__(self, position: Vec2):
        super().__init__("Zebra", position, color=(245, 245, 235), health=95, speed=76, power=13, detect_range=170)
        self.kick_power = 15.0
        self.alert_radius = 150.0

    def fight_or_flight(self, threat: Animal, world: object, dt: float) -> None:
        if self.position.distance_to(threat.position) < 36 and self.stamina > 35:
            self.kick(threat, world)
        else:
            self.flee(threat, dt)
            self.alert_herd(world)

    def kick(self, threat: Animal, world: object) -> None:
        threat.health -= self.kick_power
        self.action_text = "kick"
        if threat.health <= 0:
            threat.die(world)

    def flee(self, threat: Animal, dt: float) -> None:
        self.move_away_from(threat.position, self.flee_speed)
        self.lose_energy(7.0 * dt)
        self.action_text = "flee"

    def alert_herd(self, world: object) -> None:
        for animal in world.living_animals():
            if isinstance(animal, Zebra) and self.position.distance_to(animal.position) <= self.alert_radius:
                animal.panic_boost_timer = max(animal.panic_boost_timer, 3.0)


class Gazelle(Herbivore):
    def __init__(self, position: Vec2):
        super().__init__("Gazelle", position, color=(214, 162, 91), health=60, speed=96, power=0, detect_range=185)
        self.endurance = 0.62
        self.zigzag_angle = 0.9

    def can_hide_in_bush(self) -> bool:
        return True

    def fight_or_flight(self, threat: Animal, world: object, dt: float) -> None:
        self.zigzag(threat, world.elapsed)
        self.lose_energy(5.0 * self.endurance * dt)
        self.action_text = "zigzag"

    def zigzag(self, threat: Animal, elapsed: float) -> None:
        away = (self.position - threat.position).normalized()
        side = Vec2(-away.y, away.x) * math.sin(elapsed * 7.0) * self.zigzag_angle
        self.velocity = (away + side).normalized() * self.flee_speed


class Elephant(Herbivore):
    def __init__(self, position: Vec2):
        super().__init__("Elephant", position, color=(142, 145, 141), health=180, speed=48, power=22, detect_range=160)
        self.size_factor = 2.4
        self.intimidation = 0.78
        self.radius = 30

    def fight_or_flight(self, threat: Animal, world: object, dt: float) -> None:
        if threat.name == "Lion":
            self.stomp(threat, world)
        else:
            self.move_away_from(threat.position, self.speed)
            self.action_text = "move"

    def stomp(self, threat: Animal, world: object) -> None:
        threat.health -= self.power * 0.35
        threat.move_away_from(self.position, threat.speed * 1.6)
        self.action_text = "stomp"
        if random.random() < self.intimidation:
            threat.action_text = "pushed"
        if threat.health <= 0:
            threat.die(world)


class Meerkat(Omnivore):
    def __init__(self, position: Vec2):
        super().__init__("Meerkat", position, color=(192, 154, 96), health=45, speed=72, power=4)
        self.is_sentinel = False
        self.sentinel_height = 22.0
        self.radius = 14
        self.diet_preference = 0.25
        self.aggression = 0.15

    def behave(self, world: object, dt: float) -> bool:
        threat = world.nearest_predator(self, self.detect_range)
        if threat is not None:
            cave = world.nearest_terrain_type(Cave, self.position)
            if cave is not None:
                self.move_toward(cave.position, self.speed)
                if cave.contains(self):
                    cave.owner = self
                    cave.hide_entity(self)
                return True
        if random.random() < 0.01:
            self.stand()
            return True
        return super().behave(world, dt)

    def stand(self) -> None:
        self.is_sentinel = True
        self.stop()
        self.action_text = "sentinel"


class Warthog(Omnivore):
    def __init__(self, position: Vec2):
        super().__init__("Warthog", position, color=(142, 100, 74), health=82, speed=68, power=11)
        self.tusk_power = 14.0
        self.burrow_location: Optional[Vec2] = None
        self.diet_preference = 0.35
        self.aggression = 0.45
        self.radius = 18

    def behave(self, world: object, dt: float) -> bool:
        threat = world.nearest_predator(self, self.detect_range)
        if threat is not None:
            cave = world.nearest_terrain_type(Cave, self.position)
            if cave is not None:
                self.burrow_location = cave.position.copy()
                self.move_toward(cave.position, self.speed * 1.05)
                if cave.contains(self):
                    self.burrow(cave, world)
                return True
        return super().behave(world, dt)

    def dig(self) -> None:
        self.action_text = "dig"

    def burrow(self, cave: Cave, world: object) -> None:
        cave.owner = self
        cave.hide_entity(self)
        world.expel_meerkats_from_cave(cave)
        self.action_text = "burrow"


class Lion(Carnivore):
    def __init__(self, position: Vec2):
        super().__init__("Lion", position, color=(204, 154, 67), health=125, speed=76, power=21, detect_range=240)
        self.mane_size = 1.0
        self.mane_exist = True
        self.roar_cooldown = random.uniform(4.0, 9.0)

    def behave(self, world: object, dt: float) -> bool:
        self.roar_cooldown -= dt
        if self.roar_cooldown <= 0:
            self.Roar(world)
            self.roar_cooldown = random.uniform(8.0, 16.0)
            return True
        return super().behave(world, dt)

    def Roar(self, world: object) -> None:
        self.action_text = "roar"
        for animal in world.living_animals():
            if isinstance(animal, Zebra) and self.position.distance_to(animal.position) <= 190:
                animal.panic_boost_timer = max(animal.panic_boost_timer, 6.0)
            if animal.name in ("Bald_Eagle", "Hyena") and self.position.distance_to(animal.position) <= 115:
                animal.move_away_from(self.position, animal.speed * 1.2)
                animal.action_text = "pushed"
        for carcass in world.carcasses():
            if self.position.distance_to(carcass.position) <= 120:
                carcass.carried_by = None

    def hide(self) -> None:
        self.is_hidden = True
        self.stealth = 0.35
        self.action_text = "hide"


class Hyena(Carnivore):
    def __init__(self, position: Vec2):
        super().__init__("Hyena", position, color=(128, 118, 83), health=88, speed=82, power=13, detect_range=215)
        self.steal_prey_chance = 0.25
        self.stolen_prey: Optional[Carcass] = None
        self.steal_pray_cooltime = 0.0

    def behave(self, world: object, dt: float) -> bool:
        self.steal_pray_cooltime = max(0.0, self.steal_pray_cooltime - dt)
        lion = world.nearest_named("Lion", self.position, 130.0)
        if lion is not None and self.stolen_prey is not None and lion.action_text == "roar":
            self.stolen_prey.carried_by = None
            self.stolen_prey = None
            self.move_away_from(lion.position, self.speed * 1.3)
            self.action_text = "drop"
            return True
        if self.stolen_prey is not None:
            return self.stolen_prey_eat(world)
        if self.steal_pray_cooltime <= 0:
            carcass = world.carcass_eaten_by_lion_near(self.position, 150.0)
            if carcass is not None:
                return self.steal_prey(carcass)
        return super().behave(world, dt)

    def steal_prey(self, carcass: Carcass) -> bool:
        chance = self.steal_prey_chance + (self.health / self.max_health) * 0.25
        if random.random() <= chance:
            self.stolen_prey = carcass
            carcass.carried_by = self
            carcass.being_eaten_by = None
            self.steal_pray_cooltime = 8.0
            self.action_text = "steal"
            return True
        self.steal_pray_cooltime = 5.0
        return False

    def stolen_prey_eat(self, world: object) -> bool:
        predator = world.nearest_predator(self, 130.0)
        if predator is not None and predator is not self:
            self.move_away_from(predator.position, self.speed)
            self.action_text = "carry"
            return True
        if self.stolen_prey is not None:
            self.stolen_prey.reduce_hunger(self)
            if not self.stolen_prey.alive:
                self.stolen_prey = None
            return True
        return False

