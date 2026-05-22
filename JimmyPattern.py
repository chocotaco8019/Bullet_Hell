import pygame
import random
import math

class JimmyBoss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.size = 20
        
        # Boss health system
        self.max_health = 300
        self.health = self.max_health
        self.stage = 1  # 1, 2, or 3
        
        # Stage thresholds
        self.stage_2_threshold = self.max_health * 0.66
        self.stage_3_threshold = self.max_health * 0.33
        self.stage_4_threshold = self.max_health * 0.05  # Final phase at 5% health
        
        # Movement
        self.angle = 0
        self.radius = 50
        self.speed = 2
        
        # Attack patterns
        self.attack_timer = 0
        self.shot_counter = 0
        
        # Dialogue system
        self.dialogue_lines = [
            "You know... I've been expecting you.",
            "Time to settle this... JIMMY STYLE!",
            "Prepare yourself, mortal!",
            "I didn't get this powerful by being nice.",
            "Let's dance.",
        ]
        self.current_dialogue = random.choice(self.dialogue_lines)
        self.dialogue_timer = 180  # Show dialogue for 3 seconds (at 60 FPS)
        self.show_dialogue = True
        
        # Smite warning system
        self.smite_warnings = [
            "YOUR TIME HAS COME!",
            "FEEL MY WRATH!",
            "SMITED!",
            "BEGONE!",
            "DIVINE RETRIBUTION!",
            "YOU ASKED FOR THIS!",
        ]
        self.current_smite_warning = ""
        self.smite_warning_timer = 0
        self.show_smite_warning = False

    def take_damage(self, damage):
        """Reduce health and update stage"""
        self.health -= damage
        self.update_stage()
        
    def update_stage(self):
        """Change stage based on health"""
        if self.health <= self.stage_4_threshold and self.stage != 4:
            self.stage = 4
            self.speed = 0  # Becomes still for divine judgment
        elif self.health <= self.stage_3_threshold and self.stage != 3:
            self.stage = 3
            self.speed = 4  # Faster movement
        elif self.health <= self.stage_2_threshold and self.stage != 2:
            self.stage = 2
            self.speed = 3  # Moderate speed increase

    def update(self):
        """Update boss position and attack pattern based on stage"""
        self.attack_timer += 1
        
        # Update dialogue timer
        if self.dialogue_timer > 0:
            self.dialogue_timer -= 1
        else:
            self.show_dialogue = False
        
        # Update smite warning timer
        if self.smite_warning_timer > 0:
            self.smite_warning_timer -= 1
        else:
            self.show_smite_warning = False
        
        # Movement pattern changes by stage
        if self.stage == 1:
            self.update_stage_1()
        elif self.stage == 2:
            self.update_stage_2()
        elif self.stage == 3:
            self.update_stage_3()
        elif self.stage == 4:
            self.update_stage_4()

    def update_stage_1(self):
        """Stage 1: Circular movement pattern"""
        self.angle += 0.05
        self.x += math.cos(self.angle) * self.radius * 0.05
        self.y += math.sin(self.angle) * self.radius * 0.1

    def update_stage_2(self):
        """Stage 2: Figure-8 pattern, erratic movement"""
        self.angle += 0.08
        self.x += math.cos(self.angle) * self.radius * 0.08
        self.y += math.sin(self.angle * 2) * self.radius * 0.12

    def update_stage_3(self):
        """Stage 3: Chaotic rapid movement"""
        self.angle += 0.12
        self.x += math.cos(self.angle) * self.radius * 0.15
        self.y += math.sin(self.angle * 3) * self.radius * 0.15
        # Add some random jitter
        self.x += random.uniform(-2, 2)
        self.y += random.uniform(-2, 2)

    def update_stage_4(self):
        """Stage 4: Divine retribution - boss becomes still and prepares to smite"""
        # Boss stays centered, glowing with divine wrath
        pass

    def get_attack_pattern(self):
        """Return bullet pattern data based on stage"""
        if self.stage == 1:
            return self.get_stage_1_pattern()
        elif self.stage == 2:
            return self.get_stage_2_pattern()
        elif self.stage == 3:
            return self.get_stage_3_pattern()
        elif self.stage == 4:
            return self.get_stage_4_pattern()

    def get_stage_1_pattern(self):
        """Stage 1: Slow single stream"""
        if self.attack_timer % 30 == 0:
            angle = random.uniform(0, 2 * math.pi)
            return [{"angle": angle, "speed": 3}]
        return []

    def get_stage_2_pattern(self):
        """Stage 2: Spiral pattern with multiple bullets"""
        if self.attack_timer % 20 == 0:
            bullets = []
            for i in range(3):
                angle = (self.attack_timer * 0.1 + i * 2 * math.pi / 3) % (2 * math.pi)
                bullets.append({"angle": angle, "speed": 4})
            return bullets
        return []

    def get_stage_3_pattern(self):
        """Stage 3: Dense bullet hell pattern"""
        if self.attack_timer % 10 == 0:
            bullets = []
            num_bullets = 8
            for i in range(num_bullets):
                angle = (self.attack_timer * 0.2 + i * 2 * math.pi / num_bullets) % (2 * math.pi)
                bullets.append({"angle": angle, "speed": 5})
            return bullets
        return []

    def get_stage_4_pattern(self):
        """Stage 4: Divine smite - instant kill attack"""
        if self.attack_timer % 60 == 0:
            # Show smite warning
            self.current_smite_warning = random.choice(self.smite_warnings)
            self.smite_warning_timer = 120  # Show for 2 seconds
            self.show_smite_warning = True
            # Return instant-kill marker
            return [{"type": "smite", "instant_kill": True}]
        return []

    def draw(self, screen):
        """Draw boss with health bar"""
        # Boss body - changes color by stage
        if self.stage == 1:
            color = (255, 100, 0)  # Orange
        elif self.stage == 2:
            color = (255, 50, 0)   # Dark orange/red
        elif self.stage == 3:
            color = (255, 0, 0)    # Red
        else:  # Stage 4
            color = (255, 255, 0)  # Divine yellow
            # Draw a glowing aura around the boss
            pygame.draw.circle(screen, (255, 200, 0), (int(self.x), int(self.y)), self.size + 15, 3)
            pygame.draw.circle(screen, (255, 150, 0), (int(self.x), int(self.y)), self.size + 10, 2)
        
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)
        
        # Draw health bar
        bar_width = 200
        bar_height = 20
        bar_x = 400 - bar_width // 2
        bar_y = 20
        
        # Background bar (red)
        pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        # Health bar (green)
        health_ratio = max(0, self.health / self.max_health)
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))
        # Border
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Draw dialogue if showing
        if self.show_dialogue:
            self.draw_dialogue(screen)
        
        # Draw smite warning if showing
        if self.show_smite_warning:
            self.draw_smite_warning(screen)
        
        # Stage indicator
        stage_text = f"Stage: {self.stage}"
        # You'll need a font object from the main game to render this
        # font = pygame.font.Font(None, 24)
        # stage_surface = font.render(stage_text, True, (255, 255, 255))
        # screen.blit(stage_surface, (bar_x, bar_y + bar_height + 5))

    def is_defeated(self):
        """Check if boss is defeated"""
        return self.health <= 0

    def draw_dialogue(self, screen):
        """Draw the boss's dialogue on screen"""
        try:
            font = pygame.font.Font(None, 32)
            dialogue_surface = font.render(self.current_dialogue, True, (255, 255, 255))
            
            # Draw semi-transparent background for dialogue
            dialogue_rect = dialogue_surface.get_rect()
            dialogue_rect.center = (400, 120)
            
            # Background box
            bg_rect = dialogue_rect.inflate(20, 20)
            pygame.draw.rect(screen, (50, 50, 50), bg_rect)
            pygame.draw.rect(screen, (255, 200, 0), bg_rect, 3)  # Gold border
            
            # Dialogue text
            screen.blit(dialogue_surface, dialogue_rect)
        except:
            # If font rendering fails, just skip dialogue display
            pass

    def draw_smite_warning(self, screen):
        """Draw the smite warning text in large, threatening font"""
        try:
            font = pygame.font.Font(None, 60)
            # Make text red and pulsing
            intensity = int(255 * (self.smite_warning_timer / 120.0))
            warning_surface = font.render(self.current_smite_warning, True, (255, intensity, intensity))
            
            # Center on screen
            warning_rect = warning_surface.get_rect()
            warning_rect.center = (400, 300)
            
            # Draw background box with red glow
            bg_rect = warning_rect.inflate(40, 40)
            pygame.draw.rect(screen, (100, 0, 0), bg_rect)
            pygame.draw.rect(screen, (255, 0, 0), bg_rect, 5)  # Red border
            
            # Draw warning text
            screen.blit(warning_surface, warning_rect)
        except:
            # If font rendering fails, just skip warning display
            pass

    def smite(self):
        """Instantly kill the player - returns True if smite is used"""
        if self.stage == 4 and self.attack_timer % 60 == 0:
            return True
        return False