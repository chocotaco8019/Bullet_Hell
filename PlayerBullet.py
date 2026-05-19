# Example file showing a basic pygame "game loop"
import pygame
import math

class Player_Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.image.load("Assets/Friendly_Bullet.png")  # Load bullet image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5
        self.angle = angle

    def update(self):
        # Move the bullet in the direction of the angle
        self.rect.x += self.speed * math.cos(math.radians(self.angle))
        self.rect.y += self.speed * math.sin(math.radians(self.angle))