#!/usr/bin/env python
"""
Simple test script to demonstrate the game mechanics
"""

from Game_bitboard import Game
import numpy as np

def test_game_mechanics():
    """Test basic game mechanics"""
    print("=== Connect 4 Game Engine Test ===\n")
    
    # Create a new game
    game = Game()
    print("1. Initial empty board:")
    game.display_it()
    print()
    
    # Show allowed moves
    moves = game.allowed_moves()
    print(f"2. Number of allowed moves: {len(moves)}")
    print(f"   Column indices: {[game.convert_move_to_col_index(move) for move in moves]}")
    print()
    
    # Make some moves
    print("3. Making some moves (Yellow plays center column 3):")
    game.takestep(moves[3])  # Play in center column (index 3)
    game.display_it()
    print(f"   Current player turn: {game.player_turn} (1=Yellow, -1=Red)")
    print()
    
    # Red plays column 3
    moves = game.allowed_moves()
    print("4. Red plays column 3:")
    game.takestep(moves[3])
    game.display_it()
    print()
    
    # Continue playing a few more moves
    moves_sequence = [3, 3, 3, 3]  # Fill center column
    for i, col in enumerate(moves_sequence):
        moves = game.allowed_moves()
        if col < len(moves):
            print(f"5.{i+1}. {'Yellow' if game.player_turn == 1 else 'Red'} plays column {col}:")
            game.takestep(moves[col])
            game.display_it()
            
            # Check if game is over
            gameover, winner = game.gameover()
            if gameover:
                print(f"\n   GAME OVER! Winner: {'Yellow' if winner == 1 else 'Red' if winner == -1 else 'Draw'}")
                break
            print()

def test_nn_evaluation():
    """Test neural network evaluation on a board position"""
    print("\n=== Neural Network Evaluation Test ===\n")
    
    try:
        from ResNet import resnet18
        import torch
        
        # Load the trained model
        model = resnet18()
        model.load_state_dict(torch.load('./best_model_resnet.pth'))
        model.eval()
        
        # Create a game state
        game = Game()
        
        # Get NN evaluation for empty board
        flat_state = game.state_flattener(game.state)
        
        with torch.no_grad():
            value, policy = model.forward(flat_state)
            
        print("1. Empty board evaluation:")
        print(f"   Value (expected win rate): {value.item():.3f}")
        print(f"   Policy (move probabilities): {[f'{p:.1%}' for p in policy.numpy()[0]]}")
        print(f"   Best move: Column {np.argmax(policy.numpy()[0])}")
        
    except Exception as e:
        print(f"Neural network test failed: {e}")

if __name__ == '__main__':
    test_game_mechanics()
    test_nn_evaluation()