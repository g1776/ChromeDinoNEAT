# !/usr/bin/python
# -*- coding: utf-8 -*-
import os
import random
import neat
import numpy as np
from neat.math_util import softmax
import math
import pickle
from classes.dino import DinsosaurTrain
from classes.obstacle import *
from classes.scene import *

import pygame

# Global Constants

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

GEN = 0
MAX_FITNESS = 0

pygame.display.set_caption("Chrome Dino Runner")

Ico = pygame.image.load("assets/DinoWallpaper.png")
pygame.display.set_icon(Ico)

FONT_COLOR=(0,0,0)


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

# start game
pygame.init()
def main(genomes, config):
    global GEN
    GEN += 1

    nets = []
    ge = []
    players = []
    NUM_STARTING_PLAYERS = len(genomes)

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        players.append(DinsosaurTrain())
        g.fitness = 0
        ge.append(g)
    

    global game_speed, x_pos_bg, y_pos_bg, points, obstacles, MAX_FITNESS
    run = True
    clock = pygame.time.Clock()
    
    cloud = Cloud()
    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    font = pygame.font.Font("freesansbold.ttf", 20)
    obstacles = []
    death_count = 0
        

    def score():
        global points, game_speed, MAX_FITNESS
        points += 1
        for g in ge:
            g.fitness += 0.1
        if points % 100 == 0:
            game_speed += 1

        text = font.render(f"Best Fitness: {math.trunc(MAX_FITNESS)} Points: {points}", True, FONT_COLOR)
        textRect = text.get_rect()
        textRect.center = (940, 40)
        SCREEN.blit(text, textRect)

        # draw generation and num dinos
        text = font.render(f"Gen: {GEN}    % Dinos Remaining: {len(players)}/{NUM_STARTING_PLAYERS}", True, FONT_COLOR)
        textRect = text.get_rect()
        textRect.center = (200, 40)
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


    while run:

        # end generation when no more players
        if len(players) == 0:
            print("No more dinos :(")
            run = False
            break
        
        # handle manual exiting
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                
                best_ge = [g for g in ge if math.trunc(g.fitness) == math.trunc(MAX_FITNESS)][0]
                run = False
                with open(f'../models/dino_f{math.trunc(best_ge.fitness)}.pkl', 'wb') as f:
                    pickle.dump(best_ge, f)
                quit()
                
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

        max_fitness = max([g.fitness for g in ge])
        if max_fitness > MAX_FITNESS:
            MAX_FITNESS = max_fitness

        for i, obstacle in enumerate(obstacles):
            obstacle.draw(SCREEN)
            obstacle.update(game_speed)
            if obstacle.rect.x < -obstacle.rect.width:
                obstacles.pop(i)


            for i, player in enumerate(players):

                # DINO PASSED OBSTACLE
                if player.dino_rect.x == obstacle.rect.x and \
                    not player.dino_rect.colliderect(obstacle.rect) and \
                        obstacle.visible:
                    if player.dino_jump:
                        ge[i].fitness += 1.5
                    elif player.dino_duck:
                        ge[i].fitness += 2 # extra reward for ducking
                
                
                if player.dino_rect.colliderect(obstacle.rect) and obstacle.visible:
                    # DINO DIED
                    death_count += 1
                    ge[i].fitness -= 1
                    players.pop(i)
                    nets.pop(i)
                    ge.pop(i)
                    

        background()

        cloud.draw(SCREEN)
        cloud.update(game_speed)

        
        score()

        # update nns (neat)
        for i, player in enumerate(players):
            player.draw(SCREEN)

            output = nets[i].activate(
                State(player, obstacles, game_speed, points).process()
                )
            
            softmax_result = softmax(output)
            class_output = np.argmax(((softmax_result / np.max(softmax_result)) == 1).astype(int))
            if class_output == 0:
                player.update("")
            elif class_output == 1:   
                player.update("UP")
            elif class_output == 2:
                player.update("DOWN")

        clock.tick(9999)
        pygame.display.update()