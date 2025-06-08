#!/usr/bin/env python
"""
Simple Human vs AI 3D Connect 4 with minimal UI for testing
"""

from Game3D import Game3D
from MCTS_NN3D import MCTS_NN3D
import torch
import numpy as np
import time

def simple_3d_board_display(game, last_move=None):
    """Simple 3D board display layer by layer"""
    print("\n" + "="*50)
    print("    3D CONNECT 4 BOARD (4×4×4)")
    print("="*50)
    print()
    
    for z in range(game.SIZE-1, -1, -1):  # Top to bottom
        print(f"Layer {z} (height {z}):")
        print("  ", end="")
        for x in range(game.SIZE):
            print(f"  {x} ", end="")
        print()
        
        for y in range(game.SIZE-1, -1, -1):  # Back to front
            print(f"{y} │", end="")
            for x in range(game.SIZE):
                cell = game.board[x, y, z]
                if last_move and last_move == (x, y) and z == game._get_drop_height(x, y):
                    # Highlight last move
                    if cell == 1:
                        print(" O*", end="")  # Yellow with highlight
                    elif cell == -1:
                        print(" X*", end="")  # Red with highlight
                    else:
                        print(" .*", end="")  # Should not happen
                else:
                    if cell == 0:
                        print(" . ", end="")
                    elif cell == 1:
                        print(" O ", end="")  # Yellow
                    else:
                        print(" X ", end="")  # Red
            print(" │")
        print("  " + "─" * (game.SIZE * 3 + 1))
        print()

def get_human_move_3d(game):
    """Get move from human player for 3D game"""
    allowed_moves = game.allowed_moves()
    
    print(f"Available columns: {allowed_moves}")
    print("Enter your move as 'x y' (e.g., '1 1' for center column)")
    
    while True:
        try:
            move_input = input("Enter column coordinates (x y): ").strip()
            if move_input.lower() in ['quit', 'exit']:
                return None, None
            
            x, y = map(int, move_input.split())
            move = (x, y)
            
            if move in allowed_moves:
                return move, move
            else:
                print(f"Invalid move! Choose from: {allowed_moves}")
        except ValueError:
            print("Please enter two numbers separated by space (x y)!")
        except Exception as e:
            print(f"Error: {e}. Please try again!")

def get_ai_move_3d(game, ai_player, simulations=50):
    """Get move from AI for 3D game"""
    print(f"AI is thinking with {simulations} simulations...")
    
    # Create MCTS
    mcts = MCTS_NN3D(ai_player, use_dirichlet=False)
    
    try:
        # Run MCTS simulations
        root = mcts.run_simulations(game, simulations, cpuct=1.0)
        
        if not root.children:
            # Fallback to random move
            allowed_moves = game.allowed_moves()
            if allowed_moves:
                move = np.random.choice(len(allowed_moves))
                return allowed_moves[move], allowed_moves[move]
            return None, None
        
        # Get best move based on visit count
        visits = [child.N for child in root.children]
        best_idx = np.argmax(visits)
        best_move = root.children[best_idx].move
        
        # Show AI analysis
        print("\nAI Analysis:")
        for i, child in enumerate(root.children):
            visits = child.N
            win_rate = 50 * (1 - child.Q) if child.Q != 0 else 50
            marker = "→" if i == best_idx else " "
            print(f"  {marker} Move {child.move}: {visits} visits, {win_rate:.1f}% win rate")
        
        print(f"\nAI chooses move {best_move}")
        return best_move, best_move
        
    except Exception as e:
        print(f"AI error: {e}")
        # Fallback to random move
        allowed_moves = game.allowed_moves()
        if allowed_moves:
            move = np.random.choice(len(allowed_moves))
            return allowed_moves[move], allowed_moves[move]
        return None, None

def create_dummy_ai():
    """Create a dummy AI player that returns random policy and neutral value"""
    def dummy_ai(state_vector):
        # Return neutral evaluation and uniform random policy
        value = torch.tensor([[0.0]])  # Neutral position
        policy = torch.ones((1, 16)) / 16  # Uniform policy over 16 moves
        return value, policy
    
    return dummy_ai

def play_3d_game():
    """Play a simple human vs AI 3D Connect 4 game"""
    print("=" * 60)
    print("    HUMAN vs AI 3D CONNECT 4")
    print("=" * 60)
    print()
    print("Welcome to 3D Connect 4!")
    print("Board size: 4×4×4 cube")
    print("Goal: Get 4 pieces in any straight line (76 possible lines)")
    print("Moves: Enter column coordinates as 'x y' (0-3 for each)")
    print()
    
    # Create dummy AI (since we don't have trained model yet)
    print("Initializing AI player...")
    ai_player = create_dummy_ai()
    print("AI loaded successfully! (Using random policy)")
    
    # Game setup
    human_color = input("Choose your color (O for first player, X for second player): ").upper()
    if human_color not in ['O', 'X']:
        human_color = 'O'
        print("Defaulting to O (first player)")
    
    difficulty = input("Choose difficulty (1=Easy/25 sims, 2=Normal/50 sims, 3=Hard/100 sims): ")
    sim_map = {'1': 25, '2': 50, '3': 100}
    simulations = sim_map.get(difficulty, 50)
    
    # Initialize game
    game = Game3D()
    turn = 0
    moves_history = []
    human_turn = (human_color == 'O')  # O (Yellow/1) goes first
    
    print(f"\nStarting game! You are {'O (Yellow/First)' if human_color == 'O' else 'X (Red/Second)'}")
    print("Type 'quit' to exit anytime")
    print("=" * 60)
    
    while True:
        turn += 1
        current_player = "Human" if human_turn else "AI"
        player_symbol = human_color if human_turn else ('X' if human_color == 'O' else 'O')
        
        print(f"\nTurn {turn} - {current_player} ({player_symbol})")
        simple_3d_board_display(game, moves_history[-1] if moves_history else None)
        
        # Get move
        if human_turn:
            move, display_move = get_human_move_3d(game)
            if move is None:
                print("Game quit by player. Thanks for playing!")
                return
            print(f"You played {display_move}")
        else:
            move, display_move = get_ai_move_3d(game, ai_player, simulations)
            if move is None:
                print("AI encountered an error. Game ending.")
                return
        
        # Make move
        game = game.make_move(move[0], move[1])
        if game is None:
            print("Invalid move! Game error.")
            return
            
        moves_history.append(move)
        
        # Check game over
        if game.is_game_over():
            print(f"\nFinal position:")
            simple_3d_board_display(game, move)
            
            winner = game.get_winner()
            if winner == 0:
                print("\n🤝 It's a draw!")
            elif (winner == 1 and human_color == 'O') or (winner == -1 and human_color == 'X'):
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
        play_3d_game()

def demo_3d_game():
    """Quick demo of 3D Connect 4"""
    print("=" * 60)
    print("    3D CONNECT 4 DEMO")
    print("=" * 60)
    
    game = Game3D()
    print("\nEmpty 4×4×4 board:")
    simple_3d_board_display(game)
    
    print("\nMaking some demo moves...")
    
    # Demo moves
    moves = [(1, 1), (2, 2), (1, 1), (2, 2), (1, 1), (2, 2)]
    move_names = ["Center", "Diagonal", "Center stack", "Diagonal stack", "Center stack", "Diagonal stack"]
    
    for i, (move, name) in enumerate(zip(moves, move_names)):
        print(f"\nMove {i+1}: {name} at {move}")
        game = game.make_move(move[0], move[1])
        if game is None:
            print("Move failed!")
            break
        simple_3d_board_display(game, move)
        
        if game.is_game_over():
            winner = game.get_winner()
            if winner != 0:
                print(f"\nGame over! Player {winner} wins!")
                break
        
        time.sleep(1)
    
    print(f"\nDemo complete. Winning lines detected: {len(game._winning_lines)}")

if __name__ == '__main__':
    try:
        print("3D Connect 4 Options:")
        print("1. Play against AI")
        print("2. Watch demo")
        choice = input("Choose (1/2): ").strip()
        
        if choice == '2':
            demo_3d_game()
        else:
            play_3d_game()
            
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing!")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()