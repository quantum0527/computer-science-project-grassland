from __future__ import annotations

import argparse

from grassland.world import World


def run() -> None:
    parser = argparse.ArgumentParser(description="와글와글 초원 생태계 시뮬레이션")
    parser.add_argument("--headless-steps", type=int, default=0, help="GUI 없이 지정 횟수만큼 시뮬레이션합니다.")
    args = parser.parse_args()

    world = World.seed_default()
    if args.headless_steps > 0:
        for _ in range(args.headless_steps):
            world.update(1 / 30)
        print(
            f"Day {world.environment.day} {world.environment.clock_text()} "
            f"| terrain={len(world.terrains)} resources={len(world.resources)} animals={len(world.living_animals())}"
        )
        return

    from grassland.gui import GrasslandApp

    GrasslandApp(world).run()
