from __future__ import annotations

from dataclasses import dataclass
import random

from grassland.config import DAY_LENGTH_HOURS, GAME_HOURS_PER_SECOND


@dataclass
class Environment:
    day: int = 1
    time: float = 6.0
    weather: str = "sunny"
    temperature: int = 28
    ended: bool = False
    end_reason: str = ""

    def update(self, dt: float) -> bool:
        previous_day = self.day
        self.change_time(dt * GAME_HOURS_PER_SECOND)
        return self.day != previous_day

    def change_day(self) -> None:
        self.day += 1
        self.change_weather()
        self.change_temp()

    def change_time(self, hours: float) -> None:
        self.time += hours
        while self.time >= DAY_LENGTH_HOURS:
            self.time -= DAY_LENGTH_HOURS
            self.change_day()

    def change_weather(self) -> None:
        self.weather = random.choice(["sunny", "cloudy", "rain", "drought"])

    def change_temp(self) -> None:
        if self.weather == "drought":
            self.temperature = random.randint(34, 42)
        elif self.weather == "rain":
            self.temperature = random.randint(20, 28)
        elif self.weather == "cloudy":
            self.temperature = random.randint(23, 31)
        else:
            self.temperature = random.randint(27, 36)

    def clock_text(self) -> str:
        hour = int(self.time)
        minute = int((self.time - hour) * 60)
        return f"{hour:02d}:{minute:02d}"


class DroughtEvent:
    def __init__(self, drought_intensity: float):
        self.drought_intensity = drought_intensity

    def dry_up_map(self, world: object, dt: float) -> None:
        for water in world.water_puddles():
            water.consume(dt * self.drought_intensity * 3.0)

    def accelerate_thirst(self, animal: object, dt: float) -> None:
        animal.thirst = min(100.0, animal.thirst + dt * self.drought_intensity * 0.35)

