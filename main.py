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


DEBUG = False

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

PLAYFIELD_TOP_HEIGHT = 24
PLAYFIELD_LEFT_WIDTH = 24
PLAYFIELD_RIGHT_XPOS = 400
PLAYFIELD_BOTTOM_YPOS = 400
PLAYFIELD_WIDTH = (PLAYFIELD_RIGHT_XPOS - PLAYFIELD_LEFT_WIDTH)
PLAYFIELD_HEIGHT = (PLAYFIELD_BOTTOM_YPOS - PLAYFIELD_TOP_HEIGHT)
PLAYFIELD_MIDDLE_XPOS = (PLAYFIELD_LEFT_WIDTH + (PLAYFIELD_WIDTH / 2))
PLAYFIELD_MIDDLE_XPOS = (PLAYFIELD_TOP_HEIGHT + (PLAYFIELD_HEIGHT / 2))

HISCORES_FILE = "C:\\Users\\nrider139327\\Documents\\hiscores.json"

@dataclass
class TextAlign:
    h: str = "left"
    v: str = "top"

pygame.init()
pygame.font.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
pygame.display.set_caption("CNA Galaxy")
clock = pygame.time.Clock()
running = True
dt = 0

lunatic = False
endless = False
action = 0
timescale = 1.0
textbox = -1
jimmyboss = -1
jimmyspawned = False
myScoreNow = False
scoreAdd = 0


sprPlayer = pygame.image.load("assets/spaceship.png")
sprPlayerBullet = pygame.image.load("assets/mybullet.png")
sprBaseEnemy = pygame.image.load("assets/test_enemy.png")
sprJimmyBoss = pygame.image.load("assets/Jimmybot.png")

sndShoot = pygame.mixer.Sound("assets/sounds/shoot.wav")
sndDeath = pygame.mixer.Sound("assets/sounds/death.wav")

musTitle = pygame.mixer.Sound("assets/music/nightofnights.mp3")
musLevel1 = pygame.mixer.Sound("assets/music/deathbyglamour.mp3")
#musLevel1 = pygame.mixer.Sound("assets/music/testsong.ogg")
musJimmyBoss = pygame.mixer.Sound("assets/music/nightofnights.mp3")

channelMusic = pygame.mixer.Channel(1)
channelMusic.set_volume(1)

channelSFX = pygame.mixer.Channel(2)
channelSFX.set_volume(0.4)

Vector2 = pygame.math.Vector2

fntMain = pygame.font.Font("assets/alagard.ttf", 32)
fntMainSmol = pygame.font.Font("assets/alagard.ttf", 16)

__current_draw_color__ = pygame.Color(255, 255, 255, 255)
deaths = 0
killed = False
gameover = False
timer = 0
conductor = 0

def AddScore(scoreToAdd):
    scoreToAdd = round(scoreToAdd)
    global scoreAdd
    scoreAdd = scoreToAdd

def BulletPattern(patternID, center = Vector2(0, 0), bulletCount = 8):
    global player
    if patternID == 1: # CircularPattern
        if lunatic == True:
            bulletCount *= 1.75
        for i in range(round(bulletCount)):
            radians = math.radians(360 / bulletCount) * i  # Evenly spaced angles

            scene.addInstance(BulletObject(center.x, center.y, Vector2(math.cos(radians) * 1.5, math.sin(radians) * 1.5), 3))
    elif patternID == 2: # ShootToPlayer
        distX = (player.position.x - center.x)
        distY = (player.position.y - center.y)
        distance = math.sqrt((distX * distX) + (distY * distY))
        dirX = distX / distance
        dirY = distY / distance

        scene.addInstance(BulletObject(center.x, center.y, Vector2(dirX * 3, dirY * 3), 3))
        if lunatic == True:
            pass
    else:
        print(f"unknown bullet pattern (patternID={patternID}) attempted spawn")

message = []
for n in range(64): message.append("%%")

name = ""
score = 0
hiscores = []
hiscoresJsonData = {}
#load hiscores
def LoadHiscores():
    global hiscoresJsonData
    global hiscores
    with open(HISCORES_FILE, "r") as fileid:
        hiscoresJsonData = fileid.read()

    hiscores = json.loads(hiscoresJsonData)["scores"]

    for hiscore in hiscores:
        if not "lunatic" in hiscore.keys(): hiscore["lunatic"] = 0
        if not "endless" in hiscore.keys(): hiscore["endless"] = 0

LoadHiscores()

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def GetScoreAtIndex(idx = 0):
    _scores = sorted(
        hiscores,
        key=lambda player: player["score"],
        reverse=True,
    ) #reversi!!!!!
    return _scores[idx]

def SaveScore(name, score = score):
    global hiscoresJsonData
    global hiscores
    global lunatic
    iAmALunatic = 0
    if lunatic: iAmALunatic = 1
    iAmEndless = 0
    if endless: iAmEndless = 1
    with open(HISCORES_FILE, "w") as fileid:
        hiscores.append(json.loads("{\"name\": \"" + str(name) + "\", \"score\": " + str(score) + ", \"lunatic\": " + str(iAmALunatic) + ", \"endless\": " + str(iAmEndless) + "}"))
        fileid.write("{\"scores\":" + json.dumps(hiscores) + "}")
    pygame.time.wait(100)

    #load hiscores
    LoadHiscores()


pressedKeys = set()

def UpdateEvents():
    pressedKeys.clear()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: return False

        if event.type == pygame.KEYDOWN: pressedKeys.add(event.key)

        if scene.__class__.__name__ == "GameOverScene":
            global gameover
            global deaths
            global name
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.key == pygame.K_RETURN:
                    if name != "": SaveScore(name, score)
                    ChangeScene(IntroMenuScene())
                    gameover = False
                    deaths = 0
                elif event.unicode.isalnum():
                    name += event.unicode

    return True

def ButtonPressed(key):
    return key in pressedKeys

def ButtonHeld(key):
    return pygame.key.get_pressed()[key]

def ConfirmKeyPressed():
    return ButtonPressed(pygame.K_z) or ButtonPressed(pygame.K_RETURN)

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
        
    def destroy(self): pass

        
class PlayerObject(Object):
    def __init__(self, x = (PLAYFIELD_LEFT_WIDTH + PLAYFIELD_RIGHT_XPOS) / 2 - 12, y = PLAYFIELD_BOTTOM_YPOS  - 64):
        super().__init__(x, y)
        self.position.x = x
        self.position.y = y
        
        self.bbox = pygame.Rect(self.position.x + 8, self.position.y + 12, 8, 16)
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
        global action
        self.bbox = pygame.Rect(self.position.x + 8, self.position.y + 12, 8, 16)

        self.timer += dt

        if self.timer > 2.5: self.invincible = False
        if action > 0: return

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
            scene.addInstance(PlayerBullet(self.position.x + 7, self.position.y - 2))
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
                    global lunatic
                    instance.hp -= 1
                    scoreToAdd = 250
                    if lunatic: scoreToAdd *= 1.75
                    AddScore(scoreToAdd)
                    if instance.hp <= 0:
                        scene.destroyInstance(instance)
                    scene.destroyInstance(self)

        if not self.bbox.colliderect(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)) and self.destroyOOB:
            scene.destroyInstance(self)

            
    def render(self):
       DrawSprite(sprPlayerBullet, self.position.x, self.position.y, (0.5, 0.5))

class BulletObject(Object):
    def __init__(self, x, y, velocity = Vector2(0, 0), size = random.randint(3, 5)):
        super().__init__(x, y)
        self.velocity = velocity
        self.destroyOOB = True
        self.size = size


    def update(self, dt):
        super().update(dt)
        self.bbox = pygame.Rect(self.position.x - (self.size / 2), self.position.y - (self.size / 2), self.size, self.size)
        global action

        if not self.bbox.colliderect(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)) and self.destroyOOB:
            scene.destroyInstance(self)

        if scene.instanceExists(player) == False or player.invincible == True or gameover == True: return

        if self.bbox.colliderect(player.bbox) and action == 0:
            TimeToDie()
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
        self.spawnBullets = True
        self.spriteIndex = sprite
        self.destroyOOB = True
        self.pattern = round(random.randint(1, 2))


    def update(self, dt):
        super().update(dt)
        self.bbox = pygame.Rect(self.position.x, self.position.y, 28, 28)

        randvalue = 275
        if lunatic: randvalue = 100
        if round(random.randint(0, randvalue)) == 1 and self.spawnBullets == True:
            BulletPattern(self.pattern, Vector2(self.position.x, self.position.y), 8)
        
        if not scene.instanceExists(player): return

        if self.bbox.colliderect(player.bbox):
            TimeToDie()
        if not self.bbox.colliderect(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)) and self.destroyOOB:
            scene.destroyInstance(self)
        pass
    def render(self):
        if self.spriteIndex != -1: DrawSprite(self.spriteIndex, self.position.x, self.position.y, (0.5, 0.5))
        else: pygame.draw.circle(screen, (255, 98, 27), self.position, 16)

class JimmyBossObject(EnemyObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hp = 1000
        self.spawnBullets = False
        self.spriteIndex = sprJimmyBoss
        self.timer = 0
        self.angle = 0
        self.stage = 0
        self.radius = 50
        self.inctimer = True
        self.talked = []
        self.finishtalk = []
        for i in range(5): self.talked.append(False)
        for i in range(5): self.finishtalk.append(False)


    def update(self, dt):
        super().update(dt)
        global action
        global textbox
        self.bbox = pygame.Rect(self.position.x, self.position.y, 80, 88)
        if self.stage == 0: self.position.y += math.sin(timer / 16) * 2
        if self.inctimer: self.timer += 1 * dt

        if self.timer >= 2 and scene.instanceExistsByName("EnemyObject") == False:
            if self.talked[0] == False:
                self.talked[0] = True
                self.inctimer = False
                action = 1
                message[0] = "You know...\nI've been expecting you."
                message[1] = "Time to settle this...\n#cRJIMMY STYLE#cX!"
                message[2] = "Prepare yourself, mortal!"
                message[3] = "I didn't get this powerful\nby being nice."
                message[4] = "Let's dance."
                textbox = TextboxObject()
                scene.addInstance(textbox)
            elif scene.instanceExists(textbox) == False and self.finishtalk[0] == False:
                self.finishtalk[0] = True
                action = 0
                channelMusic.play(musJimmyBoss)
                self.timer = 0
                self.stage = 1

        if self.stage == 1:
            self.angle += 0.16
            self.position.x += math.cos((self.angle) / 4) * self.radius * 0.08
            self.position.y += math.sin((self.angle * 2) / 4) * self.radius * 0.12

            wait = 16
            if lunatic: wait = 30
            if timer % wait == 0:
                bulletnum = 16
                if lunatic: bulletnum = 20
                BulletPattern(1, Vector2(self.position.x + 40, self.position.y + 44), bulletnum)



    def render(self):
        if self.spriteIndex != -1: DrawSprite(self.spriteIndex, self.position.x, self.position.y)

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

class TextboxObject(Object):
    def __init__(self, x = (PLAYFIELD_LEFT_WIDTH + 24), y = (PLAYFIELD_BOTTOM_YPOS - 128), lock = 1):
        super().__init__(x, y)
        self.lock = lock # if 1, you can press z to skip to the next page
        self.text = message[0]
        self.pageno = 0
        self.writex = x
        self.writey = y
        self.hspacing = 12
        self.vspacing = 30
        self.textsize = 16
        self.char = " "
        
    

    def update(self, dt):
        super().update(dt)
        
        if ConfirmKeyPressed() and self.lock == 1:
            self.pageno += 1
            self.text = message[self.pageno]
            if self.text == "%%":
                scene.destroyInstance(self)


    def render(self):
        xx = self.writex
        yy = self.writey
        color = pygame.Color(255, 255, 255)
        for n in range(len(self.text)):
            self.char = self.text[n]

            if self.char == "#":
                if self.text[n + 1] == "c":
                    if self.text[n + 2] == "R": color = pygame.Color(255, 0, 0)
                    if self.text[n + 2] == "G": color = pygame.Color(0, 255, 0)
                    if self.text[n + 2] == "B": color = pygame.Color(0, 0, 255)
                    if self.text[n + 2] == "W": color = pygame.Color(255, 255, 255)
                    if self.text[n + 2] == "X": color = pygame.Color(255, 255, 255)
                    continue
            if n > 0:
                if self.char == "c" and self.text[n - 1] == "#":
                    continue
                if self.text[n - 1] == "c" and self.text[n - 2] == "#":
                    continue

            if self.char == "\n":
                xx = self.writex
                yy += self.vspacing
                continue

            DrawText(xx, yy, self.char, color, fntMainSmol)
            xx += self.hspacing

    def destroy(self):
        for n in range(64): message.append("%%")


class AlertObject(Object):
    def __init__(self, text = "", x = PLAYFIELD_RIGHT_XPOS, y = PLAYFIELD_TOP_HEIGHT + 12, color = pygame.Color(255, 255, 255)):
        super().__init__(x, y)
        self.text = text
        self.textObject = Text(TextConfig(position=Vector2(x, y), text=text, color=color, alignment=TextAlign(h="center", v="top")))
        scene.addInstance(self.textObject)
        self.flyin = True
        self.flyout = False
        self.timer = 0
        self.wait = 0


    def update(self, dt):
        self.timer += 1 * dt

        if self.wait > 0:
            if abs(self.wait - self.timer) >= 3: self.flyout = True

        if self.flyin == True:
            self.textObject.config.position.x -= 512 * dt
            if self.textObject.config.position.x <= ((PLAYFIELD_LEFT_WIDTH + PLAYFIELD_RIGHT_XPOS) / 2):
                self.textObject.config.position.x = ((PLAYFIELD_LEFT_WIDTH + PLAYFIELD_RIGHT_XPOS) / 2)
                self.flyin = False
                self.wait = self.timer

        if self.flyout == True:
            self.textObject.config.position.x -= 512 * dt
            if self.textObject.config.position.x <= PLAYFIELD_LEFT_WIDTH:
                scene.destroyInstance(self.textObject)
                scene.destroyInstance(self)



    def render(self): pass


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
        self.gameoverText = Text(TextConfig(position=Vector2(-200, PLAYFIELD_TOP_HEIGHT + (PLAYFIELD_HEIGHT / 2)), text="GAMEOVER", alignment=TextAlign(h="center", v="middle")))
        scene.addInstance(self.gameoverText)


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
            self.gameoverText.config.position.x = min((self.timer - 2) * 500, (PLAYFIELD_LEFT_WIDTH + (PLAYFIELD_WIDTH / 2)))

player = PlayerObject()
bulletgen = BulletGeneratorObject()

class IntroMenuScene(Scene):
    def __init__(self):
        super().__init__()
        self.options = []
        self.options.append(Text(TextConfig(position=Vector2(320, 250), text="Start", alignment=TextAlign(h="center", v="top"))))
        self.options.append(Text(TextConfig(position=Vector2(320, 300), text="Endless", alignment=TextAlign(h="center", v="top"))))
        self.options.append(Text(TextConfig(position=Vector2(320, 350), text="Leaderboard", alignment=TextAlign(h="center", v="top"))))
        #self.options.append(Text(TextConfig(position=Vector2(320, 400), text="Tutorial", alignment=TextAlign(h="center", v="top"))))
        self.options.append(Text(TextConfig(position=Vector2(320, 400), text="Quit", alignment=TextAlign(h="center", v="top"))))
        for i in range(len(self.options)):
            self.addInstance(self.options[i])
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


        if ConfirmKeyPressed():
            global lunatic
            global score
            global name
            global player
            global jimmyboss
            global endless
            global gameover
            if self.menu == 0:
                if self.selected == 0:
                    lunatic = ButtonHeld(pygame.K_LSHIFT)
                    
                    name = ""
                    score = 0
                    jimmyboss = -1
                    gameover = False
                    player = PlayerObject()
                    ChangeScene(GameScene())
                elif self.selected == 1:
                    lunatic = ButtonHeld(pygame.K_LSHIFT)
                    
                    endless = True

                    name = ""
                    score = 0
                    jimmyboss = -1
                    gameover = False
                    player = PlayerObject()
                    ChangeScene(GameScene())
                elif self.selected == 2:
                    self.menu = 2
                elif self.selected == 3:
                    pygame.quit()
                    sys.exit(0)
                else:
                    print(f"??? ({self.selected})")
            else: self.menu = 0
        
    def render(self):
        selectColor = pygame.Color(98, 255, 98)
        if ButtonHeld(pygame.K_LSHIFT): selectColor = pygame.Color(255, 0, 0)
        if self.menu == 0:
            for i in range(len(self.options)):
                if i == self.selected: self.options[i].ChangeColor(selectColor)
                else: self.options[i].ChangeColor(pygame.Color(255, 255, 255))
        elif self.menu == 2:
            for i in range(len(hiscores)):
                color = pygame.Color(255, 255, 255)
                if GetScoreAtIndex(i)["lunatic"] == 1: color = pygame.Color(255, 0, 0)
                text = GetScoreAtIndex(i)["name"] + " - " + str(GetScoreAtIndex(i)["score"])
                if GetScoreAtIndex(i)["endless"] == 1: text += " (endless)"
                DrawText(50, 50 + (30 * i), text, color)
        elif self.menu == 2:
            pass

class GameScene(Scene):
    def __init__(self):
        super().__init__()
        if endless: channelMusic.play(musLevel1, 99999)
        else: channelMusic.play(musLevel1, 0)

        self.textScore = Text(TextConfig(position=Vector2(PLAYFIELD_RIGHT_XPOS + ((SCREEN_WIDTH - PLAYFIELD_RIGHT_XPOS) / 2), 80), text="0000000", alignment=TextAlign(h="center", v="top"), size=32))
        self.textHiscore = Text(TextConfig(position=Vector2(PLAYFIELD_RIGHT_XPOS + ((SCREEN_WIDTH - PLAYFIELD_RIGHT_XPOS) / 2), 170), text="0000000", alignment=TextAlign(h="center", v="top"), size=32))
        self.textLives = Text(TextConfig(position=Vector2(PLAYFIELD_RIGHT_XPOS + ((SCREEN_WIDTH - PLAYFIELD_RIGHT_XPOS) / 2), 260), text="111", alignment=TextAlign(h="center", v="top"), size=32))
        self.instances = [
            player,
            bulletgen,
            Text(TextConfig(position=Vector2(PLAYFIELD_RIGHT_XPOS + ((SCREEN_WIDTH - PLAYFIELD_RIGHT_XPOS) / 2), 50), text="SCORE", alignment=TextAlign(h="center", v="top"), size=32, color=pygame.Color(255, 255, 0))),
            self.textScore,
            Text(TextConfig(position=Vector2(PLAYFIELD_RIGHT_XPOS + ((SCREEN_WIDTH - PLAYFIELD_RIGHT_XPOS) / 2), 140), text="HISCORE", alignment=TextAlign(h="center", v="top"), size=32, color=pygame.Color(255, 255, 0))),
            self.textHiscore,
            Text(TextConfig(position=Vector2(PLAYFIELD_RIGHT_XPOS + ((SCREEN_WIDTH - PLAYFIELD_RIGHT_XPOS) / 2), 230), text="LIVES", alignment=TextAlign(h="center", v="top"), size=32, color=pygame.Color(255, 255, 0))),
            self.textLives,
        ]
        if lunatic: self.instances.append(Text(TextConfig(position=Vector2(PLAYFIELD_RIGHT_XPOS + ((SCREEN_WIDTH - PLAYFIELD_RIGHT_XPOS) / 2), 420), text="LUNATIC", alignment=TextAlign(h="center", v="top"), size=32, color=pygame.Color(255, 0, 0))))
        for i in range(64):
            self.instances.append(StarObject(random.randint(PLAYFIELD_LEFT_WIDTH, PLAYFIELD_RIGHT_XPOS), random.randint(PLAYFIELD_TOP_HEIGHT, PLAYFIELD_BOTTOM_YPOS)))



    def update(self, dt):
        global conductor
        global jimmyspawned
        global jimmyboss
        global myScoreNow
        global deaths
        global endless
        super().update(dt)
        self.textScore.ChangeText(f"{score:08d}")
        if score < GetScoreAtIndex(0)['score']:
            self.textHiscore.ChangeText(f"{GetScoreAtIndex(0)['score']:08d}")
        else:
            if myScoreNow == False:
                myScoreNow = True
                scene.addInstance(AlertObject("NEW HiSCORE!!!"))
            self.textHiscore.ChangeText(f"{score:08d}")

        if deaths == 0: self.textLives.ChangeText(f"111")
        if deaths == 1: self.textLives.ChangeText(f"110")
        if deaths == 2: self.textLives.ChangeText(f"100")
        if deaths == 3: self.textLives.ChangeText(f"000")


        if DEBUG:
            if ButtonPressed(pygame.K_g):
                deaths = 3
                TimeToDie()
        if jimmyspawned == True: return
        if gameover: return

        conductor += 45 * dt


        if timer % random.randint(20, 30) == 0 and jimmyboss == -1:
            self.addInstance(EnemyObject(random.randint(PLAYFIELD_LEFT_WIDTH, PLAYFIELD_RIGHT_XPOS), PLAYFIELD_TOP_HEIGHT - 24, sprBaseEnemy, Vector2(random.randint(-1, 1), 2)))

        if endless: return

        if channelMusic.get_busy() == False:
            jimmyspawned = True
            jimmyboss = JimmyBossObject(185, PLAYFIELD_TOP_HEIGHT + 72)
            scene.addInstance(jimmyboss)
            print("now it's time for the real battle")

    def render(self):
        super().render()
        borderColor = (0, 0, 0)
        if not (DEBUG and ButtonHeld(pygame.K_c)):
            pygame.draw.rect(screen, borderColor, pygame.Rect(0, 0, SCREEN_WIDTH, PLAYFIELD_TOP_HEIGHT))
            pygame.draw.rect(screen, borderColor, pygame.Rect(0, 0, PLAYFIELD_LEFT_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, borderColor, pygame.Rect(0, PLAYFIELD_BOTTOM_YPOS, SCREEN_WIDTH, SCREEN_HEIGHT - PLAYFIELD_BOTTOM_YPOS))
            pygame.draw.rect(screen, borderColor, pygame.Rect(PLAYFIELD_RIGHT_XPOS, 0, SCREEN_WIDTH - PLAYFIELD_RIGHT_XPOS, SCREEN_HEIGHT))
            pygame.draw.rect(screen, (14, 14, 14), pygame.Rect(PLAYFIELD_LEFT_WIDTH, PLAYFIELD_TOP_HEIGHT, PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT), 2)

        for instance in self.instances:
            if instance.__class__.__name__ == "Text":
                if instance.config.text != "GAMEOVER" and instance.__class__.__name__ != "AlertObject": instance.render()

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
        pygame.draw.line(screen, (255, 255, 255), (320 - (pygame.font.Font.size(fntMain, name)[0] / 2) - 10, _lineY), (320 + (pygame.font.Font.size(fntMain, name)[0] / 2) + 10, _lineY))


scene = IntroMenuScene()


while running:
    running = UpdateEvents()

    if ButtonPressed(pygame.K_F4):
        pygame.display.toggle_fullscreen()
    
    screen.fill("black")
    timer += 1

    if timer % 2 == 0:
        if scoreAdd >= 10:
            score += 10
            scoreAdd -= 10
        elif scoreAdd > 0:
            score += scoreAdd
            scoreAdd = 0

    scene.update(dt)
    scene.render()

    if DEBUG:
        DrawText(10, 10, f"debug")
        DrawText(10, 40, f"{len(scene.instances)} instances")
        DrawText(10, 70, f"{scene.__class__.__name__}")

    pygame.display.flip()
    dt = clock.tick(60) / 1000


pygame.quit()