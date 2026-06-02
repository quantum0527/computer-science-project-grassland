from pathlib import Path

import pygame

from grassland.config import (
    ASSET_SPRITE_SHEET,
    BACKGROUND_COLOR,
    FPS,
    GRID_COLOR,
    MIN_SCREEN_HEIGHT,
    MIN_SCREEN_WIDTH,
    PANEL_BORDER,
    PANEL_COLOR,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SKY_OVERLAY_ALPHA,
    TEXT_COLOR,
)
from grassland.geometry import Vec2
from grassland.world import World


class GrasslandApp:
    def __init__(self, world):
        pygame.init()
        pygame.display.set_caption("와글와글 초원 생태계")
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.world = world
        self.camera = Vec2(220, 180)
        self.dragging = False
        self.font = self._font(17)
        self.small_font = self._font(13)
        self.title_font = self._font(22)
        self.sky_sprites = self.load_sky_sprites()

    def _font(self, size):
        for name in ("malgungothic", "맑은 고딕", "arial"):
            font = pygame.font.SysFont(name, size)
            if font is not None:
                return font
        return pygame.font.Font(None, size)

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.resize(event.w, event.h)
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

    def clamp_camera(self):
        max_x = max(0, self.world.width - self.screen_width)
        max_y = max(0, self.world.height - self.screen_height)
        self.camera.x = max(0, min(self.camera.x, max_x))
        self.camera.y = max(0, min(self.camera.y, max_y))

    def resize(self, width, height):
        self.screen_width = max(MIN_SCREEN_WIDTH, width)
        self.screen_height = max(MIN_SCREEN_HEIGHT, height)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        self.clamp_camera()

    def load_sky_sprites(self):
        sheet_path = Path(ASSET_SPRITE_SHEET)
        if not sheet_path.exists():
            return {}

        sheet = pygame.image.load(str(sheet_path)).convert_alpha()
        cell_width = sheet.get_width() // 5
        cell_height = sheet.get_height() // 4
        clear_rect = pygame.Rect(cell_width * 3, cell_height * 3, cell_width, cell_height)
        storm_rect = pygame.Rect(cell_width * 4, cell_height * 3, cell_width, cell_height)
        return {
            "clear": sheet.subsurface(clear_rect).copy(),
            "storm": sheet.subsurface(storm_rect).copy(),
        }

    def world_to_screen(self, position):
        return int(position.x - self.camera.x), int(position.y - self.camera.y)

    def visible(self, entity, margin=90):
        x, y = self.world_to_screen(entity.position)
        return -margin <= x <= self.screen_width + margin and -margin <= y <= self.screen_height + margin

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_field()
        self.draw_terrains()
        self.draw_plants()
        self.draw_resources()
        self.draw_animals()
        self.draw_sky_overlay()
        self.draw_ui()
        pygame.display.flip()

    def draw_field(self):
        start_x = int(self.camera.x // 80) * 80
        start_y = int(self.camera.y // 80) * 80
        for world_x in range(start_x, int(self.camera.x + self.screen_width) + 80, 80):
            screen_x = int(world_x - self.camera.x)
            pygame.draw.line(self.screen, GRID_COLOR, (screen_x, 0), (screen_x, self.screen_height), 1)
        for world_y in range(start_y, int(self.camera.y + self.screen_height) + 80, 80):
            screen_y = int(world_y - self.camera.y)
            pygame.draw.line(self.screen, GRID_COLOR, (0, screen_y), (self.screen_width, screen_y), 1)

    def draw_sky_overlay(self):
        sky_height = min(132, max(96, self.screen_height // 7))
        weather = self.world.environment.weather
        sprite_key = "storm" if weather in ("rain", "drought") else "clear"
        sky = self.sky_sprites.get(sprite_key)

        if sky is not None:
            overlay = pygame.transform.smoothscale(sky, (self.screen_width, sky_height))
            overlay.set_alpha(SKY_OVERLAY_ALPHA)
            self.screen.blit(overlay, (0, 0))
        else:
            fallback_colors = {
                "sunny": (135, 205, 240),
                "cloudy": (175, 198, 210),
                "rain": (92, 112, 126),
                "drought": (230, 177, 92),
            }
            overlay = pygame.Surface((self.screen_width, sky_height), pygame.SRCALPHA)
            color = fallback_colors.get(weather, (135, 205, 240))
            overlay.fill((*color, SKY_OVERLAY_ALPHA))
            self.screen.blit(overlay, (0, 0))

        if weather == "drought":
            heat = pygame.Surface((self.screen_width, sky_height), pygame.SRCALPHA)
            heat.fill((239, 137, 53, 72))
            self.screen.blit(heat, (0, 0))

        pygame.draw.line(self.screen, (246, 241, 222), (0, sky_height), (self.screen_width, sky_height), 2)

    def draw_terrains(self):
        for terrain in self.world.terrains:
            if terrain.name == "Plain":
                continue
            if not self.visible(terrain, 140):
                continue
            x, y = self.world_to_screen(terrain.position)
            if terrain.name == "Lake_Side":
                pygame.draw.circle(self.screen, terrain.color, (x, y), int(terrain.radius))
                pygame.draw.circle(self.screen, (43, 101, 149), (x, y), int(terrain.radius), 3)
            elif terrain.name == "Cave":
                rect = pygame.Rect(0, 0, terrain.radius * 2, terrain.radius * 1.4)
                rect.center = (x, y)
                pygame.draw.ellipse(self.screen, terrain.color, rect)
                pygame.draw.ellipse(self.screen, (48, 43, 39), rect, 3)
            self.draw_label(terrain.name, x, y + int(terrain.radius) + 8, self.small_font)

    def draw_plants(self):
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

    def draw_resources(self):
        for resource in self.world.resources:
            if not resource.alive or not self.visible(resource):
                continue
            x, y = self.world_to_screen(resource.position)
            if resource.name == "Water_Puddle":
                pygame.draw.circle(self.screen, resource.color, (x, y), int(resource.radius))
                pygame.draw.circle(self.screen, (36, 95, 158), (x, y), int(resource.radius), 2)
            elif resource.name == "Carcass":
                rect = pygame.Rect(0, 0, int(resource.radius * 1.6), int(resource.radius * 1.2))
                rect.center = (x, y)
                pygame.draw.rect(self.screen, resource.color, rect, border_radius=4)
                pygame.draw.rect(self.screen, (76, 43, 29), rect, 2, border_radius=4)
            self.draw_label(resource.name, x, y + int(resource.radius) + 10, self.small_font)

    def draw_animals(self):
        for animal in self.world.animals:
            if not getattr(animal, "alive", True) or not self.visible(animal):
                continue
            x, y = self.world_to_screen(animal.position)
            radius = getattr(animal, "radius", 18)
            size = int(radius * 2)
            rect = pygame.Rect(0, 0, size, size)
            rect.center = (x, y)
            color = getattr(animal, "color", (220, 220, 220))
            if getattr(animal, "is_hidden", False):
                color = tuple(max(35, int(channel * 0.65)) for channel in color)
            pygame.draw.rect(self.screen, color, rect, border_radius=6)
            pygame.draw.rect(self.screen, (40, 43, 35), rect, 2, border_radius=6)
            self.draw_health_bar(animal, x, y - size // 2 - 9, size)
            self.draw_label(getattr(animal, "name", "Animal"), x, y + size // 2 + 9, self.small_font)
            action_text = getattr(animal, "action_text", "")
            if action_text:
                self.draw_label(action_text, x, y - size // 2 - 22, self.small_font, (36, 36, 32))

    def draw_health_bar(self, animal, x, y, width):
        if not hasattr(animal, "health"):
            return
        bar_width = max(24, width)
        rect = pygame.Rect(0, 0, bar_width, 5)
        rect.center = (x, y)
        pygame.draw.rect(self.screen, (80, 65, 58), rect)
        fill = rect.copy()
        max_health = max(1.0, getattr(animal, "max_health", animal.health))
        fill.width = int(rect.width * max(0.0, animal.health / max_health))
        pygame.draw.rect(self.screen, (88, 190, 91), fill)

    def draw_ui(self):
        panel_width = min(690, self.screen_width - 32)
        panel = pygame.Rect(16, 14, panel_width, 92)
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

    def draw_end_panel(self, reason):
        panel = pygame.Rect(0, 0, min(680, self.screen_width - 48), 110)
        panel.center = (self.screen_width // 2, self.screen_height // 2)
        pygame.draw.rect(self.screen, (245, 235, 211), panel, border_radius=8)
        pygame.draw.rect(self.screen, (92, 65, 50), panel, 3, border_radius=8)
        self.draw_label("Simulation Ended", panel.centerx, panel.centery - 22, self.title_font, (62, 45, 38))
        self.draw_label(reason, panel.centerx, panel.centery + 15, self.font, (62, 45, 38))

    def draw_label(self, text, x, y, font, color=TEXT_COLOR):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(x, y))
        self.screen.blit(surface, rect)
