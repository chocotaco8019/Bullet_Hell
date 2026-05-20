import pygame
import random
import json
import sys

from Object import Object
from Scene import Scene

SCREEN_WIDTH = 640*2
SCREEN_HEIGHT = 480*2

pygame.init()
pygame.font.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True
dt = 0
timescale = 1.0

channelMusic = pygame.mixer.Channel(1)
channelSFX = pygame.mixer.Channel(2)

Vector2 = pygame.math.Vector2

fntMain = pygame.font.Font("assets/alagard.ttf", 32)

#musLevel1 = pygame.sound.Sound("assets/")

__current_draw_color__ = pygame.Color(255, 255, 255, 255)

sprPlayer = pygame.image.load("assets/spaceship.png")
sprBaseEnemy = pygame.image.load("assets/test_enemy.png")

deaths = 0
killed = False
timer = 0

name = ""
score = 0
hiscores = 0
hiscoresJsonData = {}

#load hiscores
fileid = open("hiscores.json")
hiscoresJsonData = fileid.read()
fileid.close()

hiscores = json.loads(hiscoresJsonData)["scores"]

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def GetScoreAtIndex(idx = 0):
    _scores = []
    _names = []
    for player in hiscores:
        _scores.append(player['score'])
        _names.append(player['name'])
    
    #_scores.sort(reverse=True) #reversi
    return json.loads("{\"name\": \"" + str(_names[idx]) + "\", \"score\": " + str(_scores[idx]) + "}")

def SaveScore(name, score = score):
    global hiscoresJsonData
    global hiscores
    fileid = open("hiscores.json", "w")
    hiscores.append(json.loads("{\"name\": \"" + str(name) + "\", \"score\": " + str(score) + "}"))
    fileid.write("{\"scores\":" + json.dumps(hiscores) + "}")
    fileid.close()
    pygame.time.wait(100)

    #load hiscores
    fileid = open("hiscores.json")
    hiscoresJsonData = fileid.read()
    fileid.close()
    hiscores = json.loads(hiscoresJsonData)["scores"]


def ButtonPressed(key):
    return pygame.key.get_pressed()[key]

def DrawSetColor(color):
    __current_draw_color__ = color

def DrawText(x, y, string, color = __current_draw_color__, font = fntMain):
    __textSurface = font.render(string, False, color)
    screen.blit(__textSurface, (x, y))

def DrawSprite(sprite, x, y, scale = (1, 1)):
    __imageSurface = sprite
    pygame.transform.scale(__imageSurface, scale)
    screen.blit(__imageSurface, (x, y))

def ChangeScene(scn):
    global scene
    scene = scn

def TimeToDie():
    global score
    global player
    global deaths

    if not scene.instanceExists(player): return
    if player.invincible: return

    scene.destroyInstance(player)

    deaths += 1
    if deaths < 3:
        scene.addInstance(PlayerDeathEvent())
    else:
        print(f"died! score: {score} (hiscore: {GetScoreAtIndex(0)["score"]})")
        scene.addInstance(GameOverEvent())
        scene.destroyInstance(bulletgen)
        
class PlayerObject(Object):
    def __init__(self, x = 256, y = 382):
        super().__init__(x, y)
        self.position.x = x
        self.position.y = y
        
        self.bbox = pygame.Rect(self.position.x, self.position.y, 24, 36)
        self.timer = 0
        self.invincible = True

        global killed
        global timescale

        killed = False
        timescale = 1.0
    mx = 0
    my = 0
    mvspeed = 200
    def update(self, dt):
        super().update(dt)
        self.bbox = pygame.Rect(self.position.x, self.position.y, 24, 36)

        self.timer += dt

        if self.timer > 2.5: self.invincible = False

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
        
        if pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_x]:
            self.mx /= 2
            self.my /= 2
        
        self.position.x += self.mx
        self.position.y += self.my

        self.position.x = clamp(self.position.x, 50, 500 - 24)
        self.position.y = clamp(self.position.y, 50, 425 - 36)

        if pygame.key.get_pressed()[pygame.K_z] and timer % 5 == 0 and self.timer > 0.5:
            scene.addInstance(PlayerBullet(self.position.x, self.position.y))

    def render(self):
        if not self.invincible or timer % 2 == 0: DrawSprite(sprPlayer, self.position.x, self.position.y, (0.5, 0.5))

class PlayerBullet(Object):
    def __init__(self, x, y, velocity = Vector2(0, -4)):
        super().__init__(x, y)
        self.velocity = velocity
        self.destroyOOB = False


    def update(self, dt):
        super().update(dt)
        self.bbox = pygame.Rect(self.position.x, self.position.y, 6, 16)

        for instance in scene.instances:
            if instance.__class__.__name__ == "EnemyObject":
                if self.bbox.colliderect(instance.bbox):
                    global score
                    instance.hp -= 1
                    score += 10
                    if instance.hp <= 0:
                        scene.destroyInstance(instance)

        if not self.bbox.colliderect(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)) and self.destroyOOB:
            scene.destroyInstance(self)

            
    def render(self):
        pygame.draw.rect(screen, (255, 255, 255), self.bbox, 8)

class BulletObject(Object):
    def __init__(self, x, y, velocity = Vector2(0, 0)):
        super().__init__(x, y)
        self.velocity = velocity
        self.destroyOOB = False


    def update(self, dt):
        super().update(dt)
        self.bbox = pygame.Rect(self.position.x - 4, self.position.y - 4, 8, 8)

        if not scene.instanceExists(player): return

        if self.bbox.colliderect(player.bbox):
            TimeToDie()
        if not self.bbox.colliderect(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)) and self.destroyOOB:
            scene.destroyInstance(self)
            
    def render(self):
        pygame.draw.circle(screen, (255, 255, 255), self.position, 8)

class BulletGeneratorObject(Object):
    def __init__(self, x = 0, y = 0):
        super().__init__(x, y)
        self.timer = 0


    def update(self, dt):
        super().update(dt)
        self.timer += 1
        if self.timer == 1: scene.addInstance(EnemyObject(250, 250))
        #TODO: add bullets/enemies here
        if self.timer % 10 == 0:
            scene.addInstance(BulletObject(random.randint(12, 640 - 12), 5, Vector2(random.randint(-2, 2), random.randint(1, 3))))


    def render(self): pass

class EnemyObject(Object):
    def __init__(self, x, y, sprite = sprBaseEnemy, velocity = Vector2(0, 0)):
        super().__init__(x, y)
        self.velocity = velocity
        self.hp = 20
        self.spriteIndex = sprite


    def update(self, dt):
        super().update(dt)
        self.bbox = pygame.Rect(self.position.x, self.position.y, 28, 28)
        
        if not scene.instanceExists(player): return

        if self.bbox.colliderect(player.bbox):
            TimeToDie()
        if not self.bbox.colliderect(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)) and self.destroyOOB:
            scene.destroyInstance(self)
        pass
    def render(self):
        if self.spriteIndex != -1: DrawSprite(self.spriteIndex, self.position.x, self.position.y, (0.5, 0.5))
        else: pygame.draw.circle(screen, (255, 98, 27), self.position, 16)


class PlayerDeathEvent(Object):
    def __init__(self, x = 0, y = 0):
        super().__init__(x, y)
        self.timer = 0


    def update(self, dt):
        super().update(dt)
        self.timer += 1 * dt

        if self.timer >= 3:
            global player
            player = PlayerObject()
            scene.addInstance(player)
            scene.destroyInstance(self)


    def render(self):

        pass

class GameOverEvent(Object):
    def __init__(self, x = 0, y = 0):
        super().__init__(x, y)
        self.timer = 0
        #SaveScore(input("Input your name. "), score)
        #pygame.quit()
        #sys.exit(-2147483647)


    def update(self, dt):
        super().update(dt)
        self.timer += 1 * dt

        if self.timer >= 6:
            ChangeScene(GameOverScene())

    def render(self):
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        bg.set_alpha(min(self.timer * 255, 255))
        bg.fill((0, 0, 0))
        screen.blit(bg, (0, 0))
        if self.timer >= 2:
            DrawText(min((self.timer - 2) * 500, 265 - (pygame.font.Font.size(fntMain, "GAMEOVER")[0] / 2)), 230, "GAMEOVER")

player = PlayerObject()
bulletgen = BulletGeneratorObject()

class IntroMenuScene(Scene):
    inputTimer = 0
    def update(self, dt):
        super().update(dt)
        self.inputTimer += 1 * dt

        if ButtonPressed(pygame.K_z) and self.inputTimer >= 0.5:
            ChangeScene(GameScene())
        
    def render(self):
        DrawText(20, 20, "press Z key to continue")

        for i in range(len(hiscores)):
            DrawText(50, 50 + (30 * i), GetScoreAtIndex(i)["name"] + " - " + str(GetScoreAtIndex(i)["score"]))

class GameScene(Scene):
    instances = [
        player,
        bulletgen
    ]

    def render(self):
        super().render()
        borderColor = (20, 20, 20)
        pygame.draw.rect(screen, borderColor, pygame.Rect(0, 0, SCREEN_WIDTH, 50))
        pygame.draw.rect(screen, borderColor, pygame.Rect(0, 0, 50, SCREEN_HEIGHT))
        pygame.draw.rect(screen, borderColor, pygame.Rect(0, 425, SCREEN_WIDTH, SCREEN_HEIGHT - 425))
        pygame.draw.rect(screen, borderColor, pygame.Rect(500, 0, SCREEN_WIDTH - 500, SCREEN_HEIGHT))

        DrawText(615 - (pygame.font.Font.size(fntMain, "SCORE")[0] / 2), 50, "SCORE")
        DrawText(615 - (pygame.font.Font.size(fntMain, str(score))[0] / 2), 80, str(score))
        DrawText(615 - (pygame.font.Font.size(fntMain, "HISCORE")[0] / 2), 140, "HISCORE")
        DrawText(615 - (pygame.font.Font.size(fntMain, str(GetScoreAtIndex(0)["score"]))[0] / 2), 170, str(GetScoreAtIndex(0)["score"]))


class GameOverScene(Scene):
    def render(self):
        super().render()
        DrawText(370 - (pygame.font.Font.size(fntMain, "Input your NAME.")[0] / 2), 40, "Input your NAME.")
        DrawText(370 - (pygame.font.Font.size(fntMain, "(And press [SHIFT] to continue.)")[0] / 2), 70, "(And press [SHIFT] to continue.)")
        DrawText(370 - (pygame.font.Font.size(fntMain, name)[0] / 2), 130, name)
        _lineY = (130 + pygame.font.Font.size(fntMain, name)[1] + 10)
        pygame.draw.line(screen, (255, 255, 255), (370 - (pygame.font.Font.size(fntMain, name)[0] / 2) - 10, _lineY), (370 + (pygame.font.Font.size(fntMain, name)[0] / 2) + 10, _lineY))


scene = IntroMenuScene()


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if scene.__class__.__name__ == "GameOverScene":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.key == pygame.K_LSHIFT:
                    SaveScore(name, score)
                    ChangeScene(IntroMenuScene())
                elif event.unicode.isalnum():
                    name += event.unicode
    
    screen.fill("black")
    timer += 1

    scene.update(dt)
    scene.render()

    pygame.display.flip()
    dt = clock.tick(60) / 1000


pygame.quit()