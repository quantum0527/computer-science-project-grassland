from __future__ import annotations

import pygame

from grassland.config import (
    BACKGROUND_COLOR,
    FPS,
    GRID_COLOR,
    PANEL_BORDER,
    PANEL_COLOR,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TEXT_COLOR,
)
from grassland.entities.animals import Animal
from grassland.entities.resources import Carcass, WaterPuddle
from grassland.entities.terrain import Cave, LakeSide, Plain
from grassland.geometry import Vec2
from grassland.world import World


class GrasslandApp:
    def __init__(self, world: World):
        pygame.init()
        pygame.display.set_caption("와글와글 초원 생태계")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.world = world
        self.camera = Vec2(220, 180)
        self.dragging = False
        self.font = self._font(17)
        self.small_font = self._font(13)
        self.title_font = self._font(22)

    def _font(self, size: int) -> pygame.font.Font:
        for name in ("malgungothic", "맑은 고딕", "arial"):
            font = pygame.font.SysFont(name, size)
            if font is not None:
                return font
        return pygame.font.Font(None, size)

    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.dragging = True
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.dragging = False
                elif event.type == pygame.MOUSEMOTION and self.dragging:
                    rel_x, rel_y = event.rel
                    self.camera.x -= rel_x
                    self.camera.y -= rel_y
                    self.clamp_camera()

            self.world.update(dt)
            self.draw()

        pygame.quit()

    def clamp_camera(self) -> None:
        self.camera.x = max(0, min(self.camera.x, self.world.width - SCREEN_WIDTH))
        self.camera.y = max(0, min(self.camera.y, self.world.height - SCREEN_HEIGHT))

    def world_to_screen(self, position: Vec2) -> tuple[int, int]:
        return int(position.x - self.camera.x), int(position.y - self.camera.y)

    def visible(self, entity: object, margin: int = 90) -> bool:
        x, y = self.world_to_screen(entity.position)
        return -margin <= x <= SCREEN_WIDTH + margin and -margin <= y <= SCREEN_HEIGHT + margin

    def draw(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_field()
        self.draw_terrains()
        self.draw_plants()
        self.draw_resources()
        self.draw_animals()
        self.draw_ui()
        pygame.display.flip()

    def draw_field(self) -> None:
        start_x = int(self.camera.x // 80) * 80
        start_y = int(self.camera.y // 80) * 80
        for world_x in range(start_x, int(self.camera.x + SCREEN_WIDTH) + 80, 80):
            screen_x = int(world_x - self.camera.x)
            pygame.draw.line(self.screen, GRID_COLOR, (screen_x, 0), (screen_x, SCREEN_HEIGHT), 1)
        for world_y in range(start_y, int(self.camera.y + SCREEN_HEIGHT) + 80, 80):
            screen_y = int(world_y - self.camera.y)
            pygame.draw.line(self.screen, GRID_COLOR, (0, screen_y), (SCREEN_WIDTH, screen_y), 1)

    def draw_terrains(self) -> None:
        for terrain in self.world.terrains:
            if isinstance(terrain, Plain):
                continue
            if not self.visible(terrain, 140):
                continue
            x, y = self.world_to_screen(terrain.position)
            if isinstance(terrain, LakeSide):
                pygame.draw.circle(self.screen, terrain.color, (x, y), int(terrain.radius))
                pygame.draw.circle(self.screen, (43, 101, 149), (x, y), int(terrain.radius), 3)
            elif isinstance(terrain, Cave):
                rect = pygame.Rect(0, 0, terrain.radius * 2, terrain.radius * 1.4)
                rect.center = (x, y)
                pygame.draw.ellipse(self.screen, terrain.color, rect)
                pygame.draw.ellipse(self.screen, (48, 43, 39), rect, 3)
            self.draw_label(terrain.name, x, y + int(terrain.radius) + 8, self.small_font)

    def draw_plants(self) -> None:
        for plant in self.world.alive_plants():
            if not self.visible(plant):
                continue
            x, y = self.world_to_screen(plant.position)
            size = int(plant.radius * 1.45)
            rect = pygame.Rect(0, 0, size, size)
            rect.center = (x, y)
            pygame.draw.rect(self.screen, plant.color, rect, border_radius=5)
            pygame.draw.rect(self.screen, (48, 91, 48), rect, 2, border_radius=5)
            self.draw_label(plant.name, x, y + size // 2 + 10, self.small_font)

    def draw_resources(self) -> None:
        for resource in self.world.resources:
            if not resource.alive or not self.visible(resource):
                continue
            x, y = self.world_to_screen(resource.position)
            if isinstance(resource, WaterPuddle):
                pygame.draw.circle(self.screen, resource.color, (x, y), int(resource.radius))
                pygame.draw.circle(self.screen, (36, 95, 158), (x, y), int(resource.radius), 2)
            elif isinstance(resource, Carcass):
                rect = pygame.Rect(0, 0, int(resource.radius * 1.6), int(resource.radius * 1.2))
                rect.center = (x, y)
                pygame.draw.rect(self.screen, resource.color, rect, border_radius=4)
                pygame.draw.rect(self.screen, (76, 43, 29), rect, 2, border_radius=4)
            self.draw_label(resource.name, x, y + int(resource.radius) + 10, self.small_font)

    def draw_animals(self) -> None:
        for animal in self.world.animals:
            if not animal.alive or not self.visible(animal):
                continue
            x, y = self.world_to_screen(animal.position)
            size = int(animal.radius * 2)
            rect = pygame.Rect(0, 0, size, size)
            rect.center = (x, y)
            color = animal.color
            if animal.is_hidden:
                color = tuple(max(35, int(channel * 0.65)) for channel in color)
            pygame.draw.rect(self.screen, color, rect, border_radius=6)
            pygame.draw.rect(self.screen, (40, 43, 35), rect, 2, border_radius=6)
            self.draw_health_bar(animal, x, y - size // 2 - 9, size)
            self.draw_label(animal.name, x, y + size // 2 + 9, self.small_font)
            if animal.action_text:
                self.draw_label(animal.action_text, x, y - size // 2 - 22, self.small_font, (36, 36, 32))

    def draw_health_bar(self, animal: Animal, x: int, y: int, width: int) -> None:
        bar_width = max(24, width)
        rect = pygame.Rect(0, 0, bar_width, 5)
        rect.center = (x, y)
        pygame.draw.rect(self.screen, (80, 65, 58), rect)
        fill = rect.copy()
        fill.width = int(rect.width * max(0.0, animal.health / animal.max_health))
        pygame.draw.rect(self.screen, (88, 190, 91), fill)

    def draw_ui(self) -> None:
        panel = pygame.Rect(16, 14, 650, 92)
        pygame.draw.rect(self.screen, PANEL_COLOR, panel, border_radius=8)
        pygame.draw.rect(self.screen, PANEL_BORDER, panel, 2, border_radius=8)

        env = self.world.environment
        title = f"Day {env.day}  {env.clock_text()}   Weather: {env.weather}   Temp: {env.temperature}C"
        self.screen.blit(self.title_font.render(title, True, TEXT_COLOR), (32, 26))

        counts = self.world.counts_by_name()
        count_text = " | ".join(f"{name}:{count}" for name, count in sorted(counts.items()))
        self.screen.blit(self.font.render(count_text, True, TEXT_COLOR), (32, 58))

        camera_text = f"Map {int(self.camera.x)},{int(self.camera.y)} / drag to move"
        self.screen.blit(self.small_font.render(camera_text, True, TEXT_COLOR), (32, 83))

        if env.ended:
            self.draw_end_panel(env.end_reason)

    def draw_end_panel(self, reason: str) -> None:
        panel = pygame.Rect(0, 0, 680, 110)
        panel.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.draw.rect(self.screen, (245, 235, 211), panel, border_radius=8)
        pygame.draw.rect(self.screen, (92, 65, 50), panel, 3, border_radius=8)
        self.draw_label("Simulation Ended", panel.centerx, panel.centery - 22, self.title_font, (62, 45, 38))
        self.draw_label(reason, panel.centerx, panel.centery + 15, self.font, (62, 45, 38))

    def draw_label(
        self,
        text: str,
        x: int,
        y: int,
        font: pygame.font.Font,
        color: tuple[int, int, int] = TEXT_COLOR,
    ) -> None:
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(x, y))
        self.screen.blit(surface, rect)

