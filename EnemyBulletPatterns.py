import pygame
import math
import random
class Enemy_Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.image.load("Assets/Enemy_Bullet.png")  # Load bullet image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 3
        self.angle = angle

    def update(self):
        # Move the bullet in the direction of the angle
        self.rect.x += self.speed * math.cos(math.radians(self.angle))
        self.rect.y += self.speed * math.sin(math.radians(self.angle))


class CircularPattern:
    """Fires all bullets in a circle at once"""
    def __init__(self, center_x, center_y, num_bullets=16):
        self.center_x = center_x
        self.center_y = center_y
        self.num_bullets = num_bullets
    
    def create_bullets(self):
        """Returns a list of all bullets fired in a circle"""
        bullets = []
        for i in range(self.num_bullets):
            angle = (360 / self.num_bullets) * i  # Evenly spaced angles
            bullet = Enemy_Bullet(self.center_x, self.center_y, angle)
            bullets.append(bullet)
        return bullets


class SequentialCircularPattern:
    """Fires 30 bullets in circular order, one at a time"""
    def __init__(self, center_x, center_y, num_bullets=30, fire_rate=5):
        self.center_x = center_x
        self.center_y = center_y
        self.num_bullets = num_bullets
        self.fire_rate = fire_rate  # Frames between each bullet
        self.current_bullet = 0
        self.frame_counter = 0
        self.bullets = []
    
    def update(self):
        """Call this every frame to fire bullets sequentially"""
        self.frame_counter += 1
        if self.frame_counter >= self.fire_rate and self.current_bullet < self.num_bullets:
            angle = (360 / self.num_bullets) * self.current_bullet
            bullet = Enemy_Bullet(self.center_x, self.center_y, angle)
            self.bullets.append(bullet)
            self.current_bullet += 1
            self.frame_counter = 0
        
        return self.bullets  # Return bullets created this frame
    
    def is_finished(self):
        """Returns True when all bullets have been fired"""
        return self.current_bullet >= self.num_bullets