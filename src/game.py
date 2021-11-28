# !/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import random
import threading
import numpy as np
import math
import pygame
from neat.math_util import softmax

from classes.dino import *
from classes.obstacle import *
from classes.scene import *



pygame.init()

# Global Constants

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("Chrome Dino Runner")

Ico = pygame.image.load("assets/DinoWallpaper.png")
pygame.display.set_icon(Ico)


FONT_COLOR=(0,0,0)
FONT_COLOR_NIGHT=(2555,255,255)


class State:
    def __init__(self, player, obstacles, game_speed, points):
        self.player = player
        self.obstacles = obstacles
        self.game_speed = game_speed
        self.points = points

    def process(self):

        # speed the game is running at
        speed = self.game_speed

        # player position
        p_x = self.player.dino_rect.x
        p_y = self.player.dino_rect.y
        
        # obstacle data (-1 when no obstacle)
        o_type = -1
        o_x = -1
        o_y = -1
        for obstacle in self.obstacles:
            if not obstacle.visible:
                # don't consider invisible obstacles
                o_type = -1
                o_x = -1
                o_y = -1
            else:
                o_type = obstacle_types.index(str(obstacle.__class__))
                o_x = obstacle.rect.x
                o_y = obstacle.rect.y

            # "no" obstacle to consider when obstacle at/past player x position
            if o_x <= p_x:
                o_type = -1
                o_x = -1
                o_y = -1
        
        return [p_y, o_x, o_y, o_type, speed]


def main():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    run = True
    clock = pygame.time.Clock()
    human = Dinosaur()
    bot = DinsosaurBot("Impossible")
    
    cloud = Cloud()
    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    obstacles = []
    death_count = 0
    pause = False

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1
        with open("score.txt", "r") as f:
            score_ints = [int(x) for x in f.read().split()]  
            highscore = max(score_ints)
            if points > highscore:
                highscore=points 
            font = pygame.font.Font("freesansbold.ttf", 20)
            text = font.render("High Score: "+ str(highscore) + "  Points: " + str(points), True, FONT_COLOR)
        textRect = text.get_rect()
        textRect.center = (900, 40)
        SCREEN.blit(text, textRect)

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

    def unpause():
        nonlocal pause, run
        pause = False
        run = True

    def paused():
        nonlocal pause
        pause = True
        font = pygame.font.Font("freesansbold.ttf", 30)
        text = font.render("Game Paused, Press 'u' to Unpause", True, FONT_COLOR)
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT  // 3)
        SCREEN.blit(text, textRect)
        pygame.display.update()

        while pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_u:
                    unpause()

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                run = False
                paused()

        SCREEN.fill((255, 255, 255))
        
        if len(obstacles) == 0:
            if random.randint(0, 3) == 0:
                obstacles.append(SmallCactus())
            elif random.randint(0, 3) == 1:
                obstacles.append(LargeCactus())
            elif random.randint(0, 3) == 2:
                obstacles.append(Bird())
            elif random.randint(0, 4) == 3:
                invisible_obstacle = Obstacle(Bird.BIRD, 1)
                invisible_obstacle.visible = False
                obstacles.append(invisible_obstacle)

        for i, obstacle in enumerate(obstacles):
            obstacle.draw(SCREEN)
            obstacle.update(game_speed)
            if obstacle.rect.x < -obstacle.rect.width:
                obstacles.pop(i)

            # collision detection and win/lose screens
            if human.dino_rect.colliderect(obstacle.rect):
                font = pygame.font.Font("freesansbold.ttf", 30)
                text = font.render("You Lost :(", True, FONT_COLOR)
                textRect = text.get_rect()
                textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT  // 3)
                SCREEN.blit(text, textRect)
                death_count += 1
                run = False
            

            if bot.dino_rect.colliderect(obstacle.rect):
                font = pygame.font.Font("freesansbold.ttf", 30)
                text = font.render("You Won!", True, FONT_COLOR)
                textRect = text.get_rect()
                textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT  // 3)
                SCREEN.blit(text, textRect)
                run = False
                
                
                

        background()

        cloud.draw(SCREEN)
        cloud.update(game_speed)

        score()

        # draw and update human
        userInput = pygame.key.get_pressed()
        human.draw(SCREEN)
        human.update(userInput)
        output = bot.nn.activate(
                State(bot, obstacles, game_speed, points).process()
                )

        # draw and update bot 
        bot.draw(SCREEN)
        softmax_result = softmax(output)
        class_output = np.argmax(((softmax_result / np.max(softmax_result)) == 1).astype(int))
        if class_output == 0:
            bot.update("")
        elif class_output == 1:   
            bot.update("UP")
        elif class_output == 2:
            bot.update("DOWN")

        if not run:
            pygame.display.update()
            pygame.time.delay(2000)
            menu(death_count)
        else:
            clock.tick(30)
            pygame.display.update()


def menu(death_count):
    global points
    global FONT_COLOR
    run = True
    while run:

        # determine temporal variables
        current_time = datetime.datetime.now().hour
        if 7 < current_time < 19:
            FONT_COLOR=(0,0,0)
            SCREEN.fill((255, 255, 255))
        else:
            FONT_COLOR=(255,255,255)
            SCREEN.fill((128, 128, 128))
        font = pygame.font.Font("freesansbold.ttf", 30)

        # score text
        if death_count == 0:
            text = font.render("Press any Key to Start", True, FONT_COLOR)
        elif death_count > 0:
            text = font.render("Press any Key to Restart", True, FONT_COLOR)
            score = font.render("Your Score: " + str(points), True, FONT_COLOR)
            scoreRect = score.get_rect()
            scoreRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN.blit(score, scoreRect)
            f = open("score.txt", "a")
            f.write(str(points) + "\n")
            f.close()
            with open("score.txt", "r") as f:
                score = (
                    f.read()
                )  # Read all file in case values are not on a single line
                score_ints = [int(x) for x in score.split()]  # Convert strings to ints
            highscore = max(score_ints)  # sum all elements of the list
            hs_score_text = font.render(
                "High Score : " + str(highscore), True, FONT_COLOR
            )
            hs_score_rect = hs_score_text.get_rect()
            hs_score_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
            SCREEN.blit(hs_score_text, hs_score_rect)
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        SCREEN.blit(text, textRect)
        
        SCREEN.blit(Dinosaur.RUNNING[0], (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 140))

        # draw difficulty buttons
        mouse = pygame.mouse.get_pos()
        btn_color = (170,170,170)
        btn_color_hover = (100,100,100)
        btn_width = math.trunc(SCREEN_WIDTH * .4)
        btn_height = math.trunc(SCREEN_HEIGHT * .1)
        btns_top = SCREEN_HEIGHT // 2 + 40
        btns_offset = 20
        # for idx, diff in enumerate(['Normal', 'Hard', 'Impossible']):

        #     mouseOver = SCREEN_WIDTH/2 <= mouse[0] <= SCREEN_WIDTH/2 + btn_width and \
        #         btns_top <= mouse[1] <= (btn_height + btns_offset) * idx
            
        #     pygame.draw.rect(
        #         SCREEN, 
        #         btn_color_hover if mouseOver else btn_color, 
        #         [SCREEN_WIDTH // 2 - btn_width // 2, 
        #         btns_top + (btn_height + btns_offset) * idx,
        #         btn_width, 
        #         btn_height
        #         ])
        #     text = font.render(diff , True , FONT_COLOR)
        #     textRect = text.get_rect()
        #     textRect.center = (SCREEN_WIDTH // 2, btns_top + (btn_height + btns_offset) * idx + (btn_height//2))
        #     SCREEN.blit(text, textRect)
        
        # handle input to start/exit game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                main()

        pygame.display.update()


t1 = threading.Thread(target=menu(death_count=0), daemon=True)
t1.start()
