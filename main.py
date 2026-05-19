import pygame
import random
import sys

from Object import Object
from Scene import Scene

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True
dt = 0

Vector2 = pygame.math.Vector2

fntMain = pygame.font.Font("assets/alagard.ttf", 32)

__current_draw_color__ = pygame.Color(255, 255, 255, 255)

sprPlayer = pygame.image.load("assets/spaceship.png")

deaths = 0
killed = False

score = 0
hiscore = 0


def ButtonPressed(key):
    return pygame.key.get_pressed()[key]

def DrawSetColor(color):
    __current_draw_color__ = color

def DrawText(x, y, string, color = __current_draw_color__, font = fntMain):
    __textSurface = font.render(string, False, color)
    screen.blit(__textSurface, (x, y))

def DrawSprite(sprite, x, y):
    __imageSurface = sprite
    screen.blit(__imageSurface, (x, y))

def ChangeScene(scn):
    global scene
    scene = scn

def TimeToDie():
    global score
    global hiscore
    global player
    global deaths
    global killed

    if killed == True: pass
    if not scene.instanceExists(player): pass
    if player.invincible: pass

    killed = True
    #deaths += 1
    if deaths < 3:
        scene.destroyInstance(player)
        PlayerDeathEvent()
    else:
        print(f"died! score: {score} (hiscore: {hiscore}), deaths: {deaths}")
        pygame.quit()
        sys.exit(-2147483647)

class IntroMenu(Object):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.position.x = x
        self.position.y = y
    def update(self, dt):
        super().update(dt)
        if ButtonPressed(pygame.K_z):
            ChangeScene(GameScene())

    def render(self):
        DrawText(20, 20, "press Z key to continue")
        
class PlayerObject(Object):
    def __init__(self, x = SCREEN_WIDTH / 2, y = SCREEN_HEIGHT - 48):
        super().__init__(x, y)
        self.position.x = x
        self.position.y = y
        self.bbox = pygame.Rect(self.position.x, self.position.y, 32, 32)
        self.timer = 0
        self.invincible = True

        global killed
        killed = False
    mx = 0
    my = 0
    mvspeed = 120
    def update(self, dt):
        super().update(dt)
        self.bbox = pygame.Rect(self.position.x, self.position.y, 32, 32)

        self.timer += 1

        if self.timer > 75: self.invincible = False

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
        if not self.invincible: DrawSprite(sprPlayer, self.position.x, self.position.y)
        elif self.timer % 2 == 0: DrawSprite(sprPlayer, self.position.x, self.position.y)

class BulletObject(Object):
    def __init__(self, x, y, velocity = Vector2(0, 0)):
        super().__init__(x, y)
        self.velocity = velocity
        self.destroyOOB = False


    def update(self, dt):
        super().update(dt)
        self.bbox = pygame.Rect(self.position.x - 4, self.position.y - 4, 8, 8)

        if not scene.instanceExists(player): pass

        if self.bbox.colliderect(player.bbox):
            TimeToDie()
        if not self.bbox.colliderect(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)) and self.destroyOOB:
            scene.destroyInstance(self)
        pass
    def render(self):
        pygame.draw.circle(screen, (255, 255, 255), self.position, 8)

class BulletGeneratorObject(Object):
    def __init__(self, x = 0, y = 0):
        super().__init__(x, y)
        self.timer = 0


    def update(self, dt):
        super().update(dt)
        self.timer += 1
        #TODO: add bullets/enemies here
        if self.timer % 10 == 0:
            scene.addInstance(BulletObject(random.randint(12, 640 - 12), 5, Vector2(random.randint(-2, 2), random.randint(1, 3))))


    def render(self): pass

class EnemyObject(Object):
    def __init__(self, x, y, velocity = Vector2(0, 0)):
        super().__init__(x, y)
        self.velocity = velocity


    def update(self, dt):
        super().update(dt)
        self.bbox = pygame.Rect(self.position.x - 8, self.position.y - 8, 16, 16)
        
        if not scene.instanceExists(player): pass

        if self.bbox.colliderect(player.bbox):
            TimeToDie()
        if not self.bbox.colliderect(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)) and self.destroyOOB:
            scene.destroyInstance(self)
        pass
    def render(self):
        pygame.draw.circle(screen, (255, 255, 255), self.position, 16)


class PlayerDeathEvent(Object):
    def __init__(self, x = 0, y = 0):
        super().__init__(x, y)
        self.timer = 0


    def update(self, dt):
        super().update(dt)
        self.timer += 1

        if self.timer >= 5:
            global player
            player = PlayerObject()
            scene.addInstance(player)


    def render(self):

        pass

class GameOverEvent(Object):
    def __init__(self, x = 0, y = 0):
        super().__init__(x, y)
        self.timer = 0


    def update(self, dt):
        super().update(dt)
        self.timer += 1 * dt

    def render(self):
        DrawText(50, 50, "GAMEOVER")

player = PlayerObject()

class IntroMenuScene(Scene):
    instances = [
        IntroMenu(0, 0),
    ]

class GameScene(Scene):
    instances = [
        player,
        BulletGeneratorObject()
    ]



scene = IntroMenuScene()


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