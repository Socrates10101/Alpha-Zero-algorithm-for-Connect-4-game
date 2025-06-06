#!/usr/bin/env python
"""
AI vs AI battle with automatic visualization - no user input required
"""

from MCTS_NN import MCTS_NN
from Game_bitboard import Game
from ResNet import resnet18
import torch
import numpy as np
import time
import os

class Connect4AutoBattle:
    """Automated Connect 4 battle with live commentary"""
    
    def __init__(self):
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.GREEN = '\033[92m'
        self.BLUE = '\033[94m'
        self.BOLD = '\033[1m'
        self.RESET = '\033[0m'
        
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def draw_board(self, game, last_col=None):
        """Draw the game board with colors"""
        yellow_list = game.binarystatetoflatlist(game.state[0])
        red_list = game.binarystatetoflatlist(game.state[1])
        
        print("\n" + " " * 8 + "CONNECT 4 BATTLE")
        print(" " * 8 + "="*15)
        print("\n   0   1   2   3   4   5   6")
        print("  ┌───┬───┬───┬───┬───┬───┬───┐")
        
        for row in range(6):
            print(f"{5-row} │", end="")
            for col in range(7):
                idx = row * 7 + col
                
                if yellow_list[idx] == 1:
                    if last_col == col:
                        print(f" {self.BOLD}{self.YELLOW}●{self.RESET} │", end="")
                    else:
                        print(f" {self.YELLOW}●{self.RESET} │", end="")
                elif red_list[idx] == 1:
                    if last_col == col:
                        print(f" {self.BOLD}{self.RED}●{self.RESET} │", end="")
                    else:
                        print(f" {self.RED}●{self.RESET} │", end="")
                else:
                    print("   │", end="")
            print()
            
            if row < 5:
                print("  ├───┼───┼───┼───┼───┼───┼───┤")
        
        print("  └───┴───┴───┴───┴───┴───┴───┘")
    
    def evaluate_position(self, value, player_turn):
        """Convert NN value to readable evaluation"""
        eval_from_yellow = value * player_turn * -1
        
        if abs(eval_from_yellow) < 0.1:
            return f"{self.BLUE}EQUAL{self.RESET}", eval_from_yellow
        elif eval_from_yellow > 0.3:
            return f"{self.YELLOW}YELLOW WINNING{self.RESET}", eval_from_yellow
        elif eval_from_yellow > 0.1:
            return f"{self.YELLOW}Yellow better{self.RESET}", eval_from_yellow
        elif eval_from_yellow < -0.3:
            return f"{self.RED}RED WINNING{self.RESET}", eval_from_yellow
        elif eval_from_yellow < -0.1:
            return f"{self.RED}Red better{self.RESET}", eval_from_yellow
        else:
            return f"{self.BLUE}Equal{self.RESET}", eval_from_yellow
    
    def draw_evaluation_bar(self, eval_value, width=30):
        """Visual evaluation bar"""
        normalized = (eval_value + 1) / 2
        yellow_width = int(normalized * width)
        red_width = width - yellow_width
        
        bar = f"{self.YELLOW}{'█' * yellow_width}{self.RED}{'█' * red_width}{self.RESET}"
        return f"[{bar}] {eval_value:+.3f}"
    
    def get_opening_comment(self, moves):
        """Get opening commentary"""
        if len(moves) == 0:
            return "🎮 Game starting - empty board"
        elif moves == [3]:
            return "🎯 Classic center opening!"
        elif moves == [3, 3]:
            return "⚡ Mirror response in center"
        elif len(moves) <= 6 and all(m == 3 for m in moves):
            return "🔥 Center column battle continues"
        elif 3 in moves[:4]:
            return "📚 Center-focused opening"
        else:
            return "🧠 Complex middlegame position"
    
    def analyze_critical_moves(self, game):
        """Check for critical tactical moves"""
        game_check = Game(game.state)
        can_win, win_moves, can_lose, block_moves = game_check.iscritical()
        
        if can_win:
            win_cols = [game_check.convert_move_to_col_index(m) for m in win_moves]
            return f"⚡ {self.GREEN}WINNING MOVE available: {win_cols}{self.RESET}"
        
        if can_lose:
            block_cols = [game_check.convert_move_to_col_index(m) for m in block_moves]
            return f"🛡️  {self.RED}MUST BLOCK: {block_cols}{self.RESET}"
        
        return None
    
    def run_battle(self, sim_number=50, delay=1.5):
        """Run the automatic AI battle"""
        self.clear_screen()
        
        print(f"{self.BOLD}{self.BLUE}ALPHA ZERO CONNECT 4 - AUTO BATTLE{self.RESET}")
        print("="*50)
        print("Loading neural network...", end="", flush=True)
        
        # Load model
        model = resnet18()
        model.load_state_dict(torch.load('./best_model_resnet.pth'))
        model.eval()
        print(" ✓")
        
        print(f"Battle settings: {sim_number} MCTS simulations, {delay}s delay")
        print("Starting in 3 seconds...")
        time.sleep(3)
        
        # Initialize game
        game = Game()
        tree = MCTS_NN(model, use_dirichlet=False)
        rootnode = tree.createNode(game.state)
        currentnode = rootnode
        
        turn = 0
        moves_history = []
        eval_history = []
        
        while not currentnode.isterminal():
            turn += 1
            player = "Yellow" if game.player_turn == 1 else "Red"
            player_color = self.YELLOW if game.player_turn == 1 else self.RED
            
            self.clear_screen()
            
            # Header
            print(f"{self.BOLD}TURN {turn} - {player_color}{player.upper()}{self.RESET} TO MOVE")
            print("="*50)
            
            # Board
            self.draw_board(game, moves_history[-1] if moves_history else None)
            
            # Opening comment
            opening_comment = self.get_opening_comment(moves_history)
            print(f"\n📖 {opening_comment}")
            
            # Get evaluation
            flat_state = game.state_flattener(game.state)
            with torch.no_grad():
                value, policy = model.forward(flat_state)
            
            eval_from_yellow = value.item() * game.player_turn * -1
            eval_desc, eval_val = self.evaluate_position(value.item(), game.player_turn)
            
            print(f"\n📊 Position: {eval_desc}")
            print(f"    {self.draw_evaluation_bar(eval_from_yellow)}")
            
            # Check for critical moves
            critical = self.analyze_critical_moves(game)
            if critical:
                print(f"\n{critical}")
            
            # Thinking phase
            print(f"\n🤔 {player} is calculating", end="", flush=True)
            
            start_time = time.time()
            for i in range(sim_number):
                tree.simulate(currentnode, cpuct=1)
                if i % 10 == 0:
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
            
            # Display top moves
            print("\n🎯 Top move candidates:")
            sorted_indices = np.argsort(visits)[::-1]
            policy_np = policy.numpy()[0]
            
            for i, idx in enumerate(sorted_indices[:3]):
                col = moves[idx]
                visit = visits[idx]
                win_pct = 50 * (1 - q_values[idx])
                policy_pct = policy_np[col] * 100
                
                marker = "👑" if i == 0 else f" {i+1}."
                print(f"  {marker} Column {col}: {visit} visits, {win_pct:.1f}% win, {policy_pct:.1f}% NN")
            
            # Make move
            best_idx = np.argmax(visits)
            best_col = moves[best_idx]
            
            print(f"\n➤ {self.BOLD}{player_color}{player} plays column {best_col}!{self.RESET}")
            
            # Update game
            currentnode = currentnode.children[best_idx]
            game = Game(currentnode.state)
            moves_history.append(best_col)
            eval_history.append(eval_from_yellow)
            
            # Reinitialize tree
            tree = MCTS_NN(model, use_dirichlet=False)
            rootnode = tree.createNode(game.state)
            currentnode = rootnode
            
            time.sleep(delay)
        
        # Game over
        self.clear_screen()
        print(f"{self.BOLD}🎊 GAME OVER! 🎊{self.RESET}")
        print("="*50)
        
        self.draw_board(game, moves_history[-1] if moves_history else None)
        
        _, winner = game.gameover()
        if winner == 0:
            print(f"\n🤝 {self.BOLD}{self.BLUE}IT'S A DRAW!{self.RESET}")
            print("Both AIs played perfectly - as expected in Connect 4!")
        elif winner == 1:
            print(f"\n🏆 {self.BOLD}{self.YELLOW}YELLOW WINS!{self.RESET}")
        else:
            print(f"\n🏆 {self.BOLD}{self.RED}RED WINS!{self.RESET}")
        
        print(f"\n📈 Game statistics:")
        print(f"   Total moves: {len(moves_history)}")
        print(f"   Game sequence: {' → '.join(map(str, moves_history))}")
        
        # Evaluation trend
        if eval_history:
            print(f"\n📊 Final evaluations trend:")
            for i, eval_val in enumerate(eval_history[-5:]):
                move_num = len(eval_history) - 5 + i + 1
                print(f"   Move {move_num:2d}: {self.draw_evaluation_bar(eval_val, 20)}")

def main():
    """Main entry point"""
    battle = Connect4AutoBattle()
    print("Starting Alpha Zero Connect 4 Auto Battle...")
    print("This will run automatically without user input.")
    print("\nChoose battle speed:")
    print("Running with moderate speed (1.5s delay, 50 simulations)")
    print("\nStarting battle in 2 seconds...")
    time.sleep(2)
    
    battle.run_battle(sim_number=50, delay=1.5)

if __name__ == '__main__':
    main()