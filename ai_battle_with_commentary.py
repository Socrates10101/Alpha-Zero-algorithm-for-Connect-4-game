#!/usr/bin/env python
"""
AI vs AI battle with detailed commentary and visualization
"""

from MCTS_NN import MCTS_NN
from Game_bitboard import Game
from ResNet import resnet18
import torch
import numpy as np
import time
import os

class ColoredBoard:
    """Helper class for colored terminal output"""
    # ANSI color codes
    YELLOW = '\033[93m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    @staticmethod
    def colored_piece(piece, highlight=False):
        if piece == 'o':
            color = ColoredBoard.YELLOW
        elif piece == 'x':
            color = ColoredBoard.RED
        else:
            return '·'
        
        if highlight:
            return f"{ColoredBoard.BOLD}{color}●{ColoredBoard.RESET}"
        return f"{color}●{ColoredBoard.RESET}"
    
    @staticmethod
    def display_board(game, last_move_col=None):
        """Display board with colors and last move highlight"""
        yellow_list = game.binarystatetoflatlist(game.state[0])
        red_list = game.binarystatetoflatlist(game.state[1])
        
        print("\n  0 1 2 3 4 5 6  ← Column numbers")
        print("  " + "─" * 13)
        
        for row in range(6):
            print(f"{5-row}│", end="")
            for col in range(7):
                idx = row * 7 + col
                highlight = (last_move_col == col and row == 0)  # Simple highlight
                
                if yellow_list[idx] == 1:
                    print(ColoredBoard.colored_piece('o', highlight), end=" ")
                elif red_list[idx] == 1:
                    print(ColoredBoard.colored_piece('x', highlight), end=" ")
                else:
                    print("·", end=" ")
            print("│")
        print("  " + "─" * 13)

def evaluate_position(value, player_turn):
    """Convert neural network value to human-readable evaluation"""
    # NN returns negative values when current player is winning
    eval_from_yellow = value * player_turn * -1
    
    if abs(eval_from_yellow) < 0.1:
        return "Equal position", "="
    elif eval_from_yellow > 0.5:
        return "Yellow is winning", f"+{eval_from_yellow:.2f}"
    elif eval_from_yellow > 0.2:
        return "Yellow is better", f"+{eval_from_yellow:.2f}"
    elif eval_from_yellow < -0.5:
        return "Red is winning", f"{eval_from_yellow:.2f}"
    elif eval_from_yellow < -0.2:
        return "Red is better", f"{eval_from_yellow:.2f}"
    else:
        return "Roughly equal", f"{eval_from_yellow:+.2f}"

def get_opening_name(moves):
    """Get opening name based on moves played"""
    if len(moves) == 0:
        return "Initial Position"
    elif moves == [3]:
        return "Center Opening"
    elif moves == [3, 3]:
        return "Center Counter"
    elif moves == [3, 3, 3, 3]:
        return "Center Stack"
    elif moves[:2] == [3, 2]:
        return "Asymmetric Defense"
    elif moves[:2] == [3, 4]:
        return "Mirror Defense"
    elif len(moves) <= 6 and all(m == 3 for m in moves[:min(len(moves), 6)]):
        return "Center Column Fill"
    else:
        return "Middlegame"

def analyze_critical_moves(game, policy):
    """Analyze if there are critical moves (wins/blocks)"""
    game_check = Game(game.state)
    can_win, win_moves, can_lose, block_moves = game_check.iscritical()
    
    critical_info = []
    if can_win:
        win_cols = [game_check.convert_move_to_col_index(m) for m in win_moves]
        critical_info.append(f"{ColoredBoard.GREEN}Can WIN at column(s): {win_cols}{ColoredBoard.RESET}")
    
    if can_lose:
        block_cols = [game_check.convert_move_to_col_index(m) for m in block_moves]
        critical_info.append(f"{ColoredBoard.RED}Must BLOCK at column(s): {block_cols}{ColoredBoard.RESET}")
    
    return critical_info

def display_evaluation_bar(eval_value, width=40):
    """Display evaluation as a visual bar"""
    # eval_value from Yellow's perspective (-1 to +1)
    normalized = (eval_value + 1) / 2  # 0 to 1
    yellow_width = int(normalized * width)
    red_width = width - yellow_width
    
    bar = f"[{ColoredBoard.YELLOW}{'█' * yellow_width}{ColoredBoard.RED}{'█' * red_width}{ColoredBoard.RESET}]"
    return bar

def ai_vs_ai_battle_commentary():
    """AI vs AI with detailed commentary"""
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print(f"{ColoredBoard.BOLD}=== Alpha Zero Connect 4 - Battle Commentary ==={ColoredBoard.RESET}\n")
    print(f"{ColoredBoard.YELLOW}Yellow ●{ColoredBoard.RESET} vs {ColoredBoard.RED}Red ●{ColoredBoard.RESET}")
    print("\nLoading neural network...", end="", flush=True)
    
    # Load model
    model = resnet18()
    model.load_state_dict(torch.load('./best_model_resnet.pth'))
    model.eval()
    print(" Done!")
    
    # Game setup
    game = Game()
    tree = MCTS_NN(model, use_dirichlet=False)
    rootnode = tree.createNode(game.state)
    currentnode = rootnode
    
    turn = 0
    sim_number = 100
    moves_history = []
    evaluation_history = []
    
    print(f"\nSettings: {sim_number} MCTS simulations per move")
    print("\nPress Enter to start the battle...")
    input()
    
    while not currentnode.isterminal():
        turn += 1
        player = "Yellow" if game.player_turn == 1 else "Red"
        player_color = ColoredBoard.YELLOW if game.player_turn == 1 else ColoredBoard.RED
        
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{ColoredBoard.BOLD}=== Turn {turn} - {player_color}{player}{ColoredBoard.RESET} to move ==={ColoredBoard.RESET}")
        
        # Display current position
        ColoredBoard.display_board(game, moves_history[-1] if moves_history else None)
        
        # Show opening/position name
        opening = get_opening_name(moves_history)
        print(f"\nOpening/Stage: {ColoredBoard.BLUE}{opening}{ColoredBoard.RESET}")
        
        # Get initial evaluation before search
        flat_state = game.state_flattener(game.state)
        with torch.no_grad():
            value, policy = model.forward(flat_state)
        
        eval_desc, eval_score = evaluate_position(value.item(), game.player_turn)
        print(f"\nPosition evaluation: {eval_desc} ({eval_score})")
        
        # Check for critical moves
        critical_info = analyze_critical_moves(game, policy.numpy()[0])
        if critical_info:
            print("\n⚠️  Critical position:")
            for info in critical_info:
                print(f"   {info}")
        
        # Run MCTS
        print(f"\n{player} is thinking", end="", flush=True)
        start_time = time.time()
        
        for i in range(sim_number):
            tree.simulate(currentnode, cpuct=1)
            if i % 20 == 0:
                print(".", end="", flush=True)
        
        think_time = time.time() - start_time
        print(f" ({think_time:.1f}s)")
        
        # Analyze moves
        visits = []
        moves = []
        q_values = []
        
        for child in currentnode.children:
            visits.append(child.N)
            col = game.convert_move_to_col_index(child.move)
            moves.append(col)
            q_values.append(child.Q)
        
        # Sort by visits
        sorted_indices = np.argsort(visits)[::-1]
        
        print("\nMove analysis:")
        print("Col │ Visits │ Win % │ Policy %")
        print("────┼────────┼───────┼─────────")
        
        policy_np = policy.numpy()[0]
        for idx in sorted_indices[:5]:  # Top 5 moves
            col = moves[idx]
            visit = visits[idx]
            q_val = -q_values[idx]  # Negative because it's from child's perspective
            policy_prob = policy_np[col]
            
            # Highlight best move
            if idx == sorted_indices[0]:
                print(f"{ColoredBoard.BOLD}", end="")
            
            print(f" {col}  │  {visit:4d}  │ {50*(1+q_val):4.1f}% │  {policy_prob:5.1%}")
            
            if idx == sorted_indices[0]:
                print(f"{ColoredBoard.RESET}", end="")
        
        # Make best move
        best_idx = np.argmax(visits)
        best_col = moves[best_idx]
        
        print(f"\n{ColoredBoard.BOLD}→ {player} plays column {best_col}{ColoredBoard.RESET}")
        
        # Update game state
        currentnode = currentnode.children[best_idx]
        game = Game(currentnode.state)
        moves_history.append(best_col)
        
        # Store evaluation
        eval_from_yellow = value.item() * game.player_turn * -1
        evaluation_history.append(eval_from_yellow)
        
        # Show evaluation bar
        print("\nEvaluation trend:")
        print(display_evaluation_bar(eval_from_yellow))
        
        # Reinitialize tree
        tree = MCTS_NN(model, use_dirichlet=False)
        rootnode = tree.createNode(game.state)
        currentnode = rootnode
        
        print("\nPress Enter to continue...")
        input()
    
    # Game over
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"{ColoredBoard.BOLD}=== GAME OVER ==={ColoredBoard.RESET}\n")
    
    ColoredBoard.display_board(game)
    
    _, winner = game.gameover()
    if winner == 0:
        print(f"\n{ColoredBoard.BOLD}Result: DRAW{ColoredBoard.RESET}")
        print("Both players played optimally!")
    elif winner == 1:
        print(f"\n{ColoredBoard.YELLOW}{ColoredBoard.BOLD}YELLOW WINS!{ColoredBoard.RESET}")
    else:
        print(f"\n{ColoredBoard.RED}{ColoredBoard.BOLD}RED WINS!{ColoredBoard.RESET}")
    
    print(f"\nTotal moves: {len(moves_history)}")
    print(f"Move sequence: {moves_history}")
    
    # Show evaluation graph
    print("\nEvaluation history (Yellow perspective):")
    for i, eval_val in enumerate(evaluation_history[-10:]):
        move_num = len(evaluation_history) - 10 + i + 1
        if move_num > 0:
            bar_mini = display_evaluation_bar(eval_val, 20)
            print(f"Move {move_num:2d}: {bar_mini} {eval_val:+.3f}")

if __name__ == '__main__':
    ai_vs_ai_battle_commentary()