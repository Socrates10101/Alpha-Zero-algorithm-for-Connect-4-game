#!/usr/bin/env python
"""
AI vs AI battle with live visualization
"""

from MCTS_NN import MCTS_NN
from Game_bitboard import Game
from ResNet import resnet18
import torch
import numpy as np
import time
import os
import sys

class Connect4UI:
    """Terminal-based UI for Connect 4"""
    
    def __init__(self):
        self.board_history = []
        self.eval_history = []
        self.move_history = []
        self.thinking_dots = 0
        
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def draw_header(self):
        print("╔═══════════════════════════════════════════════════════════╗")
        print("║          ALPHA ZERO CONNECT 4 - LIVE BATTLE               ║")
        print("╚═══════════════════════════════════════════════════════════╝")
        print()
    
    def draw_board(self, game, last_col=None, highlight_win=None):
        """Draw the game board with nice borders"""
        yellow_list = game.binarystatetoflatlist(game.state[0])
        red_list = game.binarystatetoflatlist(game.state[1])
        
        # Column numbers
        print("     ", end="")
        for col in range(7):
            if col == last_col:
                print(f"▼{col} ", end="")
            else:
                print(f" {col} ", end="")
        print()
        
        # Top border
        print("   ╔═══════════════════════╗")
        
        # Board rows
        for row in range(6):
            print(f" {5-row} ║ ", end="")
            for col in range(7):
                idx = row * 7 + col
                
                # Check if this position should be highlighted
                is_last_move = False
                if last_col is not None:
                    # Find the topmost piece in last_col
                    for check_row in range(5, -1, -1):
                        check_idx = check_row * 7 + last_col
                        if yellow_list[check_idx] == 1 or red_list[check_idx] == 1:
                            if check_idx == idx:
                                is_last_move = True
                            break
                
                if yellow_list[idx] == 1:
                    if is_last_move:
                        print("⭕", end=" ")  # Highlighted yellow
                    else:
                        print("🟡", end=" ")  # Normal yellow
                elif red_list[idx] == 1:
                    if is_last_move:
                        print("❌", end=" ")  # Highlighted red
                    else:
                        print("🔴", end=" ")  # Normal red
                else:
                    print("⚫", end=" ")  # Empty
            print("║")
        
        # Bottom border
        print("   ╚═══════════════════════╝")
    
    def draw_stats(self, turn, player, eval_score, think_time=None):
        """Draw game statistics"""
        print("\n┌─────────────────────────┐")
        print(f"│ Turn {turn:2d} - {player:6s} {'🟡' if player == 'Yellow' else '🔴'}│")
        print("├─────────────────────────┤")
        
        # Evaluation bar
        eval_text = f"{eval_score:+.3f}"
        if eval_score > 0.5:
            eval_desc = "Yellow winning"
        elif eval_score > 0.2:
            eval_desc = "Yellow better"
        elif eval_score < -0.5:
            eval_desc = "Red winning"
        elif eval_score < -0.2:
            eval_desc = "Red better"
        else:
            eval_desc = "Equal"
        
        print(f"│ Eval: {eval_text:>7s} {eval_desc:<11s}│")
        
        # Visual evaluation bar
        bar_width = 21
        normalized = (eval_score + 1) / 2
        yellow_width = int(normalized * bar_width)
        red_width = bar_width - yellow_width
        
        bar = "🟡" * yellow_width + "🔴" * red_width
        print(f"│ {bar} │")
        
        if think_time:
            print(f"│ Think time: {think_time:5.1f}s      │")
        
        print("└─────────────────────────┘")
    
    def draw_move_analysis(self, moves, visits, q_values, policy):
        """Draw move analysis table"""
        print("\n┌─────┬────────┬────────┬────────┐")
        print("│ Col │ Visits │  Win % │ Policy │")
        print("├─────┼────────┼────────┼────────┤")
        
        # Sort by visits
        sorted_indices = np.argsort(visits)[::-1]
        
        for i, idx in enumerate(sorted_indices[:5]):
            col = moves[idx]
            visit = visits[idx]
            win_pct = 50 * (1 - q_values[idx])  # Convert Q to win percentage
            policy_pct = policy[col] * 100
            
            # Highlight best move
            if i == 0:
                print(f"│ ▶{col}  │ {visit:6d} │ {win_pct:5.1f}% │ {policy_pct:5.1f}% │")
            else:
                print(f"│  {col}  │ {visit:6d} │ {win_pct:5.1f}% │ {policy_pct:5.1f}% │")
        
        print("└─────┴────────┴────────┴────────┘")
    
    def draw_thinking_animation(self):
        """Animated thinking indicator"""
        frames = ["🤔", "🧠", "💭", "⚡"]
        return frames[self.thinking_dots % len(frames)]
    
    def draw_game_over(self, game, winner, moves_history):
        """Draw game over screen"""
        self.clear_screen()
        self.draw_header()
        
        print("\n            🎮 GAME OVER! 🎮\n")
        
        self.draw_board(game)
        
        print("\n" + "="*40)
        
        if winner == 0:
            print("           🤝 IT'S A DRAW! 🤝")
            print("      Both AIs played perfectly!")
        elif winner == 1:
            print("         🟡 YELLOW WINS! 🎉")
        else:
            print("          🔴 RED WINS! 🎉")
        
        print("="*40)
        
        print(f"\nTotal moves: {len(moves_history)}")
        print(f"Game sequence: {' → '.join(map(str, moves_history[:20]))}")
        if len(moves_history) > 20:
            print(f"               {' → '.join(map(str, moves_history[20:]))}")

def run_ai_battle_with_ui(auto_play=False, delay=2.0):
    """Run AI vs AI battle with UI"""
    ui = Connect4UI()
    
    # Load model
    ui.clear_screen()
    ui.draw_header()
    print("Loading neural network... ", end="", flush=True)
    
    model = resnet18()
    model.load_state_dict(torch.load('./best_model_resnet.pth'))
    model.eval()
    print("✓")
    
    # Game setup
    game = Game()
    tree = MCTS_NN(model, use_dirichlet=False)
    rootnode = tree.createNode(game.state)
    currentnode = rootnode
    
    turn = 0
    sim_number = 50  # Reduced for faster gameplay
    moves_history = []
    
    print(f"\nSettings: {sim_number} MCTS simulations per move")
    print(f"Auto-play: {'ON' if auto_play else 'OFF'} (delay: {delay}s)")
    
    if not auto_play:
        print("\nPress Enter to start...")
        input()
    else:
        time.sleep(2)
    
    while not currentnode.isterminal():
        turn += 1
        player = "Yellow" if game.player_turn == 1 else "Red"
        
        # Get initial evaluation
        flat_state = game.state_flattener(game.state)
        with torch.no_grad():
            value, policy = model.forward(flat_state)
        
        eval_from_yellow = value.item() * game.player_turn * -1
        
        # Display current state
        ui.clear_screen()
        ui.draw_header()
        ui.draw_board(game, moves_history[-1] if moves_history else None)
        ui.draw_stats(turn, player, eval_from_yellow)
        
        # Show thinking animation
        print(f"\n  {ui.draw_thinking_animation()} {player} is thinking...", end="", flush=True)
        
        # Run MCTS
        start_time = time.time()
        for i in range(sim_number):
            tree.simulate(currentnode, cpuct=1)
            if i % 10 == 0:
                ui.thinking_dots += 1
                print(f"\r  {ui.draw_thinking_animation()} {player} is thinking{'.' * (i//10 + 1)}", end="", flush=True)
        
        think_time = time.time() - start_time
        
        # Analyze moves
        visits = []
        moves = []
        q_values = []
        
        for child in currentnode.children:
            visits.append(child.N)
            col = game.convert_move_to_col_index(child.move)
            moves.append(col)
            q_values.append(child.Q)
        
        # Clear thinking message
        print("\r" + " " * 50 + "\r", end="")
        
        # Display move analysis
        ui.draw_move_analysis(moves, visits, q_values, policy.numpy()[0])
        
        # Make best move
        best_idx = np.argmax(visits)
        best_col = moves[best_idx]
        
        print(f"\n  ➤ {player} chooses column {best_col}!")
        
        # Update game
        currentnode = currentnode.children[best_idx]
        game = Game(currentnode.state)
        moves_history.append(best_col)
        
        # Store evaluation
        ui.eval_history.append(eval_from_yellow)
        
        # Reinitialize tree
        tree = MCTS_NN(model, use_dirichlet=False)
        rootnode = tree.createNode(game.state)
        currentnode = rootnode
        
        if auto_play:
            time.sleep(delay)
        else:
            print("\n  Press Enter to continue...")
            input()
    
    # Game over
    _, winner = game.gameover()
    ui.draw_game_over(game, winner, moves_history)

def main():
    """Main entry point with menu"""
    print("Connect 4 AI Battle Viewer")
    print("="*30)
    print("1. Step-by-step mode (press Enter after each move)")
    print("2. Auto-play mode (2 second delay)")
    print("3. Fast auto-play mode (0.5 second delay)")
    print("4. Exit")
    
    choice = input("\nSelect mode (1-4): ").strip()
    
    if choice == '1':
        run_ai_battle_with_ui(auto_play=False)
    elif choice == '2':
        run_ai_battle_with_ui(auto_play=True, delay=2.0)
    elif choice == '3':
        run_ai_battle_with_ui(auto_play=True, delay=0.5)
    elif choice == '4':
        print("Goodbye!")
        sys.exit(0)
    else:
        print("Invalid choice!")
        sys.exit(1)

if __name__ == '__main__':
    main()