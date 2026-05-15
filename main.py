import pygame
import random
import sys

from Object import Object
from Scene import Scene

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True
dt = 0

Vector2 = pygame.math.Vector2
    

class PlayerObject(Object):
    def __init__(self, x = SCREEN_WIDTH / 2, y = SCREEN_HEIGHT - 48):
        super().__init__(x, y)
        self.position.x = x
        self.position.y = y
        self.bbox = pygame.Rect(self.position.x, self.position.y, 32, 32)
    mx = 0
    my = 0
    mvspeed = 120
    def update(self, dt):
        super().update(dt)
        self.bbox = pygame.Rect(self.position.x, self.position.y, 32, 32)
        self.mx = 0
        self.my = 0
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            self.my = self.mvspeed * dt
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            self.mx = self.mvspeed * dt
        if pygame.key.get_pressed()[pygame.K_UP]:
            self.my = -self.mvspeed * dt
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            self.mx = -self.mvspeed * dt
        
        self.position.x += self.mx
        self.position.y += self.my

    def render(self):
        pygame.draw.rect(screen, 255, self.bbox)

class BulletObject(Object):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.velocity.y = 2.5
        self.destroyOOB = False


    def update(self, dt):
        super().update(dt)
        self.bbox = pygame.Rect(self.position.x, self.position.y, 32, 32)
        if self.bbox.colliderect(player.bbox):
            pygame.quit()
            sys.exit(-2147483647)
        if not self.bbox.colliderect(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)) and self.destroyOOB:
            scene.destroyInstance(self)
        pass
    def render(self):
        pygame.draw.rect(screen, (255, 98, 98), self.bbox)


player = PlayerObject()

class GameScene(Scene):
    instances = [
        player,
    ]
    for i in range(512):
        instances.append(BulletObject(random.randint(0, SCREEN_WIDTH), random.randint(0, 32)))


scene = GameScene()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill("black")

    scene.update(dt)
    scene.render()

    pygame.display.flip()
    dt = clock.tick(60) / 1000


pygame.quit()