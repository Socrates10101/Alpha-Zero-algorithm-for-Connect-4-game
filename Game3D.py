#  ================ AlphaZero algorithm for 3D Connect 4 game =================== #
# Name:             Game3D.py
# Description:      3D Connect 4 game environment (4x4x4 board)
# Authors:          AI Assistant
# Date:             2025
# License:          BSD 3-Clause License
# ============================================================================ #

import numpy as np
import itertools

class Game3D:
    """
    3D Connect 4 game class for a 4x4x4 board.
    Players drop pieces in columns (x,y) and pieces fall to lowest available z position.
    Win condition: 4 pieces in a line (76 possible winning lines total).
    """
    
    def __init__(self, state=None):
        self.SIZE = 4  # 4x4x4 board
        
        if state is None:
            # Initialize empty board
            self.board = np.zeros((self.SIZE, self.SIZE, self.SIZE), dtype=int)
            self.player_turn = 1  # Player 1 starts (yellow)
        else:
            self.board = state['board'].copy()
            self.player_turn = state['player_turn']
        
        # Pre-compute all winning lines for efficiency
        self._winning_lines = self._compute_winning_lines()
    
    def _compute_winning_lines(self):
        """
        Pre-compute all 76 possible winning lines in 3D Connect 4.
        Returns list of lines, where each line is a list of 4 (x,y,z) coordinates.
        """
        lines = []
        
        # 1. Lines within each layer (40 total: 10 per layer × 4 layers)
        for z in range(self.SIZE):
            # Horizontal lines (4 per layer)
            for y in range(self.SIZE):
                lines.append([(x, y, z) for x in range(self.SIZE)])
            
            # Vertical lines (4 per layer)
            for x in range(self.SIZE):
                lines.append([(x, y, z) for y in range(self.SIZE)])
            
            # Diagonal lines (2 per layer)
            lines.append([(i, i, z) for i in range(self.SIZE)])  # Main diagonal
            lines.append([(i, self.SIZE-1-i, z) for i in range(self.SIZE)])  # Anti-diagonal
        
        # 2. Vertical lines through z-axis (16 total)
        for x in range(self.SIZE):
            for y in range(self.SIZE):
                lines.append([(x, y, z) for z in range(self.SIZE)])
        
        # 3. Diagonal lines between layers
        # Along x-z planes (8 total: 2 diagonals × 4 y-positions)
        for y in range(self.SIZE):
            lines.append([(i, y, i) for i in range(self.SIZE)])  # x=z diagonal
            lines.append([(i, y, self.SIZE-1-i) for i in range(self.SIZE)])  # x=-z diagonal
        
        # Along y-z planes (8 total: 2 diagonals × 4 x-positions)
        for x in range(self.SIZE):
            lines.append([(x, i, i) for i in range(self.SIZE)])  # y=z diagonal
            lines.append([(x, i, self.SIZE-1-i) for i in range(self.SIZE)])  # y=-z diagonal
        
        # 4. Space diagonals (4 total: corner to opposite corner)
        lines.append([(i, i, i) for i in range(self.SIZE)])  # (0,0,0) to (3,3,3)
        lines.append([(i, i, self.SIZE-1-i) for i in range(self.SIZE)])  # (0,0,3) to (3,3,0)
        lines.append([(i, self.SIZE-1-i, i) for i in range(self.SIZE)])  # (0,3,0) to (3,0,3)
        lines.append([(i, self.SIZE-1-i, self.SIZE-1-i) for i in range(self.SIZE)])  # (0,3,3) to (3,0,0)
        
        return lines
    
    def allowed_moves(self):
        """
        Returns list of allowed moves as (x, y) tuples.
        A move is allowed if the column is not full (z < SIZE).
        """
        moves = []
        for x in range(self.SIZE):
            for y in range(self.SIZE):
                if self._get_drop_height(x, y) < self.SIZE:
                    moves.append((x, y))
        return moves
    
    def _get_drop_height(self, x, y):
        """
        Get the z-level where a piece would land in column (x, y).
        Returns SIZE if column is full.
        """
        for z in range(self.SIZE):
            if self.board[x, y, z] == 0:
                return z
        return self.SIZE  # Column is full
    
    def is_valid_move(self, x, y):
        """Check if move (x, y) is valid."""
        return 0 <= x < self.SIZE and 0 <= y < self.SIZE and self._get_drop_height(x, y) < self.SIZE
    
    def make_move(self, x, y):
        """
        Make a move at column (x, y).
        Returns new game state or None if move is invalid.
        """
        if not self.is_valid_move(x, y):
            return None
        
        z = self._get_drop_height(x, y)
        new_board = self.board.copy()
        new_board[x, y, z] = self.player_turn
        
        return Game3D({
            'board': new_board,
            'player_turn': -self.player_turn
        })
    
    def check_win(self, player=None):
        """
        Check if specified player has won.
        If player is None, check current player.
        Returns True if player has 4 in a line.
        """
        if player is None:
            player = self.player_turn
        
        for line in self._winning_lines:
            if all(self.board[x, y, z] == player for x, y, z in line):
                return True
        return False
    
    def is_draw(self):
        """Check if game is a draw (board full, no winner)."""
        return len(self.allowed_moves()) == 0 and not self.check_win(1) and not self.check_win(-1)
    
    def is_game_over(self):
        """Check if game is over (win or draw)."""
        return self.check_win(1) or self.check_win(-1) or self.is_draw()
    
    def get_winner(self):
        """
        Get winner of the game.
        Returns 1 if player 1 wins, -1 if player 2 wins, 0 if draw, None if game not over.
        """
        if self.check_win(1):
            return 1
        elif self.check_win(-1):
            return -1
        elif self.is_draw():
            return 0
        return None
    
    def get_state_vector(self):
        """
        Convert board state to flat vector for neural network input.
        Returns vector of length 64*3 = 192 (player1 board + player2 board + current player).
        """
        player1_board = (self.board == 1).astype(int)
        player2_board = (self.board == -1).astype(int)
        current_player = np.full(64, self.player_turn)
        
        return np.concatenate([
            player1_board.flatten(),
            player2_board.flatten(), 
            current_player
        ])
    
    def display(self):
        """Display the 3D board layer by layer."""
        print("3D Connect 4 Board (4x4x4)")
        print("Player turn:", "Yellow (1)" if self.player_turn == 1 else "Red (-1)")
        print()
        
        for z in range(self.SIZE-1, -1, -1):  # Top to bottom
            print(f"Layer {z} (height):")
            for y in range(self.SIZE-1, -1, -1):  # Back to front
                row = []
                for x in range(self.SIZE):  # Left to right
                    cell = self.board[x, y, z]
                    if cell == 0:
                        row.append('.')
                    elif cell == 1:
                        row.append('O')  # Yellow
                    else:
                        row.append('X')  # Red
                print(' '.join(row))
            print()
    
    def copy(self):
        """Create a copy of the current game state."""
        return Game3D({
            'board': self.board.copy(),
            'player_turn': self.player_turn
        })
    
    def get_move_index(self, x, y):
        """Convert (x, y) move to single index for neural network output."""
        return y * self.SIZE + x
    
    def index_to_move(self, index):
        """Convert single index to (x, y) move."""
        return (index % self.SIZE, index // self.SIZE)