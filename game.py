import math
import random

import pygame

import engine
from engine import Vector2, Rectangle, Circle
from ui import Button, CheckBox


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


class MenuState(engine.GameState):
    def __init__(self, game: engine.Game):
        super().__init__(game)

    def initialize(self):
        super().initialize()
        font = pygame.font.SysFont("monospace", 60)
        play = Button(self, Vector2(self.game.resolution[0] / 2, 310), Vector2(400, 100), "Play", font, (133, 133, 133),
                      (200, 200, 200), (230, 230, 230))
        play.on_click = lambda: self.game.set_state(GameState(self.game))
        settings = Button(self, Vector2(self.game.resolution[0] / 2, 420), Vector2(400, 100), "Settings", font,
                          (133, 133, 133), (200, 200, 200), (230, 230, 230))
        settings.on_click = lambda: self.game.set_state(SettingsState(self.game))
        quit = Button(self, Vector2(self.game.resolution[0] / 2, 530), Vector2(400, 100), "Quit", font, (133, 133, 133),
                      (200, 200, 200), (230, 230, 230))
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


class StarParticle(engine.GameObject):
    def __init__(self, game: engine.GameState, center: Vector2, radius: float, color: (int, int, int)):
        super().__init__(game)
        self.center = center
        self.radius = radius
        self.color = color

    def update(self):
        super().update()
        self.center.y += 1 * self.radius / 2
        if self.center.y > self.game.resolution[1] + self.radius:
            self.destroy()

    def draw(self):
        super().draw()
        self.game.renderer.draw_circle(Circle(self.center, self.radius), self.color)


# will just move down and despawn when it goes off screen
# if its close enough to the player it will move towards it
# if its distance to the player is less than 100, it will be collected and call on_pickup
class PowerPickup(engine.GameObject):
    def __init__(self, game: engine.GameState, center: Vector2):
        super().__init__(game)
        self.center = center
        self.texture = pygame.image.load("assets/power.png")

    def update(self):
        super().update()
        self.center.y += 2
        if self.center.y > self.game.resolution[1] + 50:
            self.destroy()
        if (self.center - self.state.player.position).length() < 100:
            self.center += (self.state.player.position - self.center).normalized() * 5
        if (self.center - self.state.player.position).length() < 25:
            self.state.player.power += 1
            self.state.score += 50
            self.destroy()

    def draw(self):
        super().draw()
        self.game.renderer.draw_img_centered(self.texture, self.center)


# will just move (circle particle) in its direction while slowly decreasing in size
class ExplosionParticle(engine.GameObject):
    def __init__(self, game: engine.GameState, center: Vector2, radius: float, color: (int, int, int),
                 direction: Vector2):
        super().__init__(game)
        self.center = center
        self.radius = radius
        self.color = color
        self.direction = direction

    def update(self):
        super().update()
        self.center += self.direction * 3
        self.radius -= 0.5
        if self.radius <= 0:
            self.destroy()

    def draw(self):
        super().draw()
        self.game.renderer.draw_circle(Circle(self.center, self.radius), self.color)


class PlayerBullet:
    def __init__(self, game: engine.GameState, center: Vector2, velocity: Vector2 = Vector2(0, -10)):
        self.game = game
        self.center = center
        self.velocity = velocity
        self.color = (200, 200, 255)
        self.sprite = pygame.image.load("assets/shot.png")
        self.size = Vector2(10, 33)
        self.hitbox = Rectangle(self.center - self.size / 2, self.size)
        self.dead = False
        self.friendly = True
        game.projectiles.append(self)

    def update(self):
        self.center += self.velocity
        if self.center.y < -self.size.y / 2:
            self.dead = True
        self.hitbox = Rectangle(self.center - self.size / 2, self.size)

    def draw(self):
        self.game.renderer.draw_img_centered(self.sprite, self.center)


class Player(engine.GameObject):
    def __init__(self, game: engine.GameState, position: Vector2):
        super().__init__(game)
        # power points (drops you get from enemies)
        # makes weapon different (more power = more bullets)
        self.power = 0
        self.dead = False
        self.deadTimer = 0
        self.lives = 3
        self.position = position
        self.velocity = Vector2(0, 0)
        self.shotCd = 0
        self.texture = pygame.image.load("assets/spaceship.png")
        self.lifeTexture = pygame.image.load("assets/heart.png")
        self.hitbox = Rectangle(self.position - Vector2(10, 15), Vector2(20, 35))
        self.immuneFrames = 0

    def update(self):
        if self.dead:
            self.deadTimer += 1
            if self.deadTimer >= 240:
                self.game.set_state(MenuState(self.game))
            return
        super().update()
        self.position += self.velocity
        self.velocity *= 0.8
        if self.immuneFrames > 0:
            self.immuneFrames -= 1
        if self.shotCd > 0:
            self.shotCd -= 1
        if self.game.keyboard.is_down(pygame.K_LEFT) or self.game.keyboard.is_down(pygame.K_a):
            self.velocity.x -= 1
        if self.game.keyboard.is_down(pygame.K_RIGHT) or self.game.keyboard.is_down(pygame.K_d):
            self.velocity.x += 1
        if self.game.keyboard.is_down(pygame.K_UP) or self.game.keyboard.is_down(pygame.K_w):
            self.velocity.y -= 1
        if self.game.keyboard.is_down(pygame.K_DOWN) or self.game.keyboard.is_down(pygame.K_s):
            self.velocity.y += 1

        if (self.position.x - 10) < 0:
            self.position.x = 10
        if (self.position.x + 10) > self.game.resolution[0]:
            self.position.x = self.game.resolution[0] - 10
        if (self.position.y - 25) < 0:
            self.position.y = 25
        if (self.position.y + 25) > self.game.resolution[1]:
            self.position.y = self.game.resolution[1] - 25

        if self.game.keyboard.is_down(pygame.K_SPACE) and self.shotCd == 0:
            if self.power < 10:
                b = PlayerBullet(self.state, Vector2(self.position.x, self.position.y - 40))
            elif self.power < 25:
                b = PlayerBullet(self.state, Vector2(self.position.x - 10, self.position.y - 40))
                b = PlayerBullet(self.state, Vector2(self.position.x + 10, self.position.y - 40))
            else:
                b = PlayerBullet(self.state, Vector2(self.position.x - 10, self.position.y - 40), Vector2(-10, -10))
                b = PlayerBullet(self.state, Vector2(self.position.x + 10, self.position.y - 40), Vector2(10, -10))
                b = PlayerBullet(self.state, Vector2(self.position.x, self.position.y - 40))
            self.shotCd = 10
        self.hitbox = Rectangle(self.position - Vector2(10, 15), Vector2(20, 35))

    def on_hit(self, entity):
        if self.immuneFrames > 0 or self.dead:
            return
        # spawn some random particles in the direction of the bullet
        dir = entity.velocity
        dirRot = dir.to_rotation()
        for i in range(30):
            rot = math.radians(random.randint(-15, 15))
            direction = Vector2(math.cos(dirRot + rot), math.sin(dirRot + rot)) * random.randint(1, 4)
            e = ExplosionParticle(self.state, self.position, random.randint(5, 8), (200, 200, 255), direction)


        self.immuneFrames = 60
        entity.dead = True
        self.lives -= 1
        if self.lives <= 0:
            self.dead = True
            self.velocity = Vector2(0, 0)
            for i in range(36):
                direction = Vector2(math.cos(math.radians(i * 10)), math.sin(math.radians(i * 10)))
                e = ExplosionParticle(self.state, self.position, 15, (200, 200, 255), direction * 1)
                e = ExplosionParticle(self.state, self.position, 10, (200, 200, 255), direction * 2)

    def draw(self):
        super().draw()


class EnemyBullet:
    def __init__(self, game: engine.GameState, center: Vector2):
        self.game = game
        self.center = center
        self.color = (255, 64, 64)
        self.size = Vector2(20, 20)
        self.hitbox = Rectangle(self.center - self.size / 2, self.size)
        self.dead = False
        self.friendly = False
        game.projectiles.append(self)

    def update(self):
        self.center += self.velocity
        if (self.center.y > self.game.game.resolution[1] + self.size.y / 2) or (self.center.y < -self.size.y / 2) \
                or (self.center.x > self.game.game.resolution[0] + self.size.x / 2) or (
                self.center.x < -self.size.x / 2):
            self.dead = True

        self.hitbox = Rectangle(self.center - self.size / 2, self.size)

    def draw(self):
        # circle
        self.game.renderer.draw_circle(Circle(self.center, self.size.x / 2), self.color)


# not a game object because it has collision with the player
class Enemy:
    def __init__(self, game: engine.GameState, center: Vector2):
        self.game = game
        self.center = center
        self.velocity = Vector2(0, 0)
        self.dead = False
        self.texture = pygame.image.load("assets/enemy.png")
        self.size = Vector2(90, 75)
        self.hitbox = Rectangle(self.center - self.size / 2, self.size)
        self.shootTimer = 0
        self.health = 1
        game.enemies.append(self)

    def update(self):
        self.center += self.velocity
        self.hitbox = Rectangle(self.center - self.size / 2, self.size)

        self.shootTimer += 1
        if self.shootTimer >= 60:
            target = self.game.player.position
            direction = (target - self.center).normalized()
            b = EnemyBullet(self.game, self.center + Vector2(0, self.size.y / 2))
            b.velocity = direction * 7
            self.shootTimer = 0

    def on_hit(self, entity):
        entity.dead = True
        self.health -= 1
        # directional particles
        dir = entity.velocity
        dirRot = dir.to_rotation()
        for i in range(30):
            rot = math.radians(random.randint(-15, 15))
            direction = Vector2(math.cos(dirRot + rot), math.sin(dirRot + rot)) * random.randint(1, 4)
            e = ExplosionParticle(self.game, self.center, random.randint(5, 8), (255, 200, 200), direction)
        if self.health <= 0:
            self.dead = True
            for i in range(36):
                direction = Vector2(math.cos(math.radians(i * 10)), math.sin(math.radians(i * 10)))
                e = ExplosionParticle(self.game, self.center, 15, (255, 200, 200), direction * 1)
                e = ExplosionParticle(self.game, self.center, 10, (255, 200, 200), direction * 2)
            p = PowerPickup(self.game, self.center)
            self.game.score += 100
        else:
            self.game.score += 10

    def draw(self):
        self.game.renderer.draw_img_centered(self.texture, self.center)


# will just go into the screen, shoot a few times, then go away and despawn
class AppearShootEnemy(Enemy):
    def __init__(self, game: engine.GameState, center: Vector2):
        super().__init__(game, center)
        self.velocity = Vector2(0, 5)
        self.actionTimer = 0
        self.health = 3

    def update(self):
        self.actionTimer += 1
        if self.actionTimer < 50:
            self.velocity.y -= 0.1
        elif self.actionTimer < 200:
            self.shootTimer += 1
            if self.shootTimer >= 30:
                target = self.game.player.position
                direction = (target - self.center).normalized()
                b = EnemyBullet(self.game, self.center + Vector2(0, self.size.y / 2))
                b.velocity = direction * 4
                self.shootTimer = 0
        elif self.actionTimer < 250:
            self.velocity.y -= 0.1
        else:
            self.dead = True
        self.center += self.velocity
        self.hitbox = Rectangle(self.center - self.size / 2, self.size)


# will simply go by the screen while slowly shooting
class WalkShootEnemy(Enemy):
    def __init__(self, game: engine.GameState, center: Vector2):
        super().__init__(game, center)
        self.velocity = Vector2(0, 0)
        self.actionTimer = 0
        self.health = 2

    def update(self):
        self.actionTimer += 1
        if self.actionTimer < 50:
            self.velocity.y += 0.1
        # if its Y level is close to the player's, it will shoot, and then not shoot again
        if abs(self.center.y - self.game.player.position.y) < 25 and self.shootTimer == 0:
            self.shootTimer = 1
            target = self.game.player.position
            direction = target.x > self.center.x and Vector2(1, 0) or Vector2(-1, 0)
            b = EnemyBullet(self.game, self.center + Vector2(0, self.size.y / 2))
            b.velocity = direction * 7

        if abs(self.center.x - self.game.player.position.x) < 25 and self.shootTimer == 0:
            self.shootTimer = 1
            target = self.game.player.position
            direction = target.y > self.center.y and Vector2(0, 1) or Vector2(0, -1)
            b = EnemyBullet(self.game, self.center + Vector2(0, self.size.y / 2))
            b.velocity = direction * 7

        self.center += self.velocity
        self.hitbox = Rectangle(self.center - self.size / 2, self.size)
        if self.center.y > self.game.game.resolution[1] + self.size.y / 2:
            self.dead = True


class EnemyLayout:
    def __init__(self, game: engine.GameState):
        self.game = game
        self.timer = 0

    def update(self):
        self.timer += 1


class EnemyLayout1(EnemyLayout):
    def __init__(self, game: engine.GameState):
        super().__init__(game)
        for i in range(3):
            pos = self.game.game.resolution[0] / 4 * (i + 1)
            e = AppearShootEnemy(self.game, Vector2(pos, -50))
        self.timer = 0

    def update(self):
        super().update()
        if self.timer == 200:
            for i in range(4):
                pos = self.game.game.resolution[0] / 5 * (i + 1)
                e = AppearShootEnemy(self.game, Vector2(pos, -50))
        if self.timer == 400:
            for i in range(5):
                pos = self.game.game.resolution[0] / 6 * (i + 1)
                e = AppearShootEnemy(self.game, Vector2(pos, -50))
        # repeat (placeholder)
        if self.timer == 600:
            self.game.currentEnemyLayout = EnemyLayout2(self.game)


class EnemyLayout2(EnemyLayout):
    def __init__(self, game: engine.GameState):
        super().__init__(game)
        self.timer2 = 0

    def update(self):
        super().update()
        self.timer2 += 1
        if self.timer2 == 100:
            self.timer2 = 0
            self.game.enemies.append(WalkShootEnemy(self.game, Vector2(50, 0)))
            self.game.enemies.append(WalkShootEnemy(self.game, Vector2(self.game.game.resolution[0] - 50, 0)))

        if self.timer == 200:
            for i in range(2):
                pos = self.game.game.resolution[0] / 3 * (i + 1)
                e = AppearShootEnemy(self.game, Vector2(pos, -50))
        if self.timer == 400:
            for i in range(3):
                pos = self.game.game.resolution[0] / 4 * (i + 1)
                e = AppearShootEnemy(self.game, Vector2(pos, -50))
        if self.timer == 600:
            for i in range(2):
                pos = self.game.game.resolution[0] / 3 * (i + 1)
                e = AppearShootEnemy(self.game, Vector2(pos, -50))
        if self.timer == 800:
            for i in range(3):
                pos = self.game.game.resolution[0] / 4 * (i + 1)
                e = AppearShootEnemy(self.game, Vector2(pos, -50))
        if self.timer == 1000:
            self.game.currentEnemyLayout = EnemyLayout3(self.game)


class EnemyLayout3(EnemyLayout):
    def __init__(self, game: engine.GameState):
        super().__init__(game)
        self.timer2 = 0
        self.direction = 1

    def update(self):
        super().update()
        self.timer2 += 1
        if self.timer2 == 75:
            self.timer2 = 0
            pos = self.direction == 1 and 50 or self.game.game.resolution[0] - 50
            self.game.enemies.append(WalkShootEnemy(self.game, Vector2(pos, 0)))
            self.direction *= -1
        start = self.game.game.resolution[0] / 8
        if self.timer == 75:
            e = AppearShootEnemy(self.game, Vector2(start, -50))
        if self.timer == 100:
            e = AppearShootEnemy(self.game, Vector2(start * 2, -50))
        if self.timer == 125:
            e = AppearShootEnemy(self.game, Vector2(start * 3, -50))
        if self.timer == 150:
            e = AppearShootEnemy(self.game, Vector2(start * 4, -50))
        if self.timer == 175:
            e = AppearShootEnemy(self.game, Vector2(start * 5, -50))
        if self.timer == 200:
            e = AppearShootEnemy(self.game, Vector2(start * 6, -50))
        if self.timer == 225:
            e = AppearShootEnemy(self.game, Vector2(start * 7, -50))


class GameState(engine.GameState):
    def __init__(self, game: engine.Game):
        super().__init__(game)
        self.starTimer = 0
        self.tutorialText = pygame.image.load("assets/tooltip_text.png")
        self.tutorialTimer = 120
        self.player = Player(self, Vector2(self.game.resolution[0] / 2, self.game.resolution[1] - 100))
        self.score = 0
        self.drawnScore = 0

        self.projectiles = []
        self.enemies = []
        self.currentEnemyLayout = EnemyLayout1(self)

    def initialize(self):
        super().initialize()

    def update(self):
        if self.tutorialTimer > 0:
            super().update()
        self.starTimer += 1
        if self.starTimer >= 5:
            self.starTimer = 0
            s = StarParticle(self, Vector2(random.randint(0, self.game.resolution[0]), -10), random.randrange(2, 5),
                             (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255)))
        super().update()

        if self.score != self.drawnScore:
            self.drawnScore += max(round((self.score - self.drawnScore) / 20), 1)
            if self.drawnScore > self.score:
                self.drawnScore = self.score

        if self.tutorialTimer > 0:
            return

        self.currentEnemyLayout.update()

        for p in self.projectiles:
            p.update()
            if p.friendly:
                for e in self.enemies:
                    if p.hitbox.intersects(e.hitbox):
                        e.on_hit(p)
            else:
                if p.hitbox.intersects(self.player.hitbox):
                    self.player.on_hit(p)
            if p.dead:
                self.projectiles.remove(p)

        for e in self.enemies:
            e.update()
            if e.hitbox.intersects(self.player.hitbox):
                self.player.on_hit(e)
            if e.dead:
                self.enemies.remove(e)

    def draw(self):
        self.renderer.fill((0, 0, 0))
        if self.tutorialTimer > 0:
            self.renderer.draw_img_centered(self.tutorialText,
                                            Vector2(self.game.resolution[0] / 2, self.game.resolution[1] / 2))
            self.tutorialTimer -= 1
        else:
            super().draw()
            for p in self.projectiles:
                p.draw()
            for e in self.enemies:
                e.draw()
            # to make sure the player is drawn on top of the stars
            if not self.player.immuneFrames % 4 != 0 and not self.player.dead:
                self.game.renderer.draw_img_centered(self.player.texture, self.player.position)
            elif self.player.dead:
                self.game.renderer.draw_text_centered("Game Over",
                                                      Vector2(self.game.resolution[0] / 2, self.game.resolution[1] / 2),
                                                      (255, 255, 255), pygame.font.SysFont("monospace", 60))

            # draw lives
            for i in range(self.player.lives):
                self.game.renderer.draw_img_centered(self.player.lifeTexture, Vector2(40 + i * 60, 40))

            # draw score
            self.game.renderer.draw_text_centered(str(self.drawnScore), Vector2(self.game.resolution[0] - 100, 40),
                                                  (255, 255, 255), pygame.font.SysFont("monospace", 60))


# will have a back button and fullscreen checkbox (for now)
class SettingsState(engine.GameState):
    def __init__(self, game: engine.Game):
        super().__init__(game)

    def initialize(self):
        super().initialize()
        font = pygame.font.SysFont("monospace", 60)
        back = Button(self, Vector2(self.game.resolution[0] / 2, 530), Vector2(400, 100), "Back", font, (133, 133, 133),
                      (200, 200, 200), (230, 230, 230))
        back.on_click = lambda: self.game.set_state(MenuState(self.game))
        checkbox = CheckBox(self, Vector2(self.game.resolution[0] / 2, 200), Vector2(50, 50), "Fullscreen", font,
                            (133, 133, 133), (200, 200, 200), (230, 230, 230))
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
