#  ================ Game Selector for 2D and 3D Connect 4 =================== #
# Name:             game_selector.py
# Description:      Unified interface to switch between 2D and 3D Connect 4
# Authors:          AI Assistant
# Date:             2025
# License:          BSD 3-Clause License
# ============================================================================ #

import os
import sys

class GameSelector:
    """
    Class to manage switching between 2D and 3D Connect 4 games.
    """
    
    def __init__(self):
        self.current_mode = None
        self.available_modes = {
            '2d': {
                'name': '2D Connect 4 (6x7)',
                'description': 'Classic Connect 4 on 6x7 board',
                'game_module': 'Game_bitboard',
                'config_module': 'config',
                'mcts_module': 'MCTS_NN',
                'resnet_module': 'ResNet',
                'main_module': 'Main'
            },
            '3d': {
                'name': '3D Connect 4 (4x4x4)',
                'description': '3D Connect 4 on 4x4x4 cube',
                'game_module': 'Game3D',
                'config_module': 'config3d',
                'mcts_module': 'MCTS_NN3D',
                'resnet_module': 'ResNet3D',
                'main_module': 'Main3D'
            }
        }
    
    def display_menu(self):
        """Display game selection menu"""
        print("=" * 60)
        print("    CONNECT 4 GAME SELECTOR")
        print("=" * 60)
        print()
        print("Available games:")
        for key, game_info in self.available_modes.items():
            print(f"  {key.upper()}: {game_info['name']}")
            print(f"      {game_info['description']}")
            print()
        print("  Q: Quit")
        print()
    
    def get_user_choice(self):
        """Get user's game mode choice"""
        while True:
            choice = input("Select game mode (2d/3d/q): ").lower().strip()
            
            if choice == 'q' or choice == 'quit':
                return None
            elif choice in self.available_modes:
                return choice
            else:
                print("Invalid choice. Please enter '2d', '3d', or 'q'.")
    
    def check_requirements(self, mode):
        """Check if all required files exist for the selected mode"""
        game_info = self.available_modes[mode]
        required_files = [
            f"{game_info['game_module']}.py",
            f"{game_info['config_module']}.py",
            f"{game_info['mcts_module']}.py",
            f"{game_info['resnet_module']}.py"
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            print(f"Error: Missing required files for {mode.upper()} mode:")
            for file in missing_files:
                print(f"  - {file}")
            return False
        
        return True
    
    def set_game_mode(self, mode):
        """Set the current game mode and configure imports"""
        if mode not in self.available_modes:
            print(f"Error: Unknown game mode '{mode}'")
            return False
        
        if not self.check_requirements(mode):
            return False
        
        self.current_mode = mode
        game_info = self.available_modes[mode]
        
        print(f"Selected: {game_info['name']}")
        print(f"Game module: {game_info['game_module']}")
        print(f"Config module: {game_info['config_module']}")
        print()
        
        return True
    
    def launch_game_training(self, mode):
        """Launch training for the selected game mode"""
        if mode == '2d':
            return self.launch_2d_training()
        elif mode == '3d':
            return self.launch_3d_training()
    
    def launch_2d_training(self):
        """Launch 2D Connect 4 training"""
        try:
            import Main
            print("Starting 2D Connect 4 training...")
            Main.launch()
        except ImportError as e:
            print(f"Error importing 2D modules: {e}")
            return False
        except Exception as e:
            print(f"Error during 2D training: {e}")
            return False
        return True
    
    def launch_3d_training(self):
        """Launch 3D Connect 4 training"""
        try:
            # For now, just demonstrate the 3D game
            from Game3D import Game3D
            import config3d
            
            print("Starting 3D Connect 4 demo...")
            print("Note: Full training implementation is still in development.")
            
            # Create a simple demo game
            game = Game3D()
            print("\n3D Connect 4 initialized!")
            game.display()
            
            # Show some basic info
            print(f"Board size: {config3d.SIZE}x{config3d.SIZE}x{config3d.SIZE}")
            print(f"Possible moves: {len(game.allowed_moves())}")
            print(f"Winning lines: {len(game._winning_lines)}")
            
        except ImportError as e:
            print(f"Error importing 3D modules: {e}")
            return False
        except Exception as e:
            print(f"Error during 3D demo: {e}")
            return False
        return True
    
    def launch_game_demo(self, mode):
        """Launch a simple demo for the selected game mode"""
        if mode == '2d':
            return self.demo_2d_game()
        elif mode == '3d':
            return self.demo_3d_game()
    
    def demo_2d_game(self):
        """Demo 2D Connect 4"""
        try:
            from Game_bitboard import Game
            
            print("\n=== 2D Connect 4 Demo ===")
            game = Game()
            game.display_it()
            
            print(f"Board size: 6x7")
            print(f"Allowed moves: {len(game.allowed_moves())}")
            
        except ImportError as e:
            print(f"Error importing 2D game: {e}")
            return False
        except Exception as e:
            print(f"Error in 2D demo: {e}")
            return False
        return True
    
    def demo_3d_game(self):
        """Demo 3D Connect 4"""
        try:
            from Game3D import Game3D
            
            print("\n=== 3D Connect 4 Demo ===")
            game = Game3D()
            game.display()
            
            # Make a few sample moves
            print("\nMaking sample moves...")
            game = game.make_move(1, 1)  # Center column
            game = game.make_move(2, 2)  # Another move
            game.display()
            
            print(f"Allowed moves: {len(game.allowed_moves())}")
            print(f"Total winning lines: {len(game._winning_lines)}")
            
        except ImportError as e:
            print(f"Error importing 3D game: {e}")
            return False
        except Exception as e:
            print(f"Error in 3D demo: {e}")
            return False
        return True
    
    def play_3d_human_vs_ai(self):
        """Launch 3D Human vs AI game"""
        try:
            print("\n3D Human vs AI Options:")
            print("1. Simple text interface")
            print("2. GUI interface") 
            choice = input("Choose interface (1/2): ").strip()
            
            if choice == "2":
                print("Launching 3D GUI...")
                import subprocess
                subprocess.run(["python", "human_vs_ai_3d_gui.py"])
            else:
                print("Launching 3D simple interface...")
                import subprocess
                subprocess.run(["python", "human_vs_ai_3d_simple.py"])
                
        except Exception as e:
            print(f"Error launching 3D Human vs AI: {e}")
            return False
        return True
    
    def play_3d_ai_battle(self):
        """Launch 3D AI vs AI battle"""
        try:
            print("Launching 3D AI vs AI battle...")
            import subprocess
            subprocess.run(["python", "ai_battle_3d_auto.py"])
        except Exception as e:
            print(f"Error launching 3D AI battle: {e}")
            return False
        return True
    
    def run(self):
        """Main run loop"""
        print("Welcome to the Connect 4 Game Suite!")
        print()
        
        while True:
            self.display_menu()
            choice = self.get_user_choice()
            
            if choice is None:
                print("Goodbye!")
                break
            
            if self.set_game_mode(choice):
                # Ask what to do with selected game
                if choice == '3d':
                    print("What would you like to do?")
                    print("  1: Run demo")
                    print("  2: Human vs AI")
                    print("  3: AI vs AI battle")
                    print("  4: Start training (coming soon)")
                    print("  5: Back to menu")
                    
                    action = input("Choose action (1/2/3/4/5): ").strip()
                    
                    if action == '1':
                        self.launch_game_demo(choice)
                    elif action == '2':
                        self.play_3d_human_vs_ai()
                    elif action == '3':
                        self.play_3d_ai_battle()
                    elif action == '4':
                        print("3D training not yet implemented. Coming soon!")
                    elif action == '5':
                        continue
                    else:
                        print("Invalid choice.")
                else:
                    # 2D game options
                    print("What would you like to do?")
                    print("  1: Run demo")
                    print("  2: Start training")
                    print("  3: Back to menu")
                    
                    action = input("Choose action (1/2/3): ").strip()
                    
                    if action == '1':
                        self.launch_game_demo(choice)
                    elif action == '2':
                        self.launch_game_training(choice)
                    elif action == '3':
                        continue
                    else:
                        print("Invalid choice.")
                
                input("\nPress Enter to continue...")


def main():
    """Main entry point"""
    selector = GameSelector()
    selector.run()


if __name__ == "__main__":
    main()