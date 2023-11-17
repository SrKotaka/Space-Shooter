import math
from random import random

import pygame
from pygame.locals import *
import sys

pygame.init()
width = 1000
height = 750
display = pygame.display.set_mode((width, height))
FPS = pygame.time.Clock()
FPS.tick(60)
pygame.display.set_caption("Space Shooters")
UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3
SPACE = 4
keys = [False, False, False, False, False]

spaceship = pygame.image.load("assets/spaceship.png")

class SuperspeedParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.oldPos = (self.x, self.y)
        self.color = (120, 120, 120)

    def draw(self, screen: pygame.Surface):
        dir = pygame.math.Vector2(self.x - self.oldPos[0], self.y - self.oldPos[1])
        pygame.draw.line(screen, self.color, (self.x, self.y), (self.x + dir.x * 10, self.y + dir.y * 10), 2)

    def update(self):
        center = (width / 2, height / 2)
        self.oldPos = (self.x, self.y)
        self.x += (self.x - center[0]) / 10
        self.y += (self.y - center[1]) / 10


class Player:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.realSizeX = 69
        self.realSizeY = 44
        self.centerSizeX = 26
        self.color = color
        self.velocityX = 0
        self.velocityY = 0
        self.oldPos = [(self.x, self.y)]
        self.shootCooldown = 0
        self.hitbox = pygame.Rect(self.x - self.centerSizeX / 2, self.y - self.centerSizeX / 2, self.centerSizeX,
                                  self.centerSizeX)

    def draw(self, screen: pygame.Surface):
        for i in range(len(self.oldPos) - 1):
            progress = i / len(self.oldPos)
            pygame.draw.circle(screen, (255 * progress, (1 - progress) * 255 * progress, 0),
                               (self.oldPos[i][0], self.oldPos[i][1] - 10), self.realSizeY / 3.5 * progress)
        screen.blit(spaceship, (self.x - self.realSizeX / 2, self.y - self.realSizeY / 2))
        pygame.draw.rect(screen, (255, 0, 0), self.hitbox)

    def tryshoot(self):
        if self.shootCooldown <= 0:
            self.shootCooldown = 10
            projectiles.append(Projectile(self.x, self.y - self.realSizeY / 2, 10, (255, 0, 0), (0, -10)))

    def update(self):
        self.x += self.velocityX
        self.y += self.velocityY
        self.shootCooldown -= 1
        self.velocityX *= 0.85
        self.velocityY *= 0.85

        if self.x > width - self.realSizeX / 2:
            self.x = width - self.realSizeX / 2
        if self.x < self.realSizeX / 2:
            self.x = self.realSizeX / 2
        if self.y > height - self.realSizeY / 2:
            self.y = height - self.realSizeY / 2
        if self.y < self.realSizeY / 2:
            self.y = self.realSizeY / 2

        self.hitbox = pygame.Rect(self.x - self.centerSizeX / 2, self.y - self.centerSizeX / 2, self.centerSizeX,
                                    self.centerSizeX)

        self.oldPos.append((self.x, self.y + self.realSizeY / 2))
        if len(self.oldPos) > 15:
            self.oldPos.pop(0)
        for i in range(len(self.oldPos) - 1):
            progress = i / len(self.oldPos)
            self.oldPos[i] = (self.oldPos[i][0] + 1 * math.sin(i + pygame.time.get_ticks() / 200), self.oldPos[i][1])
            self.oldPos[i] = (self.oldPos[i][0] + (self.oldPos[i + 1][0] - self.oldPos[i][0]) * progress,
                              self.oldPos[i][1] + (self.oldPos[i + 1][1] - self.oldPos[i][1]) * progress + 3.5)


class Projectile:
    def __init__(self, x, y, size, color, velocity):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.velocity = velocity
        self.oldPos = [(self.x, self.y)]
        self.hitbox = pygame.Rect(self.x - self.size / 2, self.y - self.size / 2, self.size, self.size)
        self.friendly = True
        self.timeLeft = 100

    def draw(self, screen: pygame.Surface):
        pygame.draw.line(screen, self.color, (self.x, self.y - self.size / 2), (self.x, self.y + self.size / 2),
                         int(self.size / 2))
        for i in range(len(self.oldPos) - 1):
            progress = i / len(self.oldPos)
            pygame.draw.line(screen, (255 * progress, (1 - progress) * 255 * progress, 0),
                             (self.oldPos[i][0], self.oldPos[i][1] - 10), (self.oldPos[i][0], self.oldPos[i][1] + 10),
                             int(self.size / 2 * progress))

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.hitbox = pygame.Rect(self.x - self.size / 2, self.y - self.size / 2, self.size, self.size)
        self.oldPos.append((self.x, self.y))
        if len(self.oldPos) > 10:
            self.oldPos.pop(0)
        self.timeLeft -= 1
        if self.timeLeft <= 0:
            try:
                projectiles.remove(self)
            except ValueError:
                pass


class EnergyOrb(Projectile):
    def __init__(self, x, y, size, color, velocity):
        super().__init__(x, y, size, color, velocity)
        self.hitbox = pygame.Rect(self.x - self.size / 2, self.y - self.size / 2, self.size, self.size)
        self.oldPos = [(self.x, self.y)]
        self.color = (255, 255, 0)
        self.friendly = False
        self.timeLeft = 150

    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size / 2)
        for i in range(len(self.oldPos) - 1):
            progress = i / len(self.oldPos)
            pygame.draw.circle(screen, self.color, self.oldPos[i], self.size / 2 * progress)

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.hitbox = pygame.Rect(self.x - self.size / 2, self.y - self.size / 2, self.size, self.size)
        self.oldPos.append((self.x, self.y))
        if len(self.oldPos) > 10:
            self.oldPos.pop(0)

        # home slightly
        playerPos = (player.x, player.y)
        targetDirection = pygame.math.Vector2(playerPos[0] - self.x, playerPos[1] - self.y)
        if targetDirection.length() < 175:
            length = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)
            currentRotation = math.atan2(self.velocity[1], self.velocity[0])
            targetRotation = math.atan2(targetDirection[1], targetDirection[0])
            if targetRotation - currentRotation > math.pi:
                currentRotation += 2 * math.pi
            if targetRotation - currentRotation < -math.pi:
                currentRotation -= 2 * math.pi
            currentRotation += (targetRotation - currentRotation) / 85
            self.velocity = (length * math.cos(currentRotation), length * math.sin(currentRotation))

        # check for collision with player
        if self.hitbox.colliderect(player.hitbox):
            player.velocityX += self.velocity[0] / 2
            player.velocityY += self.velocity[1] / 2
            projectiles.remove(self)

        self.timeLeft -= 1
        if self.timeLeft <= 0:
            try:
                projectiles.remove(self)
            except ValueError:
                pass

# GAME
# class Enemy:

# class MotherShip:

# class Life:

# MENU GAME
# class RestartGame:

playerX = width / 2
playerY = height / 2
BLUE = (0, 0, 255)

player = Player(playerX, playerY, BLUE)
projectiles = []
particles = []
rot = 0
frames = 0
paused = False
while True:
    frames += 1
    


    # will spawn a circling energy orb every 10 frames
    display.fill((0, 0, 0))
    if not paused:
        for i in range(4):
            angle = i / 2 * math.pi + rot
            rot += math.sin(pygame.time.get_ticks() / 2000) / 200
            spawnX = width / 2
            spawnY = height / 2
            if frames % 3 == 0:
                projectiles.append(EnergyOrb(spawnX, spawnY, 10, (255, 255, 0), (6 * math.cos(angle), 6 * math.sin(angle))))

        for projectile in projectiles:
            projectile.update()

        for i in range(1):
            radius = random() * 50 + 300
            angle = random() * 2 * math.pi
            spawnX = width / 2 + radius * math.cos(angle)
            spawnY = height / 2 + radius * math.sin(angle)
            particles.append(SuperspeedParticle(spawnX, spawnY))

        for particle in particles:
            particle.update()
            if particle.y < 0 or particle.y > height or particle.x < 0 or particle.x > width:
                try:
                    particles.remove(particle)
                except ValueError:
                    pass

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == K_w or event.key == K_UP:
                    keys[0] = False
                if event.key == K_s or event.key == K_DOWN:
                    keys[1] = False
                if event.key == K_a or event.key == K_LEFT:
                    keys[2] = False
                if event.key == K_d or event.key == K_RIGHT:
                    keys[3] = False
                if event.key == K_SPACE:
                    keys[4] = False
                if event.key == K_p:
                    paused = not paused
            if event.type == KEYDOWN:
                if event.key == K_w or event.key == K_UP:
                    keys[0] = True
                if event.key == K_s or event.key == K_DOWN:
                    keys[1] = True
                if event.key == K_a or event.key == K_LEFT:
                    keys[2] = True
                if event.key == K_d or event.key == K_RIGHT:
                    keys[3] = True
                if event.key == K_SPACE:
                    keys[4] = True
        if keys[1]:
            player.velocityY += 1
        if keys[0]:
            player.velocityY -= 1
        if keys[2]:
            player.velocityX -= 1
        if keys[3]:
            player.velocityX += 1
        if keys[4]:
            player.tryshoot()

        player.update()


    for event in pygame.event.get():
        if event.type == KEYUP:
            if event.key == K_p:
                paused = not paused
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    for particle in particles:
        particle.draw(display)

    for projectile in projectiles:
        projectile.draw(display)
    player.draw(display)
    if paused:
        #pause menu
        # draw text "paused"
        # draw text "press p to unpause"
        pygame.draw.rect(display, (255, 255, 255), (width / 2 - 200, height / 2 - 50, 400, 150))
        font = pygame.font.SysFont("Arial", 50)
        text = font.render("Paused", True, (0, 0, 0))
        display.blit(text, (width / 2 - text.get_width() / 2, height / 2 - text.get_height() / 2))
        text = font.render("Press P to unpause", True, (0, 0, 0))
        display.blit(text, (width / 2 - text.get_width() / 2, height / 2 - text.get_height() / 2 + 50))
    pygame.display.update()
    FPS.tick(60)
