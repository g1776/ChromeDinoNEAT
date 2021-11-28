# ChromeDinoNEAT
 Teaching AI to play the Chrome Dino game with NEAT
 
Read the Medium article about this repository: https://medium.com/@gregoryg323/neural-networks-play-chromes-dino-game-with-neat-python-defe7c46a7f8

## Playing against AI
To play agaisnt the pretrained AI, run these commands:

```
cd src
python game.py -d Normal
```

you can replace the `-d` tag (difficulty) with which difficulty you would like to play against. Available difficulties are "Normal", "Hard", and "Impossible". Each difficulty is trained by setting a fitness threshold of 147, 233, and 370, respectively.

## Training your own Dinosaur 🦖
To train a dinosaur, first edit the *fitness_threshold* `config.txt` inside `src` to whatever you fitness threshold you want to train to. Note that you will have to wait until this threshold is met and the program closes itself before being able to save this dinosaur to be used later. On closing, the program will save the dinosaur to the `models` folder called dino_f{fitness_score}.pkl

After setting your fitness_threshold, run

```
cd src
python agent.py
```

The game itself is in `train.py`, but the training starts from `agent.py` which handles the initialization of NEAT, as well as saving the "winner".
