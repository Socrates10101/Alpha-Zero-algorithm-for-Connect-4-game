#!/usr/bin/env python
"""
Human vs AI 3D Connect 4 with Tkinter GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
import queue
import math

from Game3D import Game3D
from MCTS_NN3D import MCTS_NN3D
import torch
import numpy as np
import random

class HumanVsAI3DGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Human vs AI 3D Connect 4")
        self.root.geometry("1200x900")
        self.root.configure(bg='#1a1a1a')
        
        # Game state
        self.game = None
        self.ai_player = None
        self.turn = 0
        self.moves_history = []
        self.human_color = None
        self.ai_simulations = 50
        self.is_human_turn = False
        self.game_active = False
        self.ai_thread = None
        self.message_queue = queue.Queue()
        
        # 3D visualization settings
        self.layer_spacing = 150
        self.cell_size = 40
        self.board_offset_x = 50
        self.board_offset_y = 50
        
        # Colors
        self.colors = {
            'bg': '#1a1a1a',
            'board': '#2c2c2c',
            'grid': '#404040',
            'empty': '#666666',
            'yellow': '#ffcc00',
            'red': '#cc0000',
            'text': '#ffffff',
            'button': '#4CAF50',
            'human': '#00ff00',
            'ai': '#ff6600',
            'highlight': '#ffffff',
            'winning': '#00ffff'
        }
        
        self.setup_ui()
        self.create_dummy_ai()
        
    def setup_ui(self):
        """Set up the user interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="Human vs AI 3D Connect 4", 
                              font=('Arial', 24, 'bold'), 
                              fg=self.colors['text'], bg=self.colors['bg'])
        title_label.pack(pady=(0, 10))
        
        # Top info panel
        self.setup_info_panel(main_frame)
        
        # Game board area
        self.setup_board_area(main_frame)
        
        # Control panel
        self.setup_control_panel(main_frame)
        
        # Status area
        self.setup_status_area(main_frame)
        
    def setup_info_panel(self, parent):
        """Setup the information panel"""
        info_frame = tk.Frame(parent, bg=self.colors['bg'])
        info_frame.pack(fill='x', pady=5)
        
        # Game status
        self.status_label = tk.Label(info_frame, text="Click 'New Game' to start", 
                                   font=('Arial', 16, 'bold'),
                                   fg=self.colors['text'], bg=self.colors['bg'])
        self.status_label.pack()
        
        # Turn and evaluation info
        eval_frame = tk.Frame(info_frame, bg=self.colors['bg'])
        eval_frame.pack(pady=5)
        
        tk.Label(eval_frame, text="Turn:", font=('Arial', 12),
                fg=self.colors['text'], bg=self.colors['bg']).pack(side='left')
        
        self.turn_label = tk.Label(eval_frame, text="0", font=('Arial', 12, 'bold'),
                                 fg=self.colors['text'], bg=self.colors['bg'])
        self.turn_label.pack(side='left', padx=(5, 20))
        
        tk.Label(eval_frame, text="AI Evaluation:", font=('Arial', 12),
                fg=self.colors['text'], bg=self.colors['bg']).pack(side='left')
        
        self.eval_label = tk.Label(eval_frame, text="0.000", font=('Arial', 12, 'bold'),
                                 fg=self.colors['text'], bg=self.colors['bg'])
        self.eval_label.pack(side='left', padx=5)
    
    def setup_board_area(self, parent):
        """Setup the 3D board visualization area"""
        board_frame = tk.Frame(parent, bg=self.colors['board'], relief='raised', bd=2)
        board_frame.pack(pady=10, fill='both', expand=True)
        
        # Canvas for 3D board
        self.canvas = tk.Canvas(board_frame, bg=self.colors['board'], 
                               width=800, height=600)
        self.canvas.pack(side='left', padx=10, pady=10)
        
        # Bind mouse clicks
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_canvas_hover)
        
        # Layer selector
        layer_frame = tk.Frame(board_frame, bg=self.colors['bg'])
        layer_frame.pack(side='right', fill='y', padx=10, pady=10)
        
        tk.Label(layer_frame, text="3D Layers", font=('Arial', 14, 'bold'),
                fg=self.colors['text'], bg=self.colors['bg']).pack(pady=(0, 10))
        
        self.layer_buttons = []
        for z in range(4):
            btn = tk.Button(layer_frame, text=f"Layer {z}", width=12,
                           command=lambda layer=z: self.highlight_layer(layer),
                           bg=self.colors['button'], fg='white')
            btn.pack(pady=2)
            self.layer_buttons.append(btn)
        
        # Movement guide
        tk.Label(layer_frame, text="\nHow to play:", font=('Arial', 12, 'bold'),
                fg=self.colors['text'], bg=self.colors['bg']).pack(pady=(20, 5))
        
        guide_text = "Click on any column\n(x,y position) to\ndrop your piece.\n\nGoal: Get 4 pieces\nin any straight line\nthrough the 3D cube."
        tk.Label(layer_frame, text=guide_text, font=('Arial', 10),
                fg=self.colors['text'], bg=self.colors['bg'], justify='left').pack()
    
    def setup_control_panel(self, parent):
        """Setup control buttons"""
        control_frame = tk.Frame(parent, bg=self.colors['bg'])
        control_frame.pack(fill='x', pady=5)
        
        # Game controls
        tk.Button(control_frame, text="New Game", command=self.new_game,
                 bg=self.colors['button'], fg='white', font=('Arial', 12),
                 width=12).pack(side='left', padx=5)
        
        tk.Button(control_frame, text="Resign", command=self.resign_game,
                 bg='#cc4400', fg='white', font=('Arial', 12),
                 width=12).pack(side='left', padx=5)
        
        # Difficulty selector
        tk.Label(control_frame, text="AI Difficulty:", font=('Arial', 12),
                fg=self.colors['text'], bg=self.colors['bg']).pack(side='left', padx=(20, 5))
        
        self.difficulty_var = tk.StringVar(value="Normal")
        difficulty_combo = ttk.Combobox(control_frame, textvariable=self.difficulty_var,
                                      values=["Easy (25)", "Normal (50)", "Hard (100)"],
                                      state="readonly", width=12)
        difficulty_combo.pack(side='left', padx=5)
        difficulty_combo.bind("<<ComboboxSelected>>", self.on_difficulty_change)
        
        # Color selector
        tk.Label(control_frame, text="Your Color:", font=('Arial', 12),
                fg=self.colors['text'], bg=self.colors['bg']).pack(side='left', padx=(20, 5))
        
        self.color_var = tk.StringVar(value="Yellow (First)")
        color_combo = ttk.Combobox(control_frame, textvariable=self.color_var,
                                 values=["Yellow (First)", "Red (Second)"],
                                 state="readonly", width=15)
        color_combo.pack(side='left', padx=5)
    
    def setup_status_area(self, parent):
        """Setup status and move history area"""
        status_frame = tk.Frame(parent, bg=self.colors['bg'])
        status_frame.pack(fill='x', pady=5)
        
        # Move history
        history_frame = tk.Frame(status_frame, bg=self.colors['bg'])
        history_frame.pack(side='left', fill='both', expand=True)
        
        tk.Label(history_frame, text="Move History:", font=('Arial', 12, 'bold'),
                fg=self.colors['text'], bg=self.colors['bg']).pack(anchor='w')
        
        self.history_text = tk.Text(history_frame, height=6, width=50,
                                   bg='#2c2c2c', fg=self.colors['text'],
                                   font=('Courier', 10))
        self.history_text.pack(fill='both', expand=True)
        
        # AI analysis
        analysis_frame = tk.Frame(status_frame, bg=self.colors['bg'])
        analysis_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        tk.Label(analysis_frame, text="AI Analysis:", font=('Arial', 12, 'bold'),
                fg=self.colors['text'], bg=self.colors['bg']).pack(anchor='w')
        
        self.analysis_text = tk.Text(analysis_frame, height=6, width=40,
                                    bg='#2c2c2c', fg=self.colors['text'],
                                    font=('Courier', 10))
        self.analysis_text.pack(fill='both', expand=True)
    
    def create_dummy_ai(self):
        """Create dummy AI player"""
        def dummy_ai(state_vector):
            value = torch.tensor([[random.uniform(-0.3, 0.3)]])
            policy = torch.ones((1, 16)) / 16
            # Add some randomness
            policy = policy + torch.rand_like(policy) * 0.2
            policy = policy / policy.sum()
            return value, policy
        
        self.ai_player = dummy_ai
    
    def draw_3d_board(self):
        """Draw the 3D board on canvas"""
        self.canvas.delete("all")
        
        if not self.game:
            # Draw empty board template
            self.draw_empty_board()
            return
        
        # Draw each layer
        for z in range(4):
            self.draw_layer(z)
        
        # Draw layer labels
        for z in range(4):
            x = self.board_offset_x + z * self.layer_spacing + 60
            y = self.board_offset_y - 20
            self.canvas.create_text(x, y, text=f"Layer {z}", 
                                  fill=self.colors['text'], font=('Arial', 12, 'bold'))
    
    def draw_empty_board(self):
        """Draw empty board template"""
        for z in range(4):
            for x in range(4):
                for y in range(4):
                    self.draw_cell(x, y, z, 0)
    
    def draw_layer(self, z):
        """Draw a single layer of the 3D board"""
        for x in range(4):
            for y in range(4):
                piece = self.game.board[x, y, z]
                self.draw_cell(x, y, z, piece)
    
    def draw_cell(self, x, y, z, piece):
        """Draw a single cell"""
        # Calculate position on canvas
        canvas_x = self.board_offset_x + z * self.layer_spacing + x * self.cell_size
        canvas_y = self.board_offset_y + y * self.cell_size
        
        # Draw cell background
        cell_id = self.canvas.create_rectangle(
            canvas_x, canvas_y, 
            canvas_x + self.cell_size, canvas_y + self.cell_size,
            fill=self.colors['empty'], outline=self.colors['grid'], width=2
        )
        
        # Store cell info
        self.canvas.addtag_withtag(f"cell_{x}_{y}_{z}", cell_id)
        
        # Draw piece if present
        if piece != 0:
            color = self.colors['yellow'] if piece == 1 else self.colors['red']
            symbol = 'O' if piece == 1 else 'X'
            
            # Highlight last move
            if (self.moves_history and len(self.moves_history) > 0 and 
                self.moves_history[-1] == (x, y) and 
                z == self.game._get_drop_height(x, y) - 1):
                outline_color = self.colors['highlight']
                width = 4
            else:
                outline_color = color
                width = 2
            
            piece_id = self.canvas.create_oval(
                canvas_x + 5, canvas_y + 5,
                canvas_x + self.cell_size - 5, canvas_y + self.cell_size - 5,
                fill=color, outline=outline_color, width=width
            )
            
            # Add text symbol
            text_id = self.canvas.create_text(
                canvas_x + self.cell_size//2, canvas_y + self.cell_size//2,
                text=symbol, fill='white', font=('Arial', 16, 'bold')
            )
        
        # Add column coordinates text
        if z == 0 and piece == 0:  # Only on bottom layer of empty cells
            coord_text = f"{x},{y}"
            self.canvas.create_text(
                canvas_x + self.cell_size//2, canvas_y + self.cell_size//2,
                text=coord_text, fill=self.colors['text'], font=('Arial', 8)
            )
    
    def on_canvas_click(self, event):
        """Handle canvas click for move input"""
        if not self.game_active or not self.is_human_turn:
            return
        
        # Find which cell was clicked
        x, y = self.pixel_to_board_coords(event.x, event.y)
        
        if x is not None and y is not None:
            move = (x, y)
            if move in self.game.allowed_moves():
                self.make_human_move(move)
            else:
                self.update_status("Invalid move! Column is full.")
    
    def on_canvas_hover(self, event):
        """Handle mouse hover for highlighting"""
        if not self.game_active:
            return
        
        # Could add hover highlighting here
        pass
    
    def pixel_to_board_coords(self, px, py):
        """Convert pixel coordinates to board coordinates"""
        for z in range(4):
            for x in range(4):
                for y in range(4):
                    canvas_x = self.board_offset_x + z * self.layer_spacing + x * self.cell_size
                    canvas_y = self.board_offset_y + y * self.cell_size
                    
                    if (canvas_x <= px <= canvas_x + self.cell_size and 
                        canvas_y <= py <= canvas_y + self.cell_size):
                        return x, y
        
        return None, None
    
    def highlight_layer(self, layer):
        """Highlight a specific layer"""
        # Reset all layer button colors
        for btn in self.layer_buttons:
            btn.configure(bg=self.colors['button'])
        
        # Highlight selected layer button
        self.layer_buttons[layer].configure(bg=self.colors['highlight'])
        
        # Could add visual highlighting to the board here
        # For now, just flash the layer
        self.flash_layer(layer)
    
    def flash_layer(self, layer):
        """Flash a layer to show it clearly"""
        # This could be enhanced to actually highlight the layer visually
        pass
    
    def new_game(self):
        """Start a new game"""
        # Get settings
        color_choice = self.color_var.get()
        self.human_color = 1 if "Yellow" in color_choice else -1
        
        difficulty = self.difficulty_var.get()
        if "Easy" in difficulty:
            self.ai_simulations = 25
        elif "Hard" in difficulty:
            self.ai_simulations = 100
        else:
            self.ai_simulations = 50
        
        # Initialize game
        self.game = Game3D()
        self.turn = 0
        self.moves_history = []
        self.game_active = True
        self.is_human_turn = (self.human_color == 1)  # Yellow goes first
        
        # Update UI
        self.update_status(f"New game started! You are {'Yellow (O)' if self.human_color == 1 else 'Red (X)'}")
        self.turn_label.configure(text=str(self.turn))
        self.history_text.delete(1.0, tk.END)
        self.analysis_text.delete(1.0, tk.END)
        
        self.draw_3d_board()
        
        # If AI goes first
        if not self.is_human_turn:
            self.root.after(1000, self.make_ai_move)
    
    def make_human_move(self, move):
        """Make a human move"""
        if not self.game_active or not self.is_human_turn:
            return
        
        # Make move
        new_game = self.game.make_move(move[0], move[1])
        if new_game is None:
            self.update_status("Invalid move!")
            return
        
        self.game = new_game
        self.turn += 1
        self.moves_history.append(move)
        
        # Update UI
        self.turn_label.configure(text=str(self.turn))
        self.add_move_to_history(f"Turn {self.turn}: Human plays {move}")
        self.draw_3d_board()
        
        # Check game over
        if self.game.is_game_over():
            self.end_game()
            return
        
        # Switch to AI turn
        self.is_human_turn = False
        self.update_status("AI is thinking...")
        self.root.after(500, self.make_ai_move)
    
    def make_ai_move(self):
        """Make an AI move"""
        if not self.game_active or self.is_human_turn:
            return
        
        # Run AI in separate thread to avoid blocking UI
        self.ai_thread = threading.Thread(target=self.ai_move_thread)
        self.ai_thread.start()
        
        # Check for AI response
        self.root.after(100, self.check_ai_response)
    
    def ai_move_thread(self):
        """AI move calculation in separate thread"""
        try:
            mcts = MCTS_NN3D(self.ai_player, use_dirichlet=False)
            root = mcts.run_simulations(self.game, self.ai_simulations, cpuct=1.0)
            
            if root.children:
                visits = [child.N for child in root.children]
                best_idx = np.argmax(visits)
                best_move = root.children[best_idx].move
                
                # Prepare analysis
                analysis = f"AI Analysis (Turn {self.turn + 1}):\n"
                sorted_children = sorted(root.children, key=lambda x: x.N, reverse=True)
                for i, child in enumerate(sorted_children[:3]):
                    visits = child.N
                    win_rate = 50 * (1 - child.Q) if child.Q != 0 else 50
                    analysis += f"  {child.move}: {visits} visits, {win_rate:.1f}%\n"
                
                self.message_queue.put(('move', best_move, analysis))
            else:
                # Fallback to random
                allowed = self.game.allowed_moves()
                if allowed:
                    move = random.choice(allowed)
                    self.message_queue.put(('move', move, "Random fallback move"))
                else:
                    self.message_queue.put(('error', None, None))
                    
        except Exception as e:
            self.message_queue.put(('error', str(e), None))
    
    def check_ai_response(self):
        """Check if AI has responded"""
        try:
            msg_type, move, analysis = self.message_queue.get_nowait()
            
            if msg_type == 'move':
                # Make the AI move
                new_game = self.game.make_move(move[0], move[1])
                if new_game:
                    self.game = new_game
                    self.turn += 1
                    self.moves_history.append(move)
                    
                    # Update UI
                    self.turn_label.configure(text=str(self.turn))
                    self.add_move_to_history(f"Turn {self.turn}: AI plays {move}")
                    if analysis:
                        self.add_analysis(analysis)
                    self.draw_3d_board()
                    
                    # Check game over
                    if self.game.is_game_over():
                        self.end_game()
                        return
                    
                    # Switch to human turn
                    self.is_human_turn = True
                    self.update_status("Your turn! Click on a column to play.")
                else:
                    self.update_status("AI move error!")
            
            elif msg_type == 'error':
                self.update_status(f"AI error: {move}")
                
        except queue.Empty:
            # AI still thinking
            self.root.after(100, self.check_ai_response)
    
    def end_game(self):
        """Handle game end"""
        self.game_active = False
        winner = self.game.get_winner()
        
        if winner == 0:
            result = "It's a draw!"
        elif winner == self.human_color:
            result = "You win! Congratulations! 🎉"
        else:
            result = "AI wins! Better luck next time! 🤖"
        
        self.update_status(f"Game Over: {result}")
        messagebox.showinfo("Game Over", result)
    
    def resign_game(self):
        """Resign current game"""
        if self.game_active:
            if messagebox.askyesno("Resign", "Are you sure you want to resign?"):
                self.game_active = False
                self.update_status("Game resigned.")
    
    def on_difficulty_change(self, event):
        """Handle difficulty change"""
        difficulty = self.difficulty_var.get()
        if "Easy" in difficulty:
            self.ai_simulations = 25
        elif "Hard" in difficulty:
            self.ai_simulations = 100
        else:
            self.ai_simulations = 50
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.configure(text=message)
    
    def add_move_to_history(self, move_text):
        """Add move to history display"""
        self.history_text.insert(tk.END, move_text + "\n")
        self.history_text.see(tk.END)
    
    def add_analysis(self, analysis_text):
        """Add AI analysis to display"""
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(1.0, analysis_text)

def main():
    """Main function"""
    root = tk.Tk()
    app = HumanVsAI3DGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("GUI interrupted")

if __name__ == "__main__":
    main()