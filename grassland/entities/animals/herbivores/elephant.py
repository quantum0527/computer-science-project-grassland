from __future__ import annotations

import random

from grassland.entities.animals.animal import Animal
from grassland.entities.animals.herbivores.herbivore import Herbivore
from grassland.geometry import Vec2


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
