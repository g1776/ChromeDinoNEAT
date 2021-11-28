import random
import pygame
import os
from .scene import SCREEN_WIDTH

obstacle_types = [
    "<class 'classes.obstacle.SmallCactus'>",
    "<class 'classes.obstacle.LargeCactus'>",
    "<class 'classes.obstacle.Bird'>"
]

class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH
        self.visible = True

    def update(self, game_speed):
        self.rect.x -= game_speed

    def draw(self, SCREEN):
        if self.visible:
            SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    SMALL_CACTUS = [
    pygame.image.load(os.path.join("assets/Cactus", "SmallCactus1.png")),
    pygame.image.load(os.path.join("assets/Cactus", "SmallCactus2.png")),
    pygame.image.load(os.path.join("assets/Cactus", "SmallCactus3.png")),
    ]

    def __init__(self):
        self.type = random.randint(0, 2)
        super().__init__(self.SMALL_CACTUS, self.type)
        self.rect.y = 325


class LargeCactus(Obstacle):
    LARGE_CACTUS = [
    pygame.image.load(os.path.join("assets/Cactus", "LargeCactus1.png")),
    pygame.image.load(os.path.join("assets/Cactus", "LargeCactus2.png")),
    pygame.image.load(os.path.join("assets/Cactus", "LargeCactus3.png")),
    ]
    def __init__(self):
        self.type = random.randint(0, 2)
        super().__init__(self.LARGE_CACTUS, self.type)
        self.rect.y = 300


class Bird(Obstacle):
    BIRD_HEIGHTS = [240, 290, 320]
    BIRD = [
    pygame.image.load(os.path.join("assets/Bird", "Bird1.png")),
    pygame.image.load(os.path.join("assets/Bird", "Bird2.png")),
    ]

    def __init__(self):
        self.type = 0
        super().__init__(self.BIRD, self.type)
        self.rect.y = random.choice(self.BIRD_HEIGHTS)
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index // 5], self.rect)
        self.index += 1