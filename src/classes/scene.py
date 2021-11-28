import random
import pygame
import os

CLOUD = pygame.image.load(os.path.join("assets/Other", "Cloud.png"))
BG = pygame.image.load(os.path.join("assets/Other", "Track.png"))
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100

class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self, game_speed):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))
