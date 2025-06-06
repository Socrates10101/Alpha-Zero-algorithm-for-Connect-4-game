#!/usr/bin/env python
"""
AI vs AI battle with graphical user interface using Tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import queue

from MCTS_NN import MCTS_NN
from Game_bitboard import Game
from ResNet import resnet18
import torch
import numpy as np

class Connect4GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Alpha Zero Connect 4 - AI Battle")
        self.root.geometry("800x700")
        self.root.configure(bg='#1e1e1e')
        
        # Game state
        self.game = None
        self.model = None
        self.tree = None
        self.currentnode = None
        self.turn = 0
        self.moves_history = []
        self.is_running = False
        self.battle_thread = None
        self.message_queue = queue.Queue()
        
        # Colors
        self.colors = {
            'bg': '#1e1e1e',
            'board': '#0066cc',
            'empty': '#ffffff',
            'yellow': '#ffcc00',
            'red': '#cc0000',
            'text': '#ffffff',
            'button': '#4CAF50'
        }
        
        self.setup_ui()
        self.load_model()
        
    def setup_ui(self):
        """Set up the user interface"""
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="Alpha Zero Connect 4", 
                              font=('Arial', 24, 'bold'), 
                              fg=self.colors['text'], bg=self.colors['bg'])
        title_label.pack(pady=(0, 10))
        
        # Board frame
        board_frame = tk.Frame(main_frame, bg=self.colors['board'], relief='raised', bd=3)
        board_frame.pack(pady=10)
        
        # Create board grid
        self.board_buttons = []
        for row in range(6):
            button_row = []
            for col in range(7):
                btn = tk.Button(board_frame, width=6, height=3,
                               bg=self.colors['empty'], relief='raised', bd=2,
                               font=('Arial', 16, 'bold'))
                btn.grid(row=row, column=col, padx=2, pady=2)
                button_row.append(btn)
            self.board_buttons.append(button_row)
        
        # Column numbers
        col_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        col_frame.pack()
        for col in range(7):
            label = tk.Label(col_frame, text=str(col), 
                           font=('Arial', 12, 'bold'),
                           fg=self.colors['text'], bg=self.colors['bg'])
            label.grid(row=0, column=col, padx=20)
        
        # Status frame
        status_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        status_frame.pack(fill='x', pady=10)
        
        # Game status
        self.status_label = tk.Label(status_frame, text="Ready to start battle", 
                                   font=('Arial', 14, 'bold'),
                                   fg=self.colors['text'], bg=self.colors['bg'])
        self.status_label.pack()
        
        # Turn info
        self.turn_label = tk.Label(status_frame, text="Turn: 0", 
                                 font=('Arial', 12),
                                 fg=self.colors['text'], bg=self.colors['bg'])
        self.turn_label.pack()
        
        # Evaluation bar
        eval_frame = tk.Frame(status_frame, bg=self.colors['bg'])
        eval_frame.pack(pady=5)
        
        tk.Label(eval_frame, text="Evaluation:", font=('Arial', 10),
                fg=self.colors['text'], bg=self.colors['bg']).pack(side='left')
        
        self.eval_canvas = tk.Canvas(eval_frame, width=200, height=20, bg='white')
        self.eval_canvas.pack(side='left', padx=10)
        
        self.eval_label = tk.Label(eval_frame, text="0.000", font=('Arial', 10),
                                 fg=self.colors['text'], bg=self.colors['bg'])
        self.eval_label.pack(side='left')
        
        # Move analysis frame
        analysis_frame = tk.LabelFrame(main_frame, text="Move Analysis", 
                                     font=('Arial', 12, 'bold'),
                                     fg=self.colors['text'], bg=self.colors['bg'])
        analysis_frame.pack(fill='x', pady=10)
        
        # Analysis table
        columns = ('Col', 'Visits', 'Win %', 'Policy %')
        self.analysis_tree = ttk.Treeview(analysis_frame, columns=columns, show='headings', height=5)
        
        for col in columns:
            self.analysis_tree.heading(col, text=col)
            self.analysis_tree.column(col, width=100, anchor='center')
        
        self.analysis_tree.pack(fill='x', padx=10, pady=10)
        
        # Control buttons
        button_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        button_frame.pack(pady=10)
        
        self.start_button = tk.Button(button_frame, text="Start Battle", 
                                    command=self.start_battle,
                                    bg=self.colors['button'], fg='white',
                                    font=('Arial', 12, 'bold'),
                                    padx=20, pady=5)
        self.start_button.pack(side='left', padx=5)
        
        self.pause_button = tk.Button(button_frame, text="Pause", 
                                    command=self.pause_battle,
                                    bg='#FF9800', fg='white',
                                    font=('Arial', 12, 'bold'),
                                    padx=20, pady=5, state='disabled')
        self.pause_button.pack(side='left', padx=5)
        
        self.reset_button = tk.Button(button_frame, text="Reset", 
                                    command=self.reset_game,
                                    bg='#f44336', fg='white',
                                    font=('Arial', 12, 'bold'),
                                    padx=20, pady=5)
        self.reset_button.pack(side='left', padx=5)
        
        # Speed control
        speed_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        speed_frame.pack(pady=5)
        
        tk.Label(speed_frame, text="Speed:", font=('Arial', 10),
                fg=self.colors['text'], bg=self.colors['bg']).pack(side='left')
        
        self.speed_var = tk.StringVar(value="Normal")
        speed_combo = ttk.Combobox(speed_frame, textvariable=self.speed_var, 
                                 values=["Slow", "Normal", "Fast"], state="readonly")
        speed_combo.pack(side='left', padx=10)
        
    def load_model(self):
        """Load the trained model"""
        try:
            self.status_label.config(text="Loading neural network...")
            self.root.update()
            
            self.model = resnet18()
            self.model.load_state_dict(torch.load('./best_model_resnet.pth'))
            self.model.eval()
            
            self.status_label.config(text="Model loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model: {str(e)}")
            self.status_label.config(text="Failed to load model")
    
    def update_board_display(self, game, last_col=None):
        """Update the board display"""
        yellow_list = game.binarystatetoflatlist(game.state[0])
        red_list = game.binarystatetoflatlist(game.state[1])
        
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
                    btn.config(relief='sunken', bd=3)
                else:
                    btn.config(relief='raised', bd=2)
    
    def update_evaluation_bar(self, eval_value):
        """Update the evaluation bar"""
        # Clear canvas
        self.eval_canvas.delete("all")
        
        # Draw evaluation bar
        width = 200
        height = 20
        
        # Normalize evaluation (-1 to 1) to (0 to 1)
        normalized = (eval_value + 1) / 2
        yellow_width = normalized * width
        red_width = width - yellow_width
        
        # Draw yellow portion
        if yellow_width > 0:
            self.eval_canvas.create_rectangle(0, 0, yellow_width, height, 
                                            fill=self.colors['yellow'], outline="")
        
        # Draw red portion
        if red_width > 0:
            self.eval_canvas.create_rectangle(yellow_width, 0, width, height, 
                                            fill=self.colors['red'], outline="")
        
        # Draw center line
        center = width / 2
        self.eval_canvas.create_line(center, 0, center, height, fill='black', width=2)
        
        # Update label
        self.eval_label.config(text=f"{eval_value:+.3f}")
    
    def update_move_analysis(self, moves, visits, q_values, policy):
        """Update the move analysis table"""
        # Clear existing items
        for item in self.analysis_tree.get_children():
            self.analysis_tree.delete(item)
        
        # Sort by visits
        sorted_indices = np.argsort(visits)[::-1]
        
        # Add top 5 moves
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
        self.analysis_tree.tag_configure('best', background='lightgreen')
    
    def get_speed_delay(self):
        """Get delay based on speed setting"""
        speed_map = {"Slow": 3.0, "Normal": 1.5, "Fast": 0.5}
        return speed_map.get(self.speed_var.get(), 1.5)
    
    def battle_worker(self):
        """Worker thread for AI battle"""
        try:
            sim_number = 50
            
            while self.is_running and not self.currentnode.isterminal():
                self.turn += 1
                player = "Yellow" if self.game.player_turn == 1 else "Red"
                
                # Update status
                self.message_queue.put(('status', f"{player} is thinking..."))
                
                # Get initial evaluation
                flat_state = self.game.state_flattener(self.game.state)
                with torch.no_grad():
                    value, policy = self.model.forward(flat_state)
                
                eval_from_yellow = value.item() * self.game.player_turn * -1
                
                # Run MCTS
                start_time = time.time()
                for i in range(sim_number):
                    if not self.is_running:
                        return
                    self.tree.simulate(self.currentnode, cpuct=1)
                
                think_time = time.time() - start_time
                
                # Analyze moves
                visits = []
                moves = []
                q_values = []
                
                for child in self.currentnode.children:
                    visits.append(child.N)
                    col = self.game.convert_move_to_col_index(child.move)
                    moves.append(col)
                    q_values.append(child.Q)
                
                # Make best move
                best_idx = np.argmax(visits)
                best_col = moves[best_idx]
                
                # Update game state
                self.currentnode = self.currentnode.children[best_idx]
                self.game = Game(self.currentnode.state)
                self.moves_history.append(best_col)
                
                # Send updates to main thread
                self.message_queue.put(('board_update', (self.game, best_col)))
                self.message_queue.put(('eval_update', eval_from_yellow))
                self.message_queue.put(('analysis_update', (moves, visits, q_values, policy.numpy()[0])))
                self.message_queue.put(('turn_update', self.turn))
                self.message_queue.put(('status', f"{player} played column {best_col}"))
                
                # Reinitialize tree
                self.tree = MCTS_NN(self.model, use_dirichlet=False)
                rootnode = self.tree.createNode(self.game.state)
                self.currentnode = rootnode
                
                # Delay based on speed setting
                time.sleep(self.get_speed_delay())
            
            # Game over
            if self.is_running:
                _, winner = self.game.gameover()
                if winner == 0:
                    result = "It's a draw!"
                elif winner == 1:
                    result = "Yellow wins!"
                else:
                    result = "Red wins!"
                
                self.message_queue.put(('game_over', result))
                
        except Exception as e:
            self.message_queue.put(('error', str(e)))
    
    def process_messages(self):
        """Process messages from worker thread"""
        try:
            while True:
                msg_type, data = self.message_queue.get_nowait()
                
                if msg_type == 'status':
                    self.status_label.config(text=data)
                elif msg_type == 'board_update':
                    game, last_col = data
                    self.update_board_display(game, last_col)
                elif msg_type == 'eval_update':
                    self.update_evaluation_bar(data)
                elif msg_type == 'analysis_update':
                    moves, visits, q_values, policy = data
                    self.update_move_analysis(moves, visits, q_values, policy)
                elif msg_type == 'turn_update':
                    self.turn_label.config(text=f"Turn: {data}")
                elif msg_type == 'game_over':
                    self.status_label.config(text=data)
                    self.is_running = False
                    self.start_button.config(state='normal', text='Start Battle')
                    self.pause_button.config(state='disabled')
                    messagebox.showinfo("Game Over", data)
                elif msg_type == 'error':
                    messagebox.showerror("Error", f"Battle error: {data}")
                    self.is_running = False
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_messages)
    
    def start_battle(self):
        """Start the AI battle"""
        if not self.model:
            messagebox.showerror("Error", "Model not loaded!")
            return
        
        if not self.is_running:
            self.reset_game()
            self.is_running = True
            self.start_button.config(state='disabled')
            self.pause_button.config(state='normal')
            
            # Start worker thread
            self.battle_thread = threading.Thread(target=self.battle_worker)
            self.battle_thread.daemon = True
            self.battle_thread.start()
    
    def pause_battle(self):
        """Pause/resume the battle"""
        if self.is_running:
            self.is_running = False
            self.start_button.config(state='normal', text='Resume')
            self.pause_button.config(state='disabled')
            self.status_label.config(text="Battle paused")
        else:
            self.start_battle()
    
    def reset_game(self):
        """Reset the game"""
        self.is_running = False
        self.game = Game()
        self.tree = MCTS_NN(self.model, use_dirichlet=False) if self.model else None
        self.currentnode = self.tree.createNode(self.game.state) if self.tree else None
        self.turn = 0
        self.moves_history = []
        
        # Reset UI
        self.update_board_display(self.game)
        self.update_evaluation_bar(0.0)
        self.turn_label.config(text="Turn: 0")
        self.status_label.config(text="Ready to start battle")
        self.start_button.config(state='normal', text='Start Battle')
        self.pause_button.config(state='disabled')
        
        # Clear analysis table
        for item in self.analysis_tree.get_children():
            self.analysis_tree.delete(item)

def main():
    """Main entry point"""
    root = tk.Tk()
    app = Connect4GUI(root)
    
    # Start message processing
    app.process_messages()
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Application closed by user")

if __name__ == '__main__':
    main()