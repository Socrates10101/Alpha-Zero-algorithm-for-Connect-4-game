#!/usr/bin/env python
"""
Simple Human vs AI Connect 4 with minimal UI for testing
"""

from MCTS_NN import MCTS_NN
from Game_bitboard import Game
from ResNet import resnet18
import torch
import numpy as np

def simple_board_display(game, last_col=None):
    """Simple board display"""
    yellow_list = game.binarystatetoflatlist(game.state[0])
    red_list = game.binarystatetoflatlist(game.state[1])
    
    print("\n  0 1 2 3 4 5 6")
    print("  " + "─" * 13)
    
    for row in range(6):
        print(f"{5-row}│", end="")
        for col in range(7):
            idx = row * 7 + col
            
            if yellow_list[idx] == 1:
                if last_col == col:
                    print("Y", end="|")  # Last move highlight
                else:
                    print("Y", end="|")
            elif red_list[idx] == 1:
                if last_col == col:
                    print("R", end="|")  # Last move highlight
                else:
                    print("R", end="|")
            else:
                print(" ", end="|")
        print()
    print("  " + "─" * 13)

def get_human_move(game):
    """Get move from human player"""
    allowed_moves = game.allowed_moves()
    available_cols = [game.convert_move_to_col_index(move) for move in allowed_moves]
    
    print(f"\nAvailable columns: {available_cols}")
    
    while True:
        try:
            col = int(input("Enter column (0-6): "))
            if col in available_cols:
                for move in allowed_moves:
                    if game.convert_move_to_col_index(move) == col:
                        return move, col
            else:
                print(f"Invalid column! Choose from: {available_cols}")
        except ValueError:
            print("Please enter a number!")

def get_ai_move(game, model, simulations=100):
    """Get move from AI"""
    print(f"AI is thinking with {simulations} simulations...")
    
    # Create MCTS tree
    tree = MCTS_NN(model, use_dirichlet=False)
    rootnode = tree.createNode(game.state)
    
    # Run simulations
    for _ in range(simulations):
        tree.simulate(rootnode, cpuct=1)
    
    # Get best move
    visits = [child.N for child in rootnode.children]
    best_idx = np.argmax(visits)
    best_move = rootnode.children[best_idx].move
    best_col = game.convert_move_to_col_index(best_move)
    
    # Show AI analysis
    print("\nAI Analysis:")
    for i, child in enumerate(rootnode.children):
        col = game.convert_move_to_col_index(child.move)
        visits = child.N
        win_rate = 50 * (1 - child.Q)
        marker = "→" if i == best_idx else " "
        print(f"  {marker} Column {col}: {visits} visits, {win_rate:.1f}% win rate")
    
    print(f"\nAI chooses column {best_col}")
    return best_move, best_col

def play_game():
    """Play a simple human vs AI game"""
    print("=" * 50)
    print("HUMAN vs ALPHA ZERO CONNECT 4")
    print("=" * 50)
    
    # Load model
    print("Loading AI model...")
    try:
        model = resnet18()
        model.load_state_dict(torch.load('./best_model_resnet.pth'))
        model.eval()
        print("AI loaded successfully!")
    except Exception as e:
        print(f"Error loading AI: {e}")
        return
    
    # Game setup
    human_color = input("\nChoose your color (Y for Yellow/first, R for Red/second): ").upper()
    if human_color not in ['Y', 'R']:
        human_color = 'Y'
        print("Defaulting to Yellow (first)")
    
    difficulty = input("Choose difficulty (1=Easy, 2=Normal, 3=Hard): ")
    sim_map = {'1': 50, '2': 100, '3': 200}
    simulations = sim_map.get(difficulty, 100)
    
    # Initialize game
    game = Game()
    turn = 0
    moves_history = []
    human_turn = (human_color == 'Y')  # Yellow goes first
    
    print(f"\nStarting game! You are {'Yellow' if human_color == 'Y' else 'Red'}")
    print("=" * 50)
    
    while True:
        turn += 1
        current_player = "Human" if human_turn else "AI"
        
        print(f"\nTurn {turn} - {current_player}")
        simple_board_display(game, moves_history[-1] if moves_history else None)
        
        # Get move
        if human_turn:
            move, col = get_human_move(game)
            print(f"You played column {col}")
        else:
            move, col = get_ai_move(game, model, simulations)
        
        # Make move
        game.takestep(move)
        moves_history.append(col)
        
        # Check game over
        gameover, winner = game.gameover()
        if gameover:
            print(f"\nFinal position:")
            simple_board_display(game, col)
            
            if winner == 0:
                print("\n🤝 It's a draw!")
            elif (winner == 1 and human_color == 'Y') or (winner == -1 and human_color == 'R'):
                print("\n🎉 You win! Congratulations!")
            else:
                print("\n🤖 AI wins! Better luck next time!")
            
            print(f"Game lasted {turn} turns")
            print(f"Move sequence: {' → '.join(map(str, moves_history))}")
            break
        
        # Switch turns
        human_turn = not human_turn
    
    # Play again?
    if input("\nPlay again? (y/n): ").lower() == 'y':
        play_game()

if __name__ == '__main__':
    try:
        play_game()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing!")
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure the model file 'best_model_resnet.pth' exists.")