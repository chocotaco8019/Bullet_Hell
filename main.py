import pygame
import random
import json
import sys
import os
import math
from pathlib import Path
from dataclasses import dataclass, field

from Object import Object
from Scene import Scene


DEBUG = True

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

PLAYFIELD_TOP_HEIGHT = 24
PLAYFIELD_LEFT_WIDTH = 24
PLAYFIELD_RIGHT_XPOS = 400
PLAYFIELD_BOTTOM_YPOS = 400

@dataclass
class TextAlign:
    h: str = "left"
    v: str = "top"

pygame.init()
pygame.font.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True
dt = 0
timescale = 1.0
lunatic = False


sndShoot = pygame.mixer.Sound("assets/sounds/shoot.wav")
sndDeath = pygame.mixer.Sound("assets/sounds/death.wav")

musTitle = pygame.mixer.Sound("assets/music/nightofnights.mp3")
musLevel1 = pygame.mixer.Sound("assets/music/deathbyglamour.mp3")
musJimmyBoss = pygame.mixer.Sound("assets/music/nightofnights.mp3")

channelMusic = pygame.mixer.Channel(1)
channelMusic.set_volume(1)

channelSFX = pygame.mixer.Channel(2)
channelSFX.set_volume(0.4)

Vector2 = pygame.math.Vector2

fntMain = pygame.font.Font("assets/alagard.ttf", 32)

__current_draw_color__ = pygame.Color(255, 255, 255, 255)

sprPlayer = pygame.image.load("assets/spaceship.png")
sprPlayerBullet = pygame.image.load("assets/mybullet.png")
sprBaseEnemy = pygame.image.load("assets/test_enemy.png")

deaths = 0
killed = False
gameover = False
timer = 0
conductor = 0

def BulletPattern(patternID, center = Vector2(0, 0), bulletCount = 8):
    if patternID == 1: # CircularPattern
        if lunatic == True:
            bulletCount *= 2.5
        for i in range(round(bulletCount)):
            radians = math.radians(360 / bulletCount) * i  # Evenly spaced angles

            scene.addInstance(BulletObject(center.x, center.y, Vector2(math.cos(radians) * 1.5, math.sin(radians) * 1.5)))
    elif patternID == 2: #
        pass
    else:
        print(f"unknown bullet pattern (patternID={patternID}) attempted spawn")

message = []

message.append("message test")

name = ""
score = 0
hiscores = 0
hiscoresJsonData = {}
#load hiscores
with open("C:\\Users\\nrider139327\\Documents\\" + "hiscores.json", "r") as fileid:
    hiscoresJsonData = fileid.read()

hiscores = json.loads(hiscoresJsonData)["scores"]

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def GetScoreAtIndex(idx = 0):
    _scores = []
    _names = []
    for player in hiscores:
        _scores.append(player['score'])
        _names.append(player['name'])
    
    #_scores.sort(reverse=True) #reversi
    lunaticStore = 0
    if lunatic: lunaticStore = 1
    return json.loads("{\"name\": \"" + str(_names[idx]) + "\", \"score\": " + str(_scores[idx]) + ", \"lunatic\": " + str(lunaticStore) + "}")

def SaveScore(name, score = score):
    global hiscoresJsonData
    global hiscores
    global lunatic
    lunaticStore = 0
    if lunatic: lunaticStore = 1
    with open("C:\\Users\\nrider139327\\Documents\\" + "hiscores.json", "w") as fileid:
        hiscores.append(json.loads("{\"name\": \"" + str(name) + "\", \"score\": " + str(score) + ", \"lunatic\": " + str(lunaticStore) + "}"))
        fileid.write("{\"scores\":" + json.dumps(hiscores) + "}")
    pygame.time.wait(100)

    #load hiscores
    with open("C:\\Users\\nrider139327\\Documents\\" + "hiscores.json") as fileid:
        hiscoresJsonData = fileid.read()
    hiscores = json.loads(hiscoresJsonData)["scores"]


def ButtonPressed(key):
    return pygame.key.get_pressed()[key]
    # for event in pygame.event.get():
    #     if event.type == pygame.KEYDOWN:
    #         return event.key == key

def ButtonHeld(key):
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
    scene.leave()
    scene = scn

def TimeToDie():
    global score
    global player
    global deaths
    global gameover

    if not scene.instanceExists(player): return
    if player.invincible: return

    scene.destroyInstance(player)

    channelSFX.play(sndDeath)

    deaths += 1
    if deaths < 3:
        scene.addInstance(PlayerDeathEvent(player.position.x, player.position.y))
    else:
        print(f"died! score: {score} (hiscore: {GetScoreAtIndex(0)['score']})")
        scene.addInstance(GameOverEvent())
        scene.destroyInstance(bulletgen)
        gameover = True
        musLevel1.fadeout(2500)

@dataclass
class TextConfig:
    position: Vector2
    size: float = 32
    font: pygame.font = fntMain
    bold: bool = False
    italic: bool = False
    text: str = ""
    color: pygame.Color = (255, 255, 255)
    alignment: TextAlign = field(default_factory=TextAlign)

class Text:
    def __init__(self, config):
        self.config = config
        self.surface = -1
        self.drawPosition = self.config.position.copy()

    def update(self, dt): pass

    def render(self):
        self.surface = self.config.font.render(self.config.text, False, self.config.color)

        if self.config.alignment.h == "left":   self.drawPosition.x = (self.config.position.x)
        if self.config.alignment.h == "center": self.drawPosition.x = (self.config.position.x - (pygame.font.Font.size(self.config.font, self.config.text)[0] / 2))
        if self.config.alignment.h == "right":  self.drawPosition.x = (self.config.position.x - (pygame.font.Font.size(self.config.font, self.config.text)[0]))

        if self.config.alignment.v == "top":    self.drawPosition.y = (self.config.position.y)
        if self.config.alignment.v == "middle": self.drawPosition.y = (self.config.position.y - (pygame.font.Font.size(self.config.font, self.config.text)[1] / 2))
        if self.config.alignment.v == "bottom": self.drawPosition.y = (self.config.position.y - (pygame.font.Font.size(self.config.font, self.config.text)[1]))

        screen.blit(self.surface, (self.drawPosition.x, self.drawPosition.y))

    def ChangeText(self, text):
        self.config.text = text
        self.render()
    
    def ChangeColor(self, color):
        self.config.color = color
        self.render()

        
class PlayerObject(Object):
    def __init__(self, x = (PLAYFIELD_LEFT_WIDTH + PLAYFIELD_RIGHT_XPOS) / 2 - 12, y = PLAYFIELD_BOTTOM_YPOS  - 64):
        super().__init__(x, y)
        self.position.x = x
        self.position.y = y
        
        self.bbox = pygame.Rect(self.position.x + 12, self.position.y + 18, 6, 9)
        self.timer = 0
        self.invincible = True

        global gameover
        global killed
        global timescale

        gameover = False
        killed = False
        timescale = 1.0
    mx = 0
    my = 0
    mvspeed = 200
    def update(self, dt):
        super().update(dt) 
        self.bbox = pygame.Rect(self.position.x + 12, self.position.y + 18, 6, 9)

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

        self.position.x = clamp(self.position.x, PLAYFIELD_LEFT_WIDTH, PLAYFIELD_RIGHT_XPOS - 24)
        self.position.y = clamp(self.position.y, PLAYFIELD_TOP_HEIGHT, PLAYFIELD_BOTTOM_YPOS - 36)

        if pygame.key.get_pressed()[pygame.K_z] and timer % 6 == 0 and self.timer > 0.5:
            scene.addInstance(PlayerBullet(self.position.x, self.position.y))
            channelSFX.stop()
            channelSFX.play(sndShoot)

    def render(self):
        if not self.invincible or timer % 2 == 0: DrawSprite(sprPlayer, self.position.x, self.position.y, (0.5, 0.5))

class PlayerBullet(Object):
    def __init__(self, x, y, velocity = Vector2(0, -8)):
        super().__init__(x, y)
        self.velocity = velocity
        self.destroyOOB = True


    def update(self, dt):
        super().update(dt)
        self.bbox = pygame.Rect(self.position.x, self.position.y, 6, 16)

        for instance in scene.instances:
            if instance.__class__.__name__ == "EnemyObject":
                if self.bbox.colliderect(instance.bbox):
                    global score
                    instance.hp -= 1
                    score += 10
                    scene.destroyInstance(self)
                    if instance.hp <= 0:
                        scene.destroyInstance(instance)

        if not self.bbox.colliderect(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)) and self.destroyOOB:
            scene.destroyInstance(self)

            
    def render(self):
       DrawSprite(sprPlayerBullet, self.position.x, self.position.y, (0.5, 0.5))

class BulletObject(Object):
    def __init__(self, x, y, velocity = Vector2(0, 0), size = random.randint(3, 5)):
        super().__init__(x, y)
        self.velocity = velocity
        self.destroyOOB = False
        self.size = size


    def update(self, dt):
        super().update(dt)
        self.bbox = pygame.Rect(self.position.x - (self.size / 2), self.position.y - (self.size / 2), self.size, self.size)

        if not scene.instanceExists(player): return

        if self.bbox.colliderect(player.bbox):
            TimeToDie()
        if not self.bbox.colliderect(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)) and self.destroyOOB:
            scene.destroyInstance(self)
            
    def render(self):
        pygame.draw.circle(screen, (255, 255, 255), self.position, self.size)

class BulletGeneratorObject(Object):
    def __init__(self, x = 0, y = 0):
        super().__init__(x, y)
        self.timer = 0


    def update(self, dt):
        super().update(dt)
        self.timer += 1
        #TODO: add bullets/enemies here


    def render(self): pass

class EnemyObject(Object):
    def __init__(self, x, y, sprite = sprBaseEnemy, velocity = Vector2(0, 0)):
        super().__init__(x, y)
        self.velocity = velocity
        self.hp = 1
        self.spriteIndex = sprite
        self.destroyOOB = False


    def update(self, dt):
        super().update(dt)
        self.bbox = pygame.Rect(self.position.x, self.position.y, 28, 28)

        randvalue = 400
        if lunatic: randvalue = 200
        if round(random.randint(0, randvalue)) == 1:
            BulletPattern(1, Vector2(self.position.x, self.position.y), 8)
        
        if not scene.instanceExists(player): return

        if self.bbox.colliderect(player.bbox):
            TimeToDie()
        if not self.bbox.colliderect(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)) and self.destroyOOB:
            scene.destroyInstance(self)
        pass
    def render(self):
        if self.spriteIndex != -1: DrawSprite(self.spriteIndex, self.position.x, self.position.y, (0.5, 0.5))
        else: pygame.draw.circle(screen, (255, 98, 27), self.position, 16)

class StarObject(Object):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.alpha = random.uniform(0.2, 0.8)
        self.distance = abs(conductor - y)
        self.size = random.uniform(0.2, 1.4)
    

    def update(self, dt):
        super().update(dt)
        self.position.y = (conductor - self.distance)

        if self.position.y >= PLAYFIELD_BOTTOM_YPOS:
            scene.addInstance(StarObject(random.randint(PLAYFIELD_LEFT_WIDTH, PLAYFIELD_RIGHT_XPOS), random.randint(0, PLAYFIELD_TOP_HEIGHT)))
            scene.destroyInstance(self)


    def render(self):
        pygame.draw.circle(screen, (255, 255, 255), self.position, self.size)
        # star = pygame.Surface((self.size, self.size))
        # star.set_alpha(self.alpha)
        # pygame.draw.circle(star, (255, 255, 255), (self.size / 2, self.size / 2), self.size)
        # screen.blit(star, (self.position.x, self.position.y))

class WriterObject(Object):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.timer = 0
        self.lock = 0
        self.strpos = 0
        self.text = message[0]
    

    def update(self, dt):
        super().update(dt)


    def render(self):

        pass

class PlayerDeathEvent(Object):
    def __init__(self, x = 0, y = 0):
        super().__init__(x, y)
        self.timer = 0
        self.circles = 12
        self.bullets = []
        self.animdone = False

        for i in range(self.circles):
            radians = math.radians((360 / self.circles) * i)
            bullet = BulletObject(self.position.x, self.position.y, Vector2(math.cos(radians) * 1.5, math.sin(radians) * 1.5), 2)
            self.bullets.append(bullet)
            scene.addInstance(bullet)


    def update(self, dt):
        super().update(dt)
        self.timer += 1 * dt

        if self.timer > 0.75 and not self.animdone:
            self.animdone = True
            for bullet in self.bullets:
                scene.destroyInstance(bullet)

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
        #scene.addInstance(Text(TextConfig()))
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
    def __init__(self):
        super().__init__()
        self.options = []
        self.options.append(Text(TextConfig(position=Vector2(320, 200), text="Start", alignment=TextAlign(h="center", v="top"))))
        self.options.append(Text(TextConfig(position=Vector2(320, 250), text="Leaderboard", alignment=TextAlign(h="center", v="top"))))
        self.options.append(Text(TextConfig(position=Vector2(320, 300), text="Quit", alignment=TextAlign(h="center", v="top"))))
        for i in self.options: self.addInstance(i)
    inputTimer = 0
    selected = 0
    menu = 0

    def update(self, dt):
        super().update(dt)
        self.inputTimer += 1 * dt
        if self.inputTimer < 0.5: return

        if ButtonPressed(pygame.K_UP):
            self.selected -= 1
            if self.selected <= -1:
                self.selected = len(self.options)
        if ButtonPressed(pygame.K_DOWN):
            self.selected += 1
            if self.selected >= len(self.options):
                self.selected = 0

        self.selected = clamp(self.selected, 0, len(self.options))


        if ButtonPressed(pygame.K_RETURN):
            if self.menu == 0:
                if self.selected == 0:
                    global lunatic
                    global score
                    lunatic = ButtonHeld(pygame.K_LSHIFT)
                    
                    score = 0
                    player = PlayerObject()
                    ChangeScene(GameScene())
                elif self.selected == 1:
                    self.menu = 1
                elif self.selected == 2:
                    pygame.quit()
                    sys.exit(0)
                else:
                    print(f"??? ({self.selected})")
            elif self.menu == 1:
                self.menu = 0
        
    def render(self):
        selectColor = pygame.Color(98, 255, 98)
        if ButtonHeld(pygame.K_LSHIFT): selectColor = pygame.Color(255, 0, 0)
        if self.menu == 0:
            for i in range(len(self.options)):
                if i == self.selected: self.options[i].ChangeColor(selectColor)
                else: self.options[i].ChangeColor(pygame.Color(255, 255, 255))
        elif self.menu == 1:
            for i in range(len(hiscores)):
                color = pygame.Color(255, 255, 255)
                if GetScoreAtIndex(i)["lunatic"]: color = pygame.Color(255, 0, 0)
                DrawText(50, 50 + (30 * i), GetScoreAtIndex(i)["name"] + " - " + str(GetScoreAtIndex(i)["score"]), color)

class GameScene(Scene):
    def __init__(self):
        super().__init__()
        channelMusic.play(musLevel1, 99999)

        self.textScore = Text(TextConfig(position=Vector2(PLAYFIELD_RIGHT_XPOS + ((SCREEN_WIDTH - PLAYFIELD_RIGHT_XPOS) / 2), 80), text="0000000", alignment=TextAlign(h="center", v="top"), size=32))
        self.textHiscore = Text(TextConfig(position=Vector2(PLAYFIELD_RIGHT_XPOS + ((SCREEN_WIDTH - PLAYFIELD_RIGHT_XPOS) / 2), 170), text="0000000", alignment=TextAlign(h="center", v="top"), size=32))
        self.instances = [
            player,
            bulletgen,
            Text(TextConfig(position=Vector2(PLAYFIELD_RIGHT_XPOS + ((SCREEN_WIDTH - PLAYFIELD_RIGHT_XPOS) / 2), 50), text="SCORE", alignment=TextAlign(h="center", v="top"), size=32, color=pygame.Color(255, 255, 0))),
            self.textScore,
            Text(TextConfig(position=Vector2(PLAYFIELD_RIGHT_XPOS + ((SCREEN_WIDTH - PLAYFIELD_RIGHT_XPOS) / 2), 140), text="HISCORE", alignment=TextAlign(h="center", v="top"), size=32, color=pygame.Color(255, 255, 0))),
            self.textHiscore,
        ]
        if lunatic: self.instances.append(Text(TextConfig(position=Vector2(PLAYFIELD_RIGHT_XPOS + ((SCREEN_WIDTH - PLAYFIELD_RIGHT_XPOS) / 2), 240), text="LUNATIC", alignment=TextAlign(h="center", v="top"), size=32, color=pygame.Color(255, 0, 0))))
        for i in range(64):
            self.instances.append(StarObject(random.randint(PLAYFIELD_LEFT_WIDTH, PLAYFIELD_RIGHT_XPOS), random.randint(PLAYFIELD_TOP_HEIGHT, PLAYFIELD_BOTTOM_YPOS)))



    def update(self, dt):
        global conductor
        super().update(dt)
        self.textScore.ChangeText(f"{score:07d}")
        if score < GetScoreAtIndex(0)['score']:
            self.textHiscore.ChangeText(f"{GetScoreAtIndex(0)['score']:07d}")
        else:
            self.textHiscore.ChangeText(f"{score:07d}")

        if gameover: return

        conductor += 45 * dt

        if timer % 30 == 0:
            self.addInstance(EnemyObject(random.randint(PLAYFIELD_LEFT_WIDTH, PLAYFIELD_RIGHT_XPOS), PLAYFIELD_TOP_HEIGHT - 24, sprBaseEnemy, Vector2(random.randint(-1, 1), 2)))

    def render(self):
        super().render()
        borderColor = (0, 0, 0)
        pygame.draw.rect(screen, borderColor, pygame.Rect(0, 0, SCREEN_WIDTH, PLAYFIELD_TOP_HEIGHT))
        pygame.draw.rect(screen, borderColor, pygame.Rect(0, 0, PLAYFIELD_LEFT_WIDTH, SCREEN_HEIGHT))
        pygame.draw.rect(screen, borderColor, pygame.Rect(0, PLAYFIELD_BOTTOM_YPOS, SCREEN_WIDTH, SCREEN_HEIGHT - PLAYFIELD_BOTTOM_YPOS))
        pygame.draw.rect(screen, borderColor, pygame.Rect(PLAYFIELD_RIGHT_XPOS, 0, SCREEN_WIDTH - PLAYFIELD_RIGHT_XPOS, SCREEN_HEIGHT))

        for instance in self.instances:
            if instance.__class__.__name__ == "Text":
                if instance.config.text != "GAMEOVER": instance.render()

    def leave(self):
        super().leave()
        channelMusic.stop()


class GameOverScene(Scene):
    def __init__(self):
        super().__init__()
        self.nameText = Text(TextConfig(position=Vector2(320, 130), text="", alignment=TextAlign(h="center", v="top"), size=32))
        self.addInstance(Text(TextConfig(position=Vector2(320, 20), text="Input your NAME.", alignment=TextAlign(h="center", v="top"), size=32)))
        self.addInstance(Text(TextConfig(position=Vector2(320, 55), text="(And press [RETURN] to continue.)", alignment=TextAlign(h="center", v="top"), size=16)))
        self.addInstance(self.nameText)

    def render(self):
        super().render()
        self.nameText.ChangeText(name)
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
                elif event.key == pygame.K_RETURN:
                    SaveScore(name, score)
                    ChangeScene(IntroMenuScene())
                    gameover = False
                    deaths = 0
                elif event.unicode.isalnum():
                    name += event.unicode
    
    screen.fill("black")
    timer += 1

    scene.update(dt)
    scene.render()

    pygame.display.flip()
    dt = clock.tick(60) / 1000


pygame.quit()