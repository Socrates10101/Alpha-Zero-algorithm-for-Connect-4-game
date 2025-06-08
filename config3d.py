#  ================ AlphaZero algorithm for 3D Connect 4 game =================== #
# Name:             config3d.py
# Description:      Meta-parameters and various options for 3D Connect 4
# Authors:          AI Assistant
# Date:             2025
# License:          BSD 3-Clause License
# ============================================================================ #

#----------------------------------------------------------------------#
# 3D board size
SIZE = 4  # 4x4x4 board
BOARD_SIZE = SIZE * SIZE * SIZE  # 64 cells
OUTPUT_SIZE = SIZE * SIZE  # 16 possible moves (columns)

#----------------------------------------------------------------------#
# Enter how many CPUs you want to use.
CPUS = 40
max_iterations = 1000 #max number of iteration of self play reinforcement learning

#----------------------------------------------------------------------#
#MCTS parameters
SIM_NUMBER = 30
sim_number_defense = 30 #old option : you can help the second player by increasing its sim number (not sure if it works)
CPUCT = 1
# Temperature :
tau=1
# see readme :
favorlonggames = True
long_game_factor = 0.1

# Unlike other github repo I choose the true reward for terminal states and not the NN Q-value (change to True if you want change this):
use_nn_for_terminal = False
# This is an (old) option to force the program to take the win when there is one, or counter the lose. It is actually not needed since it is going to learn this anyway
use_counter_in_mcts_nn = False
# To navigate in the MCTS tree, it looks reasonnable to mask and renormalize the probabilities given by the neural network when the move is not legal
# it is actually not required since the NN does learn it by itself (see the probability going to zero at turn 6 for the full central column)
maskinmcts = False

#----------------------------------------------------------------------#
#NN architecture for 3D

net = 'resnet3d' #3D version
res_tower = 1 #number of residual block : 1 is quite enough here with 256 filters
convsize = 256 #number of filters
polfilters = 2 # 256 -> 2 filters when entering policy head (DeepMind's choice)
valfilters = 1 # 256 -> 1 filter when entering value head (DeepMind's choice)
usehiddenpol = False #you can add a dense layer in the policy head. Default : None
hiddensize = 256 # hidden dense layer's size in the value head

#----------------------------------------------------------------------#
#choice of optimizer : allowed are 'sgd' or 'adam'
optim = 'sgd'
sgd_lr = 0.001 #initial learning rate. Curiously enough the learning is catastrophic for higher learning rates (like 0.1 in DeepMind's paper).
# I don't know why, probably because the NN is not a deep one with only one residual block?

#adam_lr=0.01

#learning rate annealing (learning rate is divided by 2 every 30 succesfull improvements of the NN):
lrdecay = 2
annealing = 30

#----------------------------------------------------------------------#
# Neural Net training

use_cuda = True #if you have a GPU
momentum = 0.9
wdecay = 0.0001 #weight decay
EPOCHS = 4
MINIBATCH = 32
MAXMEMORY = MINIBATCH * 3000 #one iteration of 400 games typically creates 600-1000 batches : here we thus save the last 10-6 games or so
MAXBATCHNUMBER = 1000 #and we improve the NN by sample randomly in the last maxmemory batches
MINBATCHNUMBER = 64

#----------------------------------------------------------------------#
#self play options
dirichlet_for_self_play = True
alpha_dir  = 0.8
epsilon_dir = 0.2
selfplaygames = 400 #i'd recommend at least 64

# see main functions :
use_z_last = False
data_extension = True

# temperatures
tau_zero_self_play = 18 #play greedily after turn 18
tau_self_play = 1 #temperature

#----------------------------------------------------------------------#
# check improvement or not of the NN
tournamentloop = 2 # this number * CPUS is the number of game you play to check whether the NN has improved
threshold = 0.51 #+ 1/np.sqrt(12*tournamentloop*CPUS) # This says it must be greater than 0.5 up to 1 standard deviation. This is 0.532 for 80 games
sim_number_tournaments = 49
tau_zero_eval_new_nn = 1 #in this tournament we set this parameter to 1 : both player are greedy
tau_pv = 1 # temperature

alternplayer = True # if set to False, the new NN player always start (which is a clear bias -> default is True)

# do we want use self play data from previous iterations? unclear. Both work (False is faster)
useprevdata = False

#----------------------------------------------------------------------#
#MCTS checkpoint options and ELO ratings
use_counter_in_pure_mcts = False
printstatefreq = 1
checkpoint_frequency = 1

#----------------------------------------------------------------------#
# print particular values on specific states for 3D

def particular_states_3d():
    """Example 3D states for debugging/analysis"""
    # Start with some simple 3D states
    list = [
        # Empty board
        [[], []],
        # One move in center
        [[(1,1,0)], []],
        # Two moves in same column  
        [[(1,1,0)], [(1,1,1)]],
        # Moves in different columns
        [[(1,1,0), (2,2,0)], [(0,0,0)]],
        # More complex positions
        [[(1,1,0), (2,2,0), (1,1,1)], [(0,0,0), (3,3,0)]],
    ]
    return list

def getstate3d(i):
    """Convert 3D state index to game state representation"""
    list = particular_states_3d()
    if i >= len(list):
        return None
    
    elem = list[i]
    # For 3D, we'll use the Game3D state representation
    # This is just a placeholder - actual implementation would need Game3D
    return {
        'board': None,  # Would be filled by actual 3D board
        'player_turn': 1 if len(elem[0]) == len(elem[1]) else -1
    }