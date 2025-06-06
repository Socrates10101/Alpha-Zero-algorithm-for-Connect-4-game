#!/usr/bin/env python
"""
Human vs AI Connect 4 with beautiful UI
"""

from MCTS_NN import MCTS_NN, Node
from Game_bitboard import Game
from ResNet import resnet18
import torch
import numpy as np
import time
import os

class HumanVsAIUI:
    """Beautiful UI for Human vs AI Connect 4"""
    
    def __init__(self):
        # Colors
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.GREEN = '\033[92m'
        self.BLUE = '\033[94m'
        self.CYAN = '\033[96m'
        self.MAGENTA = '\033[95m'
        self.BOLD = '\033[1m'
        self.RESET = '\033[0m'
        
        # Game settings
        self.model = None
        self.ai_simulations = 200
        self.human_color = None
        self.ai_color = None
        
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def draw_title(self):
        """Draw game title"""
        print(f"{self.BOLD}{self.CYAN}")
        print("╔══════════════════════════════════════════════╗")
        print("║         HUMAN vs ALPHA ZERO CONNECT 4        ║")
        print("║              Epic Battle Mode                ║")
        print("╚══════════════════════════════════════════════╝")
        print(f"{self.RESET}")
    
    def draw_board(self, game, last_col=None, highlight_cols=None):
        """Draw the game board with colors and highlights"""
        yellow_list = game.binarystatetoflatlist(game.state[0])
        red_list = game.binarystatetoflatlist(game.state[1])
        
        # Column numbers with highlighting
        print("\n   ", end="")
        for col in range(7):
            if highlight_cols and col in highlight_cols:
                print(f"{self.GREEN}{self.BOLD}{col}{self.RESET}   ", end="")
            elif last_col == col:
                print(f"{self.CYAN}{self.BOLD}{col}{self.RESET}   ", end="")
            else:
                print(f"{col}   ", end="")
        print()
        
        # Board border
        print("  ┌───┬───┬───┬───┬───┬───┬───┐")
        
        # Board rows
        for row in range(6):
            print(f"{5-row} │", end="")
            for col in range(7):
                idx = row * 7 + col
                
                # Determine piece to display
                piece = "   "
                if yellow_list[idx] == 1:
                    if last_col == col:
                        piece = f" {self.BOLD}{self.YELLOW}●{self.RESET} "
                    else:
                        piece = f" {self.YELLOW}●{self.RESET} "
                elif red_list[idx] == 1:
                    if last_col == col:
                        piece = f" {self.BOLD}{self.RED}●{self.RESET} "
                    else:
                        piece = f" {self.RED}●{self.RESET} "
                
                # Highlight available moves
                if highlight_cols and col in highlight_cols and piece == "   ":
                    piece = f" {self.GREEN}○{self.RESET} "
                
                print(f"{piece}│", end="")
            print()
            
            # Row separator
            if row < 5:
                print("  ├───┼───┼───┼───┼───┼───┼───┤")
        
        # Bottom border
        print("  └───┴───┴───┴───┴───┴───┴───┘")
    
    def draw_game_status(self, current_player, turn, evaluation=None):
        """Draw current game status"""
        player_color = self.YELLOW if current_player == "Human" else self.RED
        ai_indicator = "🤖" if current_player == "AI" else "👤"
        
        print(f"\n┌─────────────────────────────────┐")
        print(f"│ Turn {turn:2d} - {player_color}{self.BOLD}{current_player:6s}{self.RESET} {ai_indicator} to move │")
        print(f"├─────────────────────────────────┤")
        
        if evaluation is not None:
            eval_desc = self.get_evaluation_description(evaluation)
            print(f"│ AI Evaluation: {eval_desc:<15s} │")
            print(f"│ {self.draw_mini_eval_bar(evaluation):<31s} │")
        
        print(f"└─────────────────────────────────┘")
    
    def get_evaluation_description(self, eval_value):
        """Get human-readable evaluation"""
        if abs(eval_value) < 0.1:
            return f"{self.BLUE}Equal{self.RESET}"
        elif eval_value > 0.3:
            return f"{self.YELLOW}Human ahead{self.RESET}"
        elif eval_value > 0.1:
            return f"{self.YELLOW}Human better{self.RESET}"
        elif eval_value < -0.3:
            return f"{self.RED}AI winning{self.RESET}"
        elif eval_value < -0.1:
            return f"{self.RED}AI better{self.RESET}"
        else:
            return f"{self.BLUE}Close{self.RESET}"
    
    def draw_mini_eval_bar(self, eval_value, width=25):
        """Draw a mini evaluation bar"""
        normalized = (eval_value + 1) / 2
        human_width = int(normalized * width)
        ai_width = width - human_width
        
        bar = f"{self.YELLOW}{'█' * human_width}{self.RED}{'█' * ai_width}{self.RESET}"
        return f"[{bar}]"
    
    def draw_move_prompt(self, available_cols):
        """Draw move input prompt"""
        print(f"\n{self.CYAN}Available moves: {', '.join(map(str, available_cols))}{self.RESET}")
        print(f"{self.BOLD}Enter column (0-6) or 'q' to quit: {self.RESET}", end="")
    
    def draw_ai_thinking(self, simulations):
        """Draw AI thinking animation"""
        print(f"\n{self.MAGENTA}🤖 AI is thinking with {simulations} simulations...{self.RESET}")
        
        # Thinking animation
        for i in range(5):
            thinking_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            for char in thinking_chars:
                print(f"\r{self.CYAN}{char} Analyzing position...{self.RESET}", end="", flush=True)
                time.sleep(0.05)
        print("\r" + " " * 30 + "\r", end="")
    
    def draw_ai_analysis(self, moves, visits, q_values, policy, chosen_col):
        """Draw AI's move analysis"""
        print(f"\n{self.CYAN}🧠 AI Analysis:{self.RESET}")
        print("┌─────┬────────┬────────┬────────┐")
        print("│ Col │ Visits │  Win % │ Policy │")
        print("├─────┼────────┼────────┼────────┤")
        
        # Sort by visits
        sorted_indices = np.argsort(visits)[::-1]
        
        for i, idx in enumerate(sorted_indices[:5]):
            col = moves[idx]
            visit = visits[idx]
            win_pct = 50 * (1 - q_values[idx])
            policy_pct = policy[col] * 100
            
            # Highlight chosen move
            if col == chosen_col:
                marker = f"{self.GREEN}▶{self.RESET}"
                col_str = f"{self.GREEN}{self.BOLD}{col}{self.RESET}"
            else:
                marker = " "
                col_str = str(col)
            
            print(f"│{marker}{col_str:>3s} │ {visit:6d} │ {win_pct:5.1f}% │ {policy_pct:5.1f}% │")
        
        print("└─────┴────────┴────────┴────────┘")
    
    def draw_game_over(self, game, winner, moves_history, final_eval):
        """Draw game over screen"""
        self.clear_screen()
        self.draw_title()
        
        print(f"\n{self.BOLD}{self.MAGENTA}🎮 GAME OVER! 🎮{self.RESET}")
        print("="*50)
        
        self.draw_board(game, moves_history[-1] if moves_history else None)
        
        # Winner announcement
        print("\n" + "="*50)
        if winner == 0:
            print(f"    {self.BOLD}{self.BLUE}🤝 IT'S A DRAW! 🤝{self.RESET}")
            print("     Great game! Neither side could break through.")
        elif (winner == 1 and self.human_color == "Yellow") or (winner == -1 and self.human_color == "Red"):
            print(f"    {self.BOLD}{self.GREEN}🏆 HUMAN WINS! 🎉{self.RESET}")
            print("     Congratulations! You defeated Alpha Zero!")
        else:
            print(f"    {self.BOLD}{self.RED}🤖 AI WINS! 🤖{self.RESET}")
            print("     Alpha Zero proved its superiority this time!")
        print("="*50)
        
        # Game statistics
        print(f"\nGame Statistics:")
        print(f"  Total moves: {len(moves_history)}")
        print(f"  Your color: {self.human_color}")
        print(f"  Final evaluation: {final_eval:+.3f}")
        print(f"  Move sequence: {' → '.join(map(str, moves_history[:15]))}")
        if len(moves_history) > 15:
            print(f"                 {' → '.join(map(str, moves_history[15:]))}")
    
    def get_setup_choice(self):
        """Get game setup from user"""
        self.clear_screen()
        self.draw_title()
        
        print(f"\n{self.BOLD}Game Setup{self.RESET}")
        print("="*20)
        print("1. 🟡 Play as Yellow (go first)")
        print("2. 🔴 Play as Red (go second)")
        print("3. 🎲 Random choice")
        print("4. ❌ Exit")
        
        while True:
            choice = input(f"\n{self.CYAN}Select option (1-4): {self.RESET}").strip()
            
            if choice == '1':
                self.human_color = "Yellow"
                self.ai_color = "Red"
                return True
            elif choice == '2':
                self.human_color = "Red"
                self.ai_color = "Yellow"
                return True
            elif choice == '3':
                import random
                if random.choice([True, False]):
                    self.human_color = "Yellow"
                    self.ai_color = "Red"
                else:
                    self.human_color = "Red"
                    self.ai_color = "Yellow"
                print(f"{self.CYAN}You've been assigned: {self.human_color}!{self.RESET}")
                time.sleep(1.5)
                return True
            elif choice == '4':
                return False
            else:
                print(f"{self.RED}Invalid choice! Please enter 1-4.{self.RESET}")
    
    def get_difficulty_choice(self):
        """Get AI difficulty setting"""
        print(f"\n{self.BOLD}AI Difficulty{self.RESET}")
        print("="*15)
        print("1. 😊 Easy (50 simulations)")
        print("2. 🤔 Normal (200 simulations)")
        print("3. 😰 Hard (500 simulations)")
        print("4. 💀 Nightmare (1000 simulations)")
        
        while True:
            choice = input(f"\n{self.CYAN}Select difficulty (1-4): {self.RESET}").strip()
            
            if choice == '1':
                self.ai_simulations = 50
                return
            elif choice == '2':
                self.ai_simulations = 200
                return
            elif choice == '3':
                self.ai_simulations = 500
                return
            elif choice == '4':
                self.ai_simulations = 1000
                return
            else:
                print(f"{self.RED}Invalid choice! Please enter 1-4.{self.RESET}")
    
    def load_model(self):
        """Load the trained model"""
        print(f"\n{self.CYAN}Loading Alpha Zero neural network...{self.RESET}", end="", flush=True)
        
        try:
            self.model = resnet18()
            self.model.load_state_dict(torch.load('./best_model_resnet.pth'))
            self.model.eval()
            print(f" {self.GREEN}✓{self.RESET}")
            return True
        except Exception as e:
            print(f" {self.RED}✗{self.RESET}")
            print(f"{self.RED}Error loading model: {e}{self.RESET}")
            return False
    
    def get_human_move(self, game):
        """Get move from human player"""
        allowed_moves = game.allowed_moves()
        available_cols = [game.convert_move_to_col_index(move) for move in allowed_moves]
        
        while True:
            self.draw_move_prompt(available_cols)
            user_input = input().strip().lower()
            
            if user_input == 'q':
                return None, None
            
            try:
                col = int(user_input)
                if col in available_cols:
                    # Find the actual move
                    for move in allowed_moves:
                        if game.convert_move_to_col_index(move) == col:
                            return move, col
                else:
                    print(f"{self.RED}Column {col} is not available! Choose from: {available_cols}{self.RESET}")
            except ValueError:
                print(f"{self.RED}Invalid input! Enter a number 0-6 or 'q' to quit.{self.RESET}")
    
    def get_ai_move(self, game):
        """Get move from AI"""
        # Create MCTS tree
        tree = MCTS_NN(self.model, use_dirichlet=False)
        rootnode = tree.createNode(game.state)
        
        # Show thinking animation
        self.draw_ai_thinking(self.ai_simulations)
        
        # Run MCTS simulations
        start_time = time.time()
        for _ in range(self.ai_simulations):
            tree.simulate(rootnode, cpuct=1)
        think_time = time.time() - start_time
        
        # Get analysis
        visits = []
        moves = []
        q_values = []
        
        for child in rootnode.children:
            visits.append(child.N)
            col = game.convert_move_to_col_index(child.move)
            moves.append(col)
            q_values.append(child.Q)
        
        # Choose best move
        best_idx = np.argmax(visits)
        best_move = rootnode.children[best_idx].move
        best_col = moves[best_idx]
        
        # Get policy for analysis
        flat_state = game.state_flattener(game.state)
        with torch.no_grad():
            _, policy = self.model.forward(flat_state)
        
        # Show analysis
        self.draw_ai_analysis(moves, visits, q_values, policy.numpy()[0], best_col)
        
        print(f"\n{self.CYAN}AI chooses column {best_col} after {think_time:.1f}s of thinking.{self.RESET}")
        
        return best_move, best_col
    
    def run_game(self):
        """Run the human vs AI game"""
        # Setup
        if not self.get_setup_choice():
            return
        
        self.get_difficulty_choice()
        
        if not self.load_model():
            return
        
        print(f"\n{self.GREEN}Game starting in 3 seconds...{self.RESET}")
        time.sleep(3)
        
        # Initialize game
        game = Game()
        turn = 0
        moves_history = []
        
        # Determine who goes first
        human_turn = (self.human_color == "Yellow")
        
        while True:
            turn += 1
            
            # Clear screen and draw current state
            self.clear_screen()
            self.draw_title()
            
            # Get current evaluation
            flat_state = game.state_flattener(game.state)
            with torch.no_grad():
                value, _ = self.model.forward(flat_state)
            
            # Adjust evaluation from Yellow's perspective
            eval_from_human = value.item()
            if self.human_color == "Red":
                eval_from_human *= -1
            
            current_player = "Human" if human_turn else "AI"
            self.draw_game_status(current_player, turn, eval_from_human)
            
            # Show available moves for human
            allowed_moves = game.allowed_moves()
            available_cols = [game.convert_move_to_col_index(move) for move in allowed_moves]
            
            if human_turn:
                self.draw_board(game, moves_history[-1] if moves_history else None, available_cols)
                
                # Get human move
                move, col = self.get_human_move(game)
                if move is None:  # Quit
                    print(f"\n{self.CYAN}Thanks for playing! Goodbye! 👋{self.RESET}")
                    return
                
                print(f"\n{self.GREEN}You played column {col}!{self.RESET}")
            else:
                self.draw_board(game, moves_history[-1] if moves_history else None)
                
                # Get AI move
                move, col = self.get_ai_move(game)
            
            # Make the move
            game.takestep(move)
            moves_history.append(col)
            
            # Check if game is over
            gameover, winner = game.gameover()
            if gameover:
                self.draw_game_over(game, winner, moves_history, eval_from_human)
                break
            
            # Switch turns
            human_turn = not human_turn
            
            if not human_turn:  # Pause before AI move
                input(f"\n{self.CYAN}Press Enter to see AI's move...{self.RESET}")
        
        # Play again?
        print(f"\n{self.CYAN}Would you like to play again? (y/n): {self.RESET}", end="")
        if input().strip().lower() == 'y':
            self.run_game()

def main():
    """Main entry point"""
    ui = HumanVsAIUI()
    
    try:
        ui.run_game()
    except KeyboardInterrupt:
        print(f"\n\n{ui.CYAN}Game interrupted. Thanks for playing! 👋{ui.RESET}")

if __name__ == '__main__':
    main()