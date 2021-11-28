import pygame
import neat
import os
import pickle


class Dinosaur:

    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5
    RUNNING = [
    pygame.image.load(os.path.join("assets/Dino", "DinoRun1.png")),
    pygame.image.load(os.path.join("assets/Dino", "DinoRun2.png")),
    ]
    JUMPING = pygame.image.load(os.path.join("assets/Dino", "DinoJump.png"))
    DUCKING = [
        pygame.image.load(os.path.join("assets/Dino", "DinoDuck1.png")),
        pygame.image.load(os.path.join("assets/Dino", "DinoDuck2.png")),
    ]

    def __init__(self):
        self.duck_img = self.DUCKING
        self.run_img = self.RUNNING
        self.jump_img = self.JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, userInput):
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        if (userInput[pygame.K_UP] or userInput[pygame.K_SPACE]) and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput[pygame.K_DOWN] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or userInput[pygame.K_DOWN]):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))


class DinsosaurBot(Dinosaur):

    difficulties = {
    'Normal': ('../models/dino_f147.pkl', (0,128,0)),
    'Hard': ('../models/dino_f233.pkl', (0,0,128)),
    'Impossible': ('../models/dino_f370.pkl', (128,0,0))
    }

    def __init__(self, difficulty):
        super().__init__()
        self.difficulty = difficulty
        with open(self.difficulties[difficulty][0], 'rb') as f:
            bot_genome = pickle.load(f) # load Dino bot
            config_path = "config.txt"
            config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                        config_path)
            self.nn = neat.nn.FeedForwardNetwork.create(bot_genome, config)

    def update(self, userInput):
        if self.dino_duck: 
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        if userInput == "UP" and not self.dino_jump and self.dino_rect.y == self.Y_POS:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput == "DOWN" and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or userInput == "DOWN"):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False


    def draw(self, SCREEN):

        # color bot green and lower alpha
        colouredImage = pygame.Surface(self.image.get_size())
        colouredImage.fill(self.difficulties[self.difficulty][1])
        
        finalImage = self.image.copy()
        finalImage.blit(colouredImage, (0, 0), special_flags = pygame.BLEND_MULT)
        finalImage.set_alpha(140)
        SCREEN.blit(finalImage, (self.dino_rect.x, self.dino_rect.y))


class DinsosaurTrain(Dinosaur):

    def __init__(self):
        super().__init__()
        config_path = "config.txt"
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                    config_path)

    def update(self, userInput):
        if self.dino_duck: 
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        if userInput == "UP" and not self.dino_jump and self.dino_rect.y == self.Y_POS:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput == "DOWN" and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or userInput == "DOWN"):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False