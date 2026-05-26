from __future__ import annotations

from grassland.entities.animals.animal import Animal
from grassland.entities.animals.herbivores.herbivore import Herbivore
from grassland.geometry import Vec2


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
