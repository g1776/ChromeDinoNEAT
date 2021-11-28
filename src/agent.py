import neat
import os
import pickle
import math

from train import main


def run_neat():
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    n_generations = 100
    winner = p.run(main,n_generations)

    with open(f'../models/dino_f{math.trunc(winner.fitness)}.pkl', 'wb') as f:
        pickle.dump(winner, f)


run_neat()

