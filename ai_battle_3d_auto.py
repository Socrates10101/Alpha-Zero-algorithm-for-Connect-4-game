#!/usr/bin/env python
"""
AI vs AI 3D Connect 4 battle with automatic visualization and commentary
"""

from Game3D import Game3D
from MCTS_NN3D import MCTS_NN3D
import torch
import numpy as np
import time
import os
import random

class Connect4_3D_AutoBattle:
    """Automated 3D Connect 4 battle with live commentary"""
    
    def __init__(self):
        # ANSI color codes
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.GREEN = '\033[92m'
        self.BLUE = '\033[94m'
        self.CYAN = '\033[96m'
        self.MAGENTA = '\033[95m'
        self.BOLD = '\033[1m'
        self.RESET = '\033[0m'
        
        # Player symbols
        self.PLAYER_SYMBOLS = {1: 'O', -1: 'X'}
        self.PLAYER_NAMES = {1: 'Yellow (O)', -1: 'Red (X)'}
        
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def draw_3d_board(self, game, last_move=None, highlight_winning_line=None):
        """Draw the 3D game board with colors and highlights"""
        print(f"\n{self.BOLD}{self.CYAN}    3D CONNECT 4 BATTLE{self.RESET}")
        print(f"{self.CYAN}    ==================={self.RESET}")
        print()
        
        for z in range(game.SIZE-1, -1, -1):  # Top to bottom
            print(f"{self.BOLD}Layer {z} (height {z}):{self.RESET}")
            
            # Column headers
            print("    ", end="")
            for x in range(game.SIZE):
                print(f"  {x} ", end="")
            print()
            
            # Board rows
            for y in range(game.SIZE-1, -1, -1):  # Back to front
                print(f"  {y} ", end="")
                
                for x in range(game.SIZE):
                    cell = game.board[x, y, z]
                    is_last_move = (last_move and last_move == (x, y) and 
                                  z == game._get_drop_height(x, y) - 1)
                    is_winning = (highlight_winning_line and 
                                (x, y, z) in highlight_winning_line)
                    
                    if cell == 0:
                        print("[ ]", end="")
                    elif cell == 1:  # Yellow
                        if is_winning:
                            print(f"[{self.BOLD}{self.YELLOW}O{self.RESET}]", end="")
                        elif is_last_move:
                            print(f"[{self.BOLD}{self.YELLOW}●{self.RESET}]", end="")
                        else:
                            print(f"[{self.YELLOW}O{self.RESET}]", end="")
                    else:  # Red
                        if is_winning:
                            print(f"[{self.BOLD}{self.RED}X{self.RESET}]", end="")
                        elif is_last_move:
                            print(f"[{self.BOLD}{self.RED}●{self.RESET}]", end="")
                        else:
                            print(f"[{self.RED}X{self.RESET}]", end="")
                print()
            print()
    
    def evaluate_position(self, game, ai_player):
        """Get AI evaluation of current position"""
        try:
            state_vector = game.get_state_vector()
            value, policy = ai_player(state_vector)
            return value.item()
        except:
            return 0.0
    
    def format_evaluation(self, eval_value, current_player):
        """Format evaluation with colors"""
        # Convert to perspective of Yellow (player 1)
        eval_from_yellow = eval_value * current_player * -1
        
        if abs(eval_from_yellow) < 0.1:
            return f"{self.BLUE}BALANCED{self.RESET}", eval_from_yellow
        elif eval_from_yellow > 0.5:
            return f"{self.BOLD}{self.YELLOW}YELLOW DOMINANT{self.RESET}", eval_from_yellow
        elif eval_from_yellow > 0.2:
            return f"{self.YELLOW}Yellow advantage{self.RESET}", eval_from_yellow
        elif eval_from_yellow < -0.5:
            return f"{self.BOLD}{self.RED}RED DOMINANT{self.RESET}", eval_from_yellow
        elif eval_from_yellow < -0.2:
            return f"{self.RED}Red advantage{self.RESET}", eval_from_yellow
        else:
            return f"{self.BLUE}Slight edge{self.RESET}", eval_from_yellow
    
    def draw_evaluation_bar(self, eval_value, width=25):
        """Visual evaluation bar"""
        normalized = max(0, min(1, (eval_value + 1) / 2))
        yellow_width = int(normalized * width)
        red_width = width - yellow_width
        
        bar = f"{self.YELLOW}{'█' * yellow_width}{self.RED}{'█' * red_width}{self.RESET}"
        return f"[{bar}] {eval_value:+.3f}"
    
    def get_tactical_comment(self, game, move, moves_history):
        """Generate tactical commentary"""
        x, y = move
        move_count = len(moves_history)
        
        # Position-based comments
        if (x, y) == (1, 1) or (x, y) == (2, 2):
            comments = [
                "🎯 Strategic center control!",
                "📐 Claiming the power positions",
                "⚡ Center dominance strategy"
            ]
        elif x == 0 or x == 3 or y == 0 or y == 3:
            comments = [
                "🏰 Corner and edge play",
                "🔄 Perimeter positioning",
                "📍 Boundary control"
            ]
        else:
            comments = [
                "🤔 Interesting middle-ground choice",
                "⚖️ Balanced positioning",
                "🎲 Creative placement"
            ]
        
        # Move count based comments
        if move_count <= 4:
            return random.choice(comments) + " - Opening development"
        elif move_count <= 10:
            return random.choice(comments) + " - Middle game tactics"
        else:
            return random.choice(comments) + " - End game precision"
    
    def get_3d_strategic_comment(self, game, move):
        """3D-specific strategic commentary"""
        x, y = move
        height = game._get_drop_height(x, y) - 1  # Height after move
        
        comments = []
        
        # Height-based strategy
        if height == 0:
            comments.append("🏗️ Foundation building")
        elif height == 1:
            comments.append("📈 Building vertical presence")
        elif height == 2:
            comments.append("🏔️ High-level positioning")
        else:
            comments.append("🎪 Top-tier placement")
        
        # 3D line potential
        intersecting_lines = 0
        for line in game._winning_lines:
            if (x, y, height) in line:
                intersecting_lines += 1
        
        if intersecting_lines >= 10:
            comments.append("⭐ High-value intersection!")
        elif intersecting_lines >= 7:
            comments.append("🔥 Strong tactical spot")
        elif intersecting_lines >= 4:
            comments.append("✨ Good line potential")
        
        return " | ".join(comments)
    
    def create_dummy_ais(self):
        """Create two different dummy AIs with slight personality differences"""
        def aggressive_ai(state_vector):
            # Slightly favor attacking moves
            value = torch.tensor([[random.uniform(-0.2, 0.2)]])
            policy = torch.ones((1, 16)) / 16
            # Add some randomness to make it interesting
            policy = policy + torch.rand_like(policy) * 0.1
            policy = policy / policy.sum()
            return value, policy
        
        def defensive_ai(state_vector):
            # Slightly more conservative
            value = torch.tensor([[random.uniform(-0.1, 0.1)]])
            policy = torch.ones((1, 16)) / 16
            # Add different randomness pattern
            policy = policy + torch.rand_like(policy) * 0.05
            policy = policy / policy.sum()
            return value, policy
        
        return aggressive_ai, defensive_ai
    
    def get_ai_move(self, game, ai_player, player_name, simulations=30):
        """Get AI move with analysis"""
        print(f"{self.CYAN}🤖 {player_name} is analyzing position...{self.RESET}")
        
        mcts = MCTS_NN3D(ai_player, use_dirichlet=False)
        
        try:
            root = mcts.run_simulations(game, simulations, cpuct=1.0)
            
            if not root.children:
                # Fallback
                allowed_moves = game.allowed_moves()
                if allowed_moves:
                    return random.choice(allowed_moves)
                return None
            
            # Get best move
            visits = [child.N for child in root.children]
            best_idx = np.argmax(visits)
            best_move = root.children[best_idx].move
            
            # Show top 3 moves analysis
            print(f"\n{self.MAGENTA}🧠 AI Analysis:{self.RESET}")
            sorted_children = sorted(root.children, key=lambda x: x.N, reverse=True)
            
            for i, child in enumerate(sorted_children[:3]):
                visits = child.N
                win_rate = 50 * (1 - child.Q) if child.Q != 0 else 50
                marker = "👉" if i == 0 else "  "
                print(f"  {marker} Move {child.move}: {visits:2d} visits, {win_rate:5.1f}% win rate")
            
            return best_move
            
        except Exception as e:
            print(f"AI error: {e}")
            allowed_moves = game.allowed_moves()
            return random.choice(allowed_moves) if allowed_moves else None
    
    def battle(self, simulations_p1=30, simulations_p2=30, delay=2.0):
        """Run an AI vs AI battle"""
        print(f"{self.BOLD}{self.GREEN}🚀 STARTING 3D CONNECT 4 AI BATTLE!{self.RESET}")
        print(f"{self.CYAN}⚡ Player 1 (Yellow/O): {simulations_p1} simulations{self.RESET}")
        print(f"{self.CYAN}⚡ Player 2 (Red/X): {simulations_p2} simulations{self.RESET}")
        print()
        
        # Create AI players
        ai1, ai2 = self.create_dummy_ais()
        ai_players = {1: ai1, -1: ai2}
        simulations = {1: simulations_p1, -1: simulations_p2}
        
        # Initialize game
        game = Game3D()
        turn = 0
        moves_history = []
        
        print("🎮 Battle commencing in 3...")
        time.sleep(1)
        print("2...")
        time.sleep(1)
        print("1...")
        time.sleep(1)
        print("GO! 🎯")
        time.sleep(delay)
        
        while not game.is_game_over():
            turn += 1
            current_player = game.player_turn
            player_name = self.PLAYER_NAMES[current_player]
            
            self.clear_screen()
            
            print(f"{self.BOLD}🏆 3D CONNECT 4 AI BATTLE - Turn {turn}{self.RESET}")
            print(f"{self.CYAN}Current Player: {player_name}{self.RESET}")
            print()
            
            # Show board
            last_move = moves_history[-1] if moves_history else None
            self.draw_3d_board(game, last_move)
            
            # Show evaluation
            eval_value = self.evaluate_position(game, ai_players[current_player])
            eval_text, eval_num = self.format_evaluation(eval_value, current_player)
            eval_bar = self.draw_evaluation_bar(eval_num)
            
            print(f"📊 Position: {eval_text}")
            print(f"📈 Evaluation: {eval_bar}")
            print()
            
            # Get AI move
            move = self.get_ai_move(game, ai_players[current_player], player_name, 
                                  simulations[current_player])
            
            if move is None:
                print("❌ No valid moves available!")
                break
            
            # Commentary
            tactical_comment = self.get_tactical_comment(game, move, moves_history)
            strategic_comment = self.get_3d_strategic_comment(game, move)
            
            print(f"🎯 {player_name} plays {move}")
            print(f"💬 {tactical_comment}")
            print(f"🧩 3D Strategy: {strategic_comment}")
            
            # Make move
            new_game = game.make_move(move[0], move[1])
            if new_game is None:
                print("❌ Invalid move!")
                break
            
            game = new_game
            moves_history.append(move)
            
            time.sleep(delay)
        
        # Game over
        self.clear_screen()
        print(f"{self.BOLD}🏁 GAME OVER! 🏁{self.RESET}")
        print()
        
        # Show final board
        winner = game.get_winner()
        winning_line = None
        
        # Try to find winning line for highlight
        if winner != 0:
            for line in game._winning_lines:
                if all(game.board[x, y, z] == winner for x, y, z in line):
                    winning_line = line
                    break
        
        self.draw_3d_board(game, moves_history[-1] if moves_history else None, winning_line)
        
        # Announce result
        if winner == 0:
            print(f"{self.BOLD}{self.BLUE}🤝 DRAW! Both AIs played excellently!{self.RESET}")
        else:
            winner_name = self.PLAYER_NAMES[winner]
            if winner == 1:
                print(f"{self.BOLD}{self.YELLOW}🏆 {winner_name} WINS!{self.RESET}")
            else:
                print(f"{self.BOLD}{self.RED}🏆 {winner_name} WINS!{self.RESET}")
            
            if winning_line:
                print(f"🎯 Winning line: {' → '.join(map(str, winning_line))}")
        
        print(f"📊 Game statistics:")
        print(f"   🎲 Total turns: {turn}")
        print(f"   📝 Moves: {' → '.join(map(str, moves_history))}")
        print(f"   🎮 Average thinking time: {delay}s per move")
        
        return winner, turn, moves_history

def main():
    """Main function to run AI battles"""
    battle = Connect4_3D_AutoBattle()
    
    print("🎮 3D Connect 4 AI Battle Setup")
    print("=" * 40)
    
    try:
        # Get settings
        p1_sims = input("Player 1 (Yellow) simulations (default: 30): ").strip()
        p1_sims = int(p1_sims) if p1_sims else 30
        
        p2_sims = input("Player 2 (Red) simulations (default: 30): ").strip() 
        p2_sims = int(p2_sims) if p2_sims else 30
        
        delay = input("Delay between moves in seconds (default: 2.0): ").strip()
        delay = float(delay) if delay else 2.0
        
        print()
        
        # Run battle
        winner, turns, moves = battle.battle(p1_sims, p2_sims, delay)
        
        # Ask for another battle
        if input("\n🔄 Run another battle? (y/n): ").lower() == 'y':
            main()
            
    except KeyboardInterrupt:
        print(f"\n{battle.YELLOW}⚡ Battle interrupted! Thanks for watching!{battle.RESET}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()