import pygame
import random

Vector2 = pygame.Vector2

class Object:
    def __init__(self, x = 0, y = 0):
        #initalize all object variables :)
        self.position = Vector2(x, y)
        self.velocity = Vector2(0 ,0)
        self.zIndex = 0
        self.bbox = pygame.Rect(self.position.x, self.position.y, 1, 1)

        self.hspeed = 0
        self.vspeed = 0

        self.persistent = False
    def update(self, dt): 
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y
    def render(self): pass
    def destroy(self): pass