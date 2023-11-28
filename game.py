import os

import subprocess
import pygame

import engine

from engine import Vector2, Rectangle


class SpaceShooter(engine.Game):
    def __init__(self, resolution: (int, int)):
        super().__init__(resolution)
        self.set_state(MenuState(self))
        self.settings.load("settings.json")
        if self.settings.is_empty():
            self.settings.set("resolution", resolution)
            self.settings.set("fullscreen", False)
            self.settings.save()
        else:
            self.resolution = self.settings.get("resolution")
            if self.settings.get("fullscreen"):
                pygame.display.toggle_fullscreen()
        pygame.display.set_caption("Space Shooters")

    def update(self):
        super().update()

    def draw(self):
        super().draw()


class Button(engine.GameObject):
    def __init__(self, game : engine.GameState, center : Vector2, size : Vector2, text : str, font : pygame.font.Font, color : (int, int, int), hover_color : (int, int, int), click_color : (int, int, int)):
        super().__init__(game)
        self.center = center
        self.size = size
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.click_color = click_color
        self.rect = Rectangle(self.center - self.size / 2, self.size)
        self.hover = False
        self.click = False
        self.on_click = None

    def update(self):
        super().update()
        if self.click and not self.game.mouse.is_down(1):
            if self.on_click is not None:
                self.on_click()
        self.hover = self.rect.contains_point(self.game.mouse.get_mouse_position())
        self.click = self.hover and self.game.mouse.is_down(1)

    def draw(self):
        super().draw()
        if self.click:
            self.game.renderer.draw_rect(self.rect, self.click_color)
        elif self.hover:
            self.game.renderer.draw_rect(self.rect, self.hover_color)
        else:
            self.game.renderer.draw_rect(self.rect, self.color)
        self.game.renderer.draw_text_centered(self.text, self.center, (255, 255, 255), self.font)


class CheckBox(engine.GameObject):
    def __init__(self, game: engine.GameState, center: Vector2, size: Vector2, text: str, font: pygame.font.Font,
                 color: (int, int, int), hover_color: (int, int, int), click_color: (int, int, int)):
        super().__init__(game)
        self.center = center
        self.size = size
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.click_color = click_color
        checkbox_size = min(self.size.x, self.size.y)
        text_size = self.font.size(self.text)
        self.rect = Rectangle(self.center - Vector2(checkbox_size + text_size[0], checkbox_size) / 2,
                                  Vector2(checkbox_size, checkbox_size))
        self.hover = False
        self.click = False
        self.checked = False  # New property for checkbox
        self.on_click = None

    def update(self):
        super().update()
        if self.click and not self.game.mouse.is_down(1):
            if self.on_click is not None:
                self.checked = not self.checked
                self.on_click()
        self.hover = self.rect.contains_point(self.game.mouse.get_mouse_position())
        self.click = self.hover and self.game.mouse.is_down(1)

    def draw(self):
        super().draw()
        checkbox_size = min(self.size.x, self.size.y)
        text_size = self.font.size(self.text)
        checkbox_rect = Rectangle(self.center - Vector2(checkbox_size + text_size[0], checkbox_size) / 2,
                                  Vector2(checkbox_size, checkbox_size))
        container_rect = Rectangle(self.center - Vector2(text_size[0] + checkbox_size + 40, text_size[1] + 10) / 2,
                                   Vector2((text_size[0] + 120), text_size[1] + 10))

        self.game.renderer.draw_rect(container_rect, self.color)

        if self.click:
            self.game.renderer.draw_rect(self.rect, self.click_color)
        elif self.hover:
            self.game.renderer.draw_rect(self.rect, self.hover_color)
        else:
            self.game.renderer.draw_rect(self.rect, self.color)

        if self.checked:
            self.game.renderer.draw_rect(checkbox_rect, (255, 255, 255))

        # Draw checkbox border
        self.game.renderer.draw_rect_border(checkbox_rect, (0, 0, 0), 2)

        # Draw text
        text_position = Vector2(self.center.x + checkbox_size, self.center.y)
        self.game.renderer.draw_text_centered(self.text, text_position, (255, 255, 255), self.font)


class MenuState(engine.GameState):
    def __init__(self, game: engine.Game):
        super().__init__(game)

    def initialize(self):
        super().initialize()
        font = pygame.font.SysFont("monospace", 60)
        play = Button(self, Vector2(self.game.resolution[0] / 2, 310), Vector2(400, 100), "Play", font, (133, 133, 133), (200, 200, 200), (230, 230, 230))
        play.on_click = lambda: self.game.set_state(GameState(self.game))
        settings = Button(self, Vector2(self.game.resolution[0] / 2, 420), Vector2(400, 100), "Settings", font, (133, 133, 133), (200, 200, 200), (230, 230, 230))
        settings.on_click = lambda: self.game.set_state(SettingsState(self.game))
        quit = Button(self, Vector2(self.game.resolution[0] / 2, 530), Vector2(400, 100), "Quit", font, (133, 133, 133), (200, 200, 200), (230, 230, 230))
        quit.on_click = lambda: self.game.quit()

    def update(self):
        super().update()

    def draw(self):
        self.renderer.fill((100, 100, 100))
        super().draw()
        center = Vector2(self.game.resolution[0] / 2, 100)
        self.renderer.draw_rect(Rectangle(center - Vector2(300, 50), Vector2(600, 100)), (133, 133, 133))
        font = pygame.font.SysFont("monospace", 60)
        self.renderer.draw_text_centered("Space Shooters", center, (255, 255, 255), font)

# will have a back button and fullscreen checkbox (for now)
class SettingsState(engine.GameState):
    def __init__(self, game: engine.Game):
        super().__init__(game)

    def initialize(self):
        super().initialize()
        font = pygame.font.SysFont("monospace", 60)
        back = Button(self, Vector2(self.game.resolution[0] / 2, 530), Vector2(400, 100), "Back", font, (133, 133, 133), (200, 200, 200), (230, 230, 230))
        back.on_click = lambda: self.game.set_state(MenuState(self.game))
        checkbox = CheckBox(self, Vector2(self.game.resolution[0] / 2, 200), Vector2(50, 50), "Fullscreen", font, (133, 133, 133), (200, 200, 200), (230, 230, 230))
        checkbox.checked = self.game.settings.get("fullscreen")
        checkbox.on_click = lambda: {
            self.game.settings.set("fullscreen", checkbox.checked),
            pygame.display.toggle_fullscreen()
        }


    def update(self):
        super().update()

    def draw(self):
        self.renderer.fill((100, 100, 100))
        super().draw()
        center = Vector2(self.game.resolution[0] / 2, 100)
        self.renderer.draw_rect(Rectangle(center - Vector2(300, 50), Vector2(600, 100)), (133, 133, 133))
        font = pygame.font.SysFont("monospace", 60)
        self.renderer.draw_text_centered("Settings", center, (255, 255, 255), font)


game = SpaceShooter((800, 600))
game.run()
