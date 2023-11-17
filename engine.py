import json
import math

import pygame


class KeyHandler:
    def __init__(self):
        self.keys = {}

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.keys[event.key] = True
        elif event.type == pygame.KEYUP:
            self.keys[event.key] = False

    def is_pressed(self, key):
        return self.keys.get(key, False)

    def is_released(self, key):
        return not self.keys.get(key, False)

    def is_down(self, key):
        return self.keys.get(key, False)

    def is_up(self, key):
        return not self.keys.get(key, False)

    def reset(self):
        self.keys = {}


class MouseHandler:
    def __init__(self):
        self.buttons = {}
        self.mouse_position = Vector2(0, 0)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.buttons[event.button] = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.buttons[event.button] = False
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_position = Vector2(event.pos[0], event.pos[1])

    def is_pressed(self, button):
        return self.buttons.get(button, False)

    def is_released(self, button):
        return not self.buttons.get(button, False)

    def is_down(self, button):
        return self.buttons.get(button, False)

    def is_up(self, button):
        return not self.buttons.get(button, False)

    def get_mouse_position(self):
        return self.mouse_position

    def reset(self):
        self.buttons = {}


class Game:
    def __init__(self, resolution: (int, int)):
        self.state = GameState(self)
        self.state.game = self
        self.keyboard = KeyHandler()
        self.mouse = MouseHandler()
        self.settings = SettingsHandler(self)
        self.paused = False
        self.fps = 60
        self.fps_clock = pygame.time.Clock()
        self.fps_clock.tick(self.fps)
        self.objects = []

        self.resolution = resolution
        self.screen = pygame.display.set_mode(self.resolution)
        self.renderer = Renderer(self)
        pygame.init()

    def set_resolution(self, resolution):
        self.resolution = resolution
        self.screen = pygame.display.set_mode(self.resolution)

    def handle_event(self, event):
        self.keyboard.handle_event(event)
        self.mouse.handle_event(event)
        self.state.handle_event(event)

    def update(self):
        if self.paused:
            return
        self.state.update()

    def draw(self):
        self.state.draw()
        # pause menu
        if self.paused:
            pygame.draw.rect(self.screen, (255, 255, 255), (0, 0, self.resolution[0], self.resolution[1]))
            font = pygame.font.SysFont("Arial", 50)
            text = font.render("Paused", True, (0, 0, 0))
            self.screen.blit(text, (
            self.resolution[0] / 2 - text.get_width() / 2, self.resolution[1] / 2 - text.get_height() / 2))
            text = font.render("Press P to unpause", True, (0, 0, 0))
            self.screen.blit(text, (
            self.resolution[0] / 2 - text.get_width() / 2, self.resolution[1] / 2 - text.get_height() / 2 + 50))

    def initialize(self):
        self.state.initialize()

    def set_state(self, state):
        self.state = state
        self.state.game = self
        self.initialize()

    def run(self):
        self.initialize()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                self.handle_event(event)
            self.update()
            self.draw()
            pygame.display.update()
            self.keyboard.reset()
            self.fps_clock.tick(self.fps)

    def handle_error(self, error: Exception):
        print(error)

    def quit(self):
        self.settings.save()
        pygame.quit()


class GameObject:
    def __init__(self, state):
        self.state = state
        self.game = state.game
        self.state.objects.append(self)
        self.renderer = state.renderer

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def draw(self):
        pass

    def initialize(self):
        pass

    def on_destroy(self):
        pass

    def destroy(self):
        try:
            self.state.objects.remove(self)
            self.on_destroy()
        except Exception as e:
            self.state.game.handle_error(e)


class GameState:
    def __init__(self, game):
        self.game = game
        self.renderer = Renderer(game)
        self.objects = []

    def handle_event(self, event):
        for obj in self.objects:
            obj.handle_event(event)

    def update(self):
        for obj in self.objects:
            obj.update()

    def draw(self):
        for obj in self.objects:
            obj.draw()

    def initialize(self):
        for obj in self.objects:
            obj.initialize()


# saves and reads settings from a json file
class SettingsHandler:
    def __init__(self, game: Game):
        self.game = game
        self.path = ""
        self.settings = {}

    def load(self, path: str):
        self.path = path
        try:
            with open(self.path, "r") as file:
                self.settings = json.load(file)
        except Exception as e:
            print(e)

    def save(self):
        if self.path == "":
            return
        try:
            with open(self.path, "w") as file:
                json.dump(self.settings, file)
        except Exception as e:
            self.game.handle_error(e)

    def get(self, key: str, default):
        return self.settings.get(key, default)

    def set(self, key: str, value):
        self.settings[key] = value

    def is_empty(self):
        return len(self.settings) == 0


# utilities

class Vector2:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        self = self + other
        return self

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __isub__(self, other):
        self = self - other
        return self

    def __mul__(self, other):
        return Vector2(self.x * other, self.y * other)

    def __imul__(self, other):
        self = self * other
        return self

    def __truediv__(self, other):
        return Vector2(self.x / other, self.y / other)

    def __itruediv__(self, other):
        self = self / other
        return self

    def __floordiv__(self, other):
        return Vector2(self.x // other, self.y // other)

    def __ifloordiv__(self, other):
        self = self // other
        return self

    def __str__(self):
        return "Vector2({}, {})".format(self.x, self.y)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def length(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def normalized(self):
        return self / self.length()

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def distance(self, other):
        return (self - other).length()

    def angle(self, other):
        return math.acos(self.dot(other) / (self.length() * other.length()))

    def rotate(self, angle):
        return Vector2(self.x * math.cos(angle) - self.y * math.sin(angle),
                       self.x * math.sin(angle) + self.y * math.cos(angle))


class Rectangle:
    def __init__(self, pos: Vector2, size: Vector2):
        self.pos = pos
        self.size = size

    def __str__(self):
        return "Rectangle({}, {})".format(self.pos, self.size)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.pos == other.pos and self.size == other.size

    def __contains__(self, other):
        return other.pos.x >= self.pos.x and other.pos.y >= self.pos.y and other.pos.x + other.size.x <= self.pos.x + self.size.x and other.pos.y + other.size.y <= self.pos.y + self.size.y

    def contains(self, other):
        return other in self

    def contains_point(self, point):
        return point.x >= self.pos.x and point.y >= self.pos.y and point.x <= self.pos.x + self.size.x and point.y <= self.pos.y + self.size.y

    def center(self):
        return self.pos + self.size / 2

    def center_on(self, other):
        self.pos = other.center() - self.size / 2

    def top_left(self):
        return self.pos

    def top_right(self):
        return Vector2(self.pos.x + self.size.x, self.pos.y)

    def bottom_left(self):
        return Vector2(self.pos.x, self.pos.y + self.size.y)

    def bottom_right(self):
        return self.pos + self.size

    def top(self):
        return self.pos.y

    def bottom(self):
        return self.pos.y + self.size.y

    def left(self):
        return self.pos.x

    def right(self):
        return self.pos.x + self.size.x

    def width(self):
        return self.size.x

    def height(self):
        return self.size.y

    def set_width(self, width):
        self.size.x = width

    def set_height(self, height):
        self.size.y = height

    def set_size(self, size):
        self.size = size

    def set_pos(self, pos):
        self.pos = pos

    def set_x(self, x):
        self.pos.x = x

    def set_y(self, y):
        self.pos.y = y


class Circle:
    def __init__(self, pos: Vector2, radius: float):
        self.pos = pos
        self.radius = radius

    def __str__(self):
        return "Circle({}, {})".format(self.pos, self.radius)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.pos == other.pos and self.radius == other.radius

    def __contains__(self, other):
        return self.pos.distance(other.pos) <= self.radius + other.radius

    def intersects(self, other):
        return self.pos.distance(other.pos) <= self.radius + other.radius

    def contains(self, other):
        return other in self

    def center(self):
        return self.pos

    def center_on(self, other):
        self.pos = other.center()

    def top_left(self):
        return Vector2(self.pos.x - self.radius, self.pos.y - self.radius)

    def top_right(self):
        return Vector2(self.pos.x + self.radius, self.pos.y - self.radius)

    def bottom_left(self):
        return Vector2(self.pos.x - self.radius, self.pos.y + self.radius)

    def bottom_right(self):
        return Vector2(self.pos.x + self.radius, self.pos.y + self.radius)

    def top(self):
        return self.pos.y - self.radius

    def bottom(self):
        return self.pos.y + self.radius

    def left(self):
        return self.pos.x - self.radius

    def right(self):
        return self.pos.x + self.radius

    def width(self):
        return self.radius * 2

    def height(self):
        return self.radius * 2

    def set_width(self, width):
        self.radius = width / 2

    def set_height(self, height):
        self.radius = height / 2

    def set_size(self, size):
        self.radius = size.x / 2

    def set_pos(self, pos):
        self.pos = pos

    def set_x(self, x):
        self.pos.x = x

    def set_y(self, y):
        self.pos.y = y


class Renderer:
    def __init__(self, game):
        self.game = game

    def fill(self, color: (int, int, int)):
        self.game.screen.fill(color)

    def clear(self):
        self.game.screen.fill((0, 0, 0))

    def draw_rect(self, rect: Rectangle, color: (int, int, int)):
        pygame.draw.rect(self.game.screen, color, (rect.pos.x, rect.pos.y, rect.size.x, rect.size.y))

    def draw_rect_border(self, rect: Rectangle, color: (int, int, int), width: int):
        pygame.draw.rect(self.game.screen, color, (rect.pos.x, rect.pos.y, rect.size.x, rect.size.y), width)

    def draw_circle(self, circle: Circle, color: (int, int, int)):
        pygame.draw.circle(self.game.screen, color, (int(circle.pos.x), int(circle.pos.y)), int(circle.radius))

    def draw_line(self, start: Vector2, end: Vector2, color: (int, int, int)):
        pygame.draw.line(self.game.screen, color, (int(start.x), int(start.y)), (int(end.x), int(end.y)))

    def draw_polygon(self, points: [Vector2], color: (int, int, int)):
        pygame.draw.polygon(self.game.screen, color, [(int(point.x), int(point.y)) for point in points])

    def draw_text(self, text: str, pos: Vector2, color: (int, int, int), font: pygame.font.Font):
        rendered_text = font.render(text, True, color)
        self.game.screen.blit(rendered_text, (pos.x, pos.y))

    def draw_text_centered(self, text: str, pos: Vector2, color: (int, int, int), font: pygame.font.Font):
        rendered_text = font.render(text, True, color)
        self.game.screen.blit(rendered_text,
                              (pos.x - rendered_text.get_width() / 2, pos.y - rendered_text.get_height() / 2))

    def draw_img(self, img: pygame.Surface, pos: Vector2):
        self.game.screen.blit(img, (pos.x, pos.y))

    def draw_img_centered(self, img: pygame.Surface, pos: Vector2):
        self.game.screen.blit(img, (pos.x - img.get_width() / 2, pos.y - img.get_height() / 2))

    def draw_img_rotated(self, img: pygame.Surface, pos: Vector2, angle: float):
        self.game.screen.blit(pygame.transform.rotate(img, angle), (pos.x, pos.y))

    def draw_img_rotated_centered(self, img: pygame.Surface, pos: Vector2, angle: float):
        self.game.screen.blit(pygame.transform.rotate(img, angle),
                              (pos.x - img.get_width() / 2, pos.y - img.get_height() / 2))
