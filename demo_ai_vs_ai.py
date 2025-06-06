#!/usr/bin/env python
"""
Demo script showing AI vs AI game
"""

from MCTS_NN import MCTS_NN
from Game_bitboard import Game
from ResNet import resnet18
import torch
import numpy as np
import time

def ai_vs_ai_demo():
    """Demonstrate AI playing against itself"""
    print("=== Alpha Zero Connect 4 - AI vs AI Demo ===\n")
    
    # Load the trained model
    print("Loading trained neural network...")
    model = resnet18()
    model.load_state_dict(torch.load('./best_model_resnet.pth'))
    model.eval()
    print("Model loaded successfully!\n")
    
    # Initialize game
    game = Game()
    
    # Create MCTS for both players
    tree = MCTS_NN(model, use_dirichlet=False)
    rootnode = tree.createNode(game.state)
    currentnode = rootnode
    
    turn = 0
    sim_number = 100  # Number of MCTS simulations per move
    
    print(f"Starting game with {sim_number} MCTS simulations per move...\n")
    game.display_it()
    print()
    
    while not currentnode.isterminal():
        turn += 1
        player = "Yellow" if game.player_turn == 1 else "Red"
        
        print(f"Turn {turn}: {player} is thinking...")
        start_time = time.time()
        
        # Run MCTS simulations
        for _ in range(sim_number):
            tree.simulate(currentnode, cpuct=1)
        
        # Get visit counts for each child
        visits = []
        moves = []
        for child in currentnode.children:
            visits.append(child.N)
            moves.append(game.convert_move_to_col_index(child.move))
        
        # Choose best move (most visited)
        best_idx = np.argmax(visits)
        best_col = moves[best_idx]
        
        think_time = time.time() - start_time
        print(f"   Thinking time: {think_time:.2f}s")
        print(f"   Visit counts by column: {dict(zip(moves, visits))}")
        print(f"   Chosen move: Column {best_col}\n")
        
        # Make the move
        currentnode = currentnode.children[best_idx]
        game = Game(currentnode.state)
        game.display_it()
        print()
        
        # Reinitialize tree for next player
        tree = MCTS_NN(model, use_dirichlet=False)
        rootnode = tree.createNode(game.state)
        currentnode = rootnode
    
    # Game over
    _, winner = game.gameover()
    print("=== GAME OVER ===")
    if winner == 0:
        print("Result: DRAW")
    elif winner == 1:
        print("Result: YELLOW WINS!")
    else:
        print("Result: RED WINS!")
    
    return winner

def show_nn_analysis():
    """Show neural network's analysis of key positions"""
    print("\n=== Neural Network Analysis of Key Positions ===\n")
    
    model = resnet18()
    model.load_state_dict(torch.load('./best_model_resnet.pth'))
    model.eval()
    
    # Analyze some standard openings
    positions = [
        ([], [], "Empty board"),
        ([3], [], "After Yellow plays center"),
        ([3], [3], "After Yellow and Red both play center"),
        ([3, 2], [3, 4], "Typical opening sequence")
    ]
    
    for yellow_moves, red_moves, desc in positions:
        game = Game()
        
        # Make moves
        for i in range(max(len(yellow_moves), len(red_moves))):
            if i < len(yellow_moves):
                moves = game.allowed_moves()
                game.takestep(moves[yellow_moves[i]])
            if i < len(red_moves):
                moves = game.allowed_moves()
                game.takestep(moves[red_moves[i]])
        
        # Get NN evaluation
        flat_state = game.state_flattener(game.state)
        with torch.no_grad():
            value, policy = model.forward(flat_state)
        
        print(f"{desc}:")
        game.display_it()
        print(f"Current player: {'Yellow' if game.player_turn == 1 else 'Red'}")
        print(f"NN evaluation: {value.item():.3f}")
        print(f"Move probabilities: {[f'{p:.1%}' for p in policy.numpy()[0]]}")
        print()

if __name__ == '__main__':
    show_nn_analysis()
    print("\n" + "="*50 + "\n")
    ai_vs_ai_demo()