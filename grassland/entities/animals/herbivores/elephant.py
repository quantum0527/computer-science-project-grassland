from __future__ import annotations

from grassland.entities.animals.herbivores.herbivore import Herbivore
from grassland.geometry import Vec2


class Elephant(Herbivore):
    def __init__(self, position: Vec2):
        super().__init__("Elephant", position, (132, 132, 123), 165.0, 52.0, 28.0, 220.0)
        self.radius = 28.0

    def fight_or_flight(self, threat: object, world: object, dt: float) -> None:
        if self.position.distance_to(threat.position) < 70.0:
            self.stomp(threat, world)
        else:
            self.move_away_from(threat.position, self.flee_speed * 0.75)
            self.action_text = "guard"
        self.lose_energy(7.0 * dt)

    def stomp(self, target: object, world: object) -> None:
        self.attack(target, world)
        self.action_text = "stomp"
