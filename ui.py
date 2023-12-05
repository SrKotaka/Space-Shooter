import engine
import pygame
from engine import Vector2, Rectangle

class Button(engine.GameObject):
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