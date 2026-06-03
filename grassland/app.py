import argparse

from grassland.world import World


def run():
    parser = argparse.ArgumentParser(description="와글와글 초원 생태계 시뮬레이션")
    parser.add_argument("--headless-steps", type=int, default=0, help="GUI 없이 지정 횟수만큼 시뮬레이션합니다.")
    args = parser.parse_args()

    world = World.seed_default()

    if args.headless_steps > 0:
        for step in range(args.headless_steps):
            world.update(1 / 30)
        print(
            "Day "
            + str(world.environment.day)
            + " "
            + world.environment.clock_text()
            + " | terrain="
            + str(len(world.terrains))
            + " resources="
            + str(len(world.resources))
            + " animals="
            + str(len(world.living_animals()))
        )
        return

    from grassland.gui import GrasslandApp

    app = GrasslandApp(world)
    app.run()

