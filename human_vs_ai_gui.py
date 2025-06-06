#!/usr/bin/env python
"""
Human vs AI Connect 4 with Tkinter GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
import queue

from MCTS_NN import MCTS_NN
from Game_bitboard import Game
from ResNet import resnet18
import torch
import numpy as np

class HumanVsAIGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Human vs Alpha Zero Connect 4")
        self.root.geometry("900x800")
        self.root.configure(bg='#1a1a1a')
        
        # Game state
        self.game = None
        self.model = None
        self.turn = 0
        self.moves_history = []
        self.human_color = None
        self.ai_simulations = 200
        self.is_human_turn = False
        self.game_active = False
        self.ai_thread = None
        self.message_queue = queue.Queue()
        
        # Colors
        self.colors = {
            'bg': '#1a1a1a',
            'board': '#0066cc',
            'empty': '#ffffff',
            'yellow': '#ffcc00',
            'red': '#cc0000',
            'text': '#ffffff',
            'button': '#4CAF50',
            'human': '#00ff00',
            'ai': '#ff6600'
        }
        
        self.setup_ui()
        self.load_model()
        
    def setup_ui(self):
        """Set up the user interface"""
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="Human vs Alpha Zero Connect 4", 
                              font=('Arial', 24, 'bold'), 
                              fg=self.colors['text'], bg=self.colors['bg'])
        title_label.pack(pady=(0, 10))
        
        # Game info frame
        info_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        info_frame.pack(fill='x', pady=5)
        
        # Turn indicator
        self.turn_label = tk.Label(info_frame, text="Click 'New Game' to start", 
                                 font=('Arial', 16, 'bold'),
                                 fg=self.colors['text'], bg=self.colors['bg'])
        self.turn_label.pack()
        
        # Evaluation display
        eval_frame = tk.Frame(info_frame, bg=self.colors['bg'])
        eval_frame.pack(pady=5)
        
        tk.Label(eval_frame, text="Position Evaluation:", font=('Arial', 12),
                fg=self.colors['text'], bg=self.colors['bg']).pack(side='left')
        
        self.eval_canvas = tk.Canvas(eval_frame, width=200, height=25, bg='white')
        self.eval_canvas.pack(side='left', padx=10)
        
        self.eval_label = tk.Label(eval_frame, text="0.000", font=('Arial', 12),
                                 fg=self.colors['text'], bg=self.colors['bg'])
        self.eval_label.pack(side='left')
        
        # Board frame
        board_frame = tk.Frame(main_frame, bg=self.colors['board'], relief='raised', bd=3)
        board_frame.pack(pady=10)
        
        # Column buttons for moves
        self.col_buttons = []
        col_button_frame = tk.Frame(board_frame, bg=self.colors['board'])
        col_button_frame.grid(row=0, column=0, columnspan=7, pady=5)
        
        for col in range(7):
            btn = tk.Button(col_button_frame, text=f"↓ {col}", width=8, height=1,
                           command=lambda c=col: self.make_human_move(c),
                           bg=self.colors['button'], fg='white',
                           font=('Arial', 10, 'bold'), state='disabled')
            btn.grid(row=0, column=col, padx=2)
            self.col_buttons.append(btn)
        
        # Board grid
        self.board_buttons = []
        for row in range(6):
            button_row = []
            for col in range(7):
                btn = tk.Button(board_frame, width=6, height=3,
                               bg=self.colors['empty'], relief='raised', bd=2,
                               font=('Arial', 16, 'bold'), state='disabled')
                btn.grid(row=row+1, column=col, padx=2, pady=2)
                button_row.append(btn)
            self.board_buttons.append(button_row)
        
        # AI Analysis frame
        analysis_frame = tk.LabelFrame(main_frame, text="AI Analysis", 
                                     font=('Arial', 14, 'bold'),
                                     fg=self.colors['text'], bg=self.colors['bg'])
        analysis_frame.pack(fill='x', pady=10)
        
        # Analysis table
        columns = ('Col', 'Visits', 'Win %', 'Policy %')
        self.analysis_tree = ttk.Treeview(analysis_frame, columns=columns, show='headings', height=5)
        
        for col in columns:
            self.analysis_tree.heading(col, text=col)
            self.analysis_tree.column(col, width=120, anchor='center')
        
        self.analysis_tree.pack(fill='x', padx=10, pady=10)
        
        # Status frame
        status_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        status_frame.pack(fill='x', pady=5)
        
        self.status_label = tk.Label(status_frame, text="Ready to play", 
                                   font=('Arial', 12),
                                   fg=self.colors['text'], bg=self.colors['bg'])
        self.status_label.pack()
        
        # Control buttons
        button_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        button_frame.pack(pady=10)
        
        self.new_game_button = tk.Button(button_frame, text="New Game", 
                                       command=self.start_new_game,
                                       bg=self.colors['button'], fg='white',
                                       font=('Arial', 14, 'bold'),
                                       padx=20, pady=5)
        self.new_game_button.pack(side='left', padx=5)
        
        self.settings_button = tk.Button(button_frame, text="Settings", 
                                       command=self.show_settings,
                                       bg='#FF9800', fg='white',
                                       font=('Arial', 14, 'bold'),
                                       padx=20, pady=5)
        self.settings_button.pack(side='left', padx=5)
        
        self.quit_button = tk.Button(button_frame, text="Quit", 
                                   command=self.quit_game,
                                   bg='#f44336', fg='white',
                                   font=('Arial', 14, 'bold'),
                                   padx=20, pady=5)
        self.quit_button.pack(side='left', padx=5)
        
        # Help text
        help_text = ("Click column buttons (↓ 0-6) to make your move.\n"
                    "AI will analyze the position and respond automatically.")
        help_label = tk.Label(main_frame, text=help_text, 
                            font=('Arial', 10), fg='#cccccc', bg=self.colors['bg'])
        help_label.pack(pady=5)
    
    def load_model(self):
        """Load the trained model"""
        try:
            self.status_label.config(text="Loading Alpha Zero neural network...")
            self.root.update()
            
            self.model = resnet18()
            self.model.load_state_dict(torch.load('./best_model_resnet.pth'))
            self.model.eval()
            
            self.status_label.config(text="Alpha Zero loaded successfully! Ready to play.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load AI model: {str(e)}")
            self.status_label.config(text="Failed to load AI model")
    
    def show_settings(self):
        """Show game settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Game Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg=self.colors['bg'])
        
        # Color choice
        color_frame = tk.LabelFrame(settings_window, text="Your Color", 
                                  font=('Arial', 12, 'bold'),
                                  fg=self.colors['text'], bg=self.colors['bg'])
        color_frame.pack(fill='x', padx=20, pady=10)
        
        self.color_var = tk.StringVar(value="Yellow")
        tk.Radiobutton(color_frame, text="🟡 Yellow (First)", variable=self.color_var, value="Yellow",
                      fg=self.colors['text'], bg=self.colors['bg'],
                      selectcolor=self.colors['bg']).pack(anchor='w')
        tk.Radiobutton(color_frame, text="🔴 Red (Second)", variable=self.color_var, value="Red",
                      fg=self.colors['text'], bg=self.colors['bg'],
                      selectcolor=self.colors['bg']).pack(anchor='w')
        
        # Difficulty choice
        diff_frame = tk.LabelFrame(settings_window, text="AI Difficulty", 
                                 font=('Arial', 12, 'bold'),
                                 fg=self.colors['text'], bg=self.colors['bg'])
        diff_frame.pack(fill='x', padx=20, pady=10)
        
        self.diff_var = tk.StringVar(value="Normal")
        difficulties = [
            ("😊 Easy (50 simulations)", "Easy"),
            ("🤔 Normal (200 simulations)", "Normal"),
            ("😰 Hard (500 simulations)", "Hard"),
            ("💀 Nightmare (1000 simulations)", "Nightmare")
        ]
        
        for text, value in difficulties:
            tk.Radiobutton(diff_frame, text=text, variable=self.diff_var, value=value,
                          fg=self.colors['text'], bg=self.colors['bg'],
                          selectcolor=self.colors['bg']).pack(anchor='w')
        
        # Buttons
        btn_frame = tk.Frame(settings_window, bg=self.colors['bg'])
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Apply", command=lambda: self.apply_settings(settings_window),
                 bg=self.colors['button'], fg='white', font=('Arial', 12, 'bold')).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Cancel", command=settings_window.destroy,
                 bg='#f44336', fg='white', font=('Arial', 12, 'bold')).pack(side='left', padx=5)
    
    def apply_settings(self, window):
        """Apply game settings"""
        self.human_color = self.color_var.get()
        
        diff_map = {"Easy": 50, "Normal": 200, "Hard": 500, "Nightmare": 1000}
        self.ai_simulations = diff_map[self.diff_var.get()]
        
        self.status_label.config(text=f"Settings applied: {self.human_color}, {self.diff_var.get()} AI")
        window.destroy()
    
    def start_new_game(self):
        """Start a new game"""
        if not self.model:
            messagebox.showerror("Error", "AI model not loaded!")
            return
        
        # Reset game state
        self.game = Game()
        self.turn = 0
        self.moves_history = []
        self.game_active = True
        
        # Set default settings if not set
        if not hasattr(self, 'human_color'):
            self.human_color = "Yellow"
        if not hasattr(self, 'ai_simulations'):
            self.ai_simulations = 200
        
        # Determine first player
        self.is_human_turn = (self.human_color == "Yellow")
        
        # Update UI
        self.update_board_display()
        self.update_turn_display()
        self.update_evaluation(0.0)
        self.clear_analysis()
        
        # Enable/disable controls
        if self.is_human_turn:
            self.enable_human_moves()
            self.status_label.config(text="Your turn! Click a column to make your move.")
        else:
            self.disable_human_moves()
            self.status_label.config(text="AI is thinking...")
            self.start_ai_move()
    
    def update_board_display(self, last_col=None):
        """Update the board display"""
        yellow_list = self.game.binarystatetoflatlist(self.game.state[0])
        red_list = self.game.binarystatetoflatlist(self.game.state[1])
        
        for row in range(6):
            for col in range(7):
                idx = row * 7 + col
                btn = self.board_buttons[row][col]
                
                if yellow_list[idx] == 1:
                    btn.config(text="●", bg=self.colors['yellow'], fg='black')
                elif red_list[idx] == 1:
                    btn.config(text="●", bg=self.colors['red'], fg='white')
                else:
                    btn.config(text="", bg=self.colors['empty'])
                
                # Highlight last move
                if last_col is not None and col == last_col:
                    btn.config(relief='sunken', bd=4)
                else:
                    btn.config(relief='raised', bd=2)
    
    def update_turn_display(self):
        """Update turn display"""
        if not self.game_active:
            return
            
        player = "You" if self.is_human_turn else "AI"
        color = self.human_color if self.is_human_turn else ("Red" if self.human_color == "Yellow" else "Yellow")
        
        self.turn_label.config(text=f"Turn {self.turn + 1} - {player} ({color})")
    
    def update_evaluation(self, eval_value):
        """Update evaluation display"""
        # Clear canvas
        self.eval_canvas.delete("all")
        
        # Draw evaluation bar
        width = 200
        height = 25
        
        # Normalize evaluation (-1 to 1) to (0 to 1)
        normalized = (eval_value + 1) / 2
        
        # Adjust based on human color
        if self.human_color == "Red":
            normalized = 1 - normalized
        
        human_width = normalized * width
        ai_width = width - human_width
        
        # Draw human portion
        if human_width > 0:
            self.eval_canvas.create_rectangle(0, 0, human_width, height, 
                                            fill=self.colors['human'], outline="")
        
        # Draw AI portion
        if ai_width > 0:
            self.eval_canvas.create_rectangle(human_width, 0, width, height, 
                                            fill=self.colors['ai'], outline="")
        
        # Draw center line
        center = width / 2
        self.eval_canvas.create_line(center, 0, center, height, fill='black', width=2)
        
        # Update label
        display_eval = eval_value if self.human_color == "Yellow" else -eval_value
        self.eval_label.config(text=f"{display_eval:+.3f}")
    
    def enable_human_moves(self):
        """Enable column buttons for human moves"""
        allowed_moves = self.game.allowed_moves()
        available_cols = [self.game.convert_move_to_col_index(move) for move in allowed_moves]
        
        for i, btn in enumerate(self.col_buttons):
            if i in available_cols:
                btn.config(state='normal', bg=self.colors['button'])
            else:
                btn.config(state='disabled', bg='#666666')
    
    def disable_human_moves(self):
        """Disable column buttons"""
        for btn in self.col_buttons:
            btn.config(state='disabled', bg='#666666')
    
    def make_human_move(self, col):
        """Handle human move"""
        if not self.game_active or not self.is_human_turn:
            return
        
        # Check if move is valid
        allowed_moves = self.game.allowed_moves()
        available_cols = [self.game.convert_move_to_col_index(move) for move in allowed_moves]
        
        if col not in available_cols:
            return
        
        # Find the actual move
        move = None
        for m in allowed_moves:
            if self.game.convert_move_to_col_index(m) == col:
                move = m
                break
        
        if move is None:
            return
        
        # Make the move
        self.game.takestep(move)
        self.moves_history.append(col)
        self.turn += 1
        
        # Update display
        self.update_board_display(col)
        self.update_evaluation_from_game()
        
        # Check for game over
        gameover, winner = self.game.gameover()
        if gameover:
            self.end_game(winner)
            return
        
        # Switch to AI turn
        self.is_human_turn = False
        self.disable_human_moves()
        self.update_turn_display()
        self.status_label.config(text="AI is thinking...")
        
        # Start AI move
        self.start_ai_move()
    
    def start_ai_move(self):
        """Start AI move in separate thread"""
        self.ai_thread = threading.Thread(target=self.ai_move_worker)
        self.ai_thread.daemon = True
        self.ai_thread.start()
        
        # Start checking for AI completion
        self.check_ai_completion()
    
    def ai_move_worker(self):
        """Worker thread for AI move calculation"""
        try:
            # Create MCTS tree
            tree = MCTS_NN(self.model, use_dirichlet=False)
            rootnode = tree.createNode(self.game.state)
            
            # Run simulations
            for _ in range(self.ai_simulations):
                tree.simulate(rootnode, cpuct=1)
            
            # Get analysis
            visits = []
            moves = []
            q_values = []
            
            for child in rootnode.children:
                visits.append(child.N)
                col = self.game.convert_move_to_col_index(child.move)
                moves.append(col)
                q_values.append(child.Q)
            
            # Choose best move
            best_idx = np.argmax(visits)
            best_move = rootnode.children[best_idx].move
            best_col = moves[best_idx]
            
            # Get policy for analysis
            flat_state = self.game.state_flattener(self.game.state)
            with torch.no_grad():
                _, policy = self.model.forward(flat_state)
            
            # Send result to main thread
            self.message_queue.put(('ai_move', {
                'move': best_move,
                'col': best_col,
                'moves': moves,
                'visits': visits,
                'q_values': q_values,
                'policy': policy.numpy()[0]
            }))
            
        except Exception as e:
            self.message_queue.put(('error', str(e)))
    
    def check_ai_completion(self):
        """Check if AI has completed its move"""
        try:
            while True:
                msg_type, data = self.message_queue.get_nowait()
                
                if msg_type == 'ai_move':
                    self.process_ai_move(data)
                    return
                elif msg_type == 'error':
                    messagebox.showerror("AI Error", f"AI calculation failed: {data}")
                    self.status_label.config(text="AI error occurred")
                    return
                    
        except queue.Empty:
            # Check again in 100ms
            self.root.after(100, self.check_ai_completion)
    
    def process_ai_move(self, data):
        """Process AI move result"""
        # Make the move
        self.game.takestep(data['move'])
        self.moves_history.append(data['col'])
        self.turn += 1
        
        # Update display
        self.update_board_display(data['col'])
        self.update_evaluation_from_game()
        self.update_move_analysis(data['moves'], data['visits'], data['q_values'], data['policy'])
        
        # Check for game over
        gameover, winner = self.game.gameover()
        if gameover:
            self.end_game(winner)
            return
        
        # Switch to human turn
        self.is_human_turn = True
        self.enable_human_moves()
        self.update_turn_display()
        self.status_label.config(text="Your turn! Click a column to make your move.")
    
    def update_evaluation_from_game(self):
        """Update evaluation from current game state"""
        flat_state = self.game.state_flattener(self.game.state)
        with torch.no_grad():
            value, _ = self.model.forward(flat_state)
        
        self.update_evaluation(value.item())
    
    def update_move_analysis(self, moves, visits, q_values, policy):
        """Update move analysis table"""
        # Clear existing items
        for item in self.analysis_tree.get_children():
            self.analysis_tree.delete(item)
        
        # Sort by visits
        sorted_indices = np.argsort(visits)[::-1]
        
        # Add top moves
        for i, idx in enumerate(sorted_indices[:5]):
            col = moves[idx]
            visit = visits[idx]
            win_pct = 50 * (1 - q_values[idx])
            policy_pct = policy[col] * 100
            
            tags = ('best',) if i == 0 else ()
            self.analysis_tree.insert('', 'end', 
                                    values=(col, visit, f"{win_pct:.1f}%", f"{policy_pct:.1f}%"),
                                    tags=tags)
        
        # Style the best move
        self.analysis_tree.tag_configure('best', background='lightblue')
    
    def clear_analysis(self):
        """Clear move analysis table"""
        for item in self.analysis_tree.get_children():
            self.analysis_tree.delete(item)
    
    def end_game(self, winner):
        """Handle game end"""
        self.game_active = False
        self.disable_human_moves()
        
        # Determine result message
        if winner == 0:
            result = "It's a draw! 🤝"
        elif (winner == 1 and self.human_color == "Yellow") or (winner == -1 and self.human_color == "Red"):
            result = "You win! 🎉 Congratulations!"
        else:
            result = "AI wins! 🤖 Better luck next time!"
        
        self.status_label.config(text=result)
        self.turn_label.config(text="Game Over")
        
        # Show game over dialog
        moves_str = " → ".join(map(str, self.moves_history))
        detail = f"Total moves: {len(self.moves_history)}\nSequence: {moves_str}"
        messagebox.showinfo("Game Over", f"{result}\n\n{detail}")
    
    def quit_game(self):
        """Quit the application"""
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.root.quit()

def main():
    """Main entry point"""
    root = tk.Tk()
    app = HumanVsAIGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Application closed by user")

if __name__ == '__main__':
    main()