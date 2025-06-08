#  ================ Test for 3D Connect 4 game =================== #
# Name:             test_game3d.py
# Description:      Test script for 3D Connect 4 implementation
# Authors:          AI Assistant
# Date:             2025
# License:          BSD 3-Clause License
# ============================================================================ #

from Game3D import Game3D
import numpy as np

def test_winning_lines_count():
    """Test that we have exactly 76 winning lines."""
    game = Game3D()
    lines = game._winning_lines
    print(f"Total winning lines: {len(lines)}")
    
    # Count by category
    layer_lines = 0  # 40 expected (10 per layer × 4 layers)
    vertical_lines = 0  # 16 expected (one for each x,y position)
    xz_diagonal_lines = 0  # 8 expected
    yz_diagonal_lines = 0  # 8 expected
    space_diagonal_lines = 0  # 4 expected
    
    for line in lines:
        # Check if all z coordinates are the same (layer line)
        z_coords = [pos[2] for pos in line]
        if len(set(z_coords)) == 1:
            layer_lines += 1
        # Check if x,y are the same for all positions (vertical line)
        elif len(set((pos[0], pos[1]) for pos in line)) == 1:
            vertical_lines += 1
        # Check if it's a space diagonal
        elif all(pos[0] == pos[1] == pos[2] for pos in line) or \
             all(pos[0] == pos[1] == 3-pos[2] for pos in line) or \
             all(pos[0] == 3-pos[1] == pos[2] for pos in line) or \
             all(pos[0] == 3-pos[1] == 3-pos[2] for pos in line):
            space_diagonal_lines += 1
        else:
            # Check if y is constant (xz diagonal)
            y_coords = [pos[1] for pos in line]
            if len(set(y_coords)) == 1:
                xz_diagonal_lines += 1
            # Check if x is constant (yz diagonal)
            else:
                yz_diagonal_lines += 1
    
    print(f"Layer lines: {layer_lines} (expected: 40)")
    print(f"Vertical lines: {vertical_lines} (expected: 16)")
    print(f"XZ diagonal lines: {xz_diagonal_lines} (expected: 8)")
    print(f"YZ diagonal lines: {yz_diagonal_lines} (expected: 8)")
    print(f"Space diagonal lines: {space_diagonal_lines} (expected: 4)")
    
    total = layer_lines + vertical_lines + xz_diagonal_lines + yz_diagonal_lines + space_diagonal_lines
    print(f"Total: {total}")
    
    assert len(lines) == 76, f"Expected 76 winning lines, got {len(lines)}"
    print("✓ Winning lines count test passed!")

def test_basic_gameplay():
    """Test basic game functionality."""
    game = Game3D()
    
    # Test initial state
    assert game.player_turn == 1
    assert len(game.allowed_moves()) == 16  # All 16 columns available
    assert not game.is_game_over()
    print("✓ Initial state test passed!")
    
    # Test making moves
    new_game = game.make_move(0, 0)
    assert new_game.player_turn == -1
    assert new_game.board[0, 0, 0] == 1  # Piece should be at bottom
    print("✓ Move making test passed!")
    
    # Test column filling
    current_game = game
    for i in range(4):  # Fill column (0,0) completely
        current_game = current_game.make_move(0, 0)
    
    # Column should now be full
    assert not current_game.is_valid_move(0, 0)
    print("✓ Column filling test passed!")

def test_win_detection():
    """Test win detection for different line types."""
    # Test vertical win
    game = Game3D()
    
    # Player 1 wins with vertical line in column (1,1)
    game.board[1, 1, 0] = 1
    game.board[1, 1, 1] = 1
    game.board[1, 1, 2] = 1
    game.board[1, 1, 3] = 1
    
    assert game.check_win(1)
    assert not game.check_win(-1)
    print("✓ Vertical win test passed!")
    
    # Test horizontal win
    game = Game3D()
    game.board[0, 0, 0] = 1
    game.board[1, 0, 0] = 1
    game.board[2, 0, 0] = 1
    game.board[3, 0, 0] = 1
    
    assert game.check_win(1)
    print("✓ Horizontal win test passed!")
    
    # Test space diagonal win
    game = Game3D()
    game.board[0, 0, 0] = 1
    game.board[1, 1, 1] = 1
    game.board[2, 2, 2] = 1
    game.board[3, 3, 3] = 1
    
    assert game.check_win(1)
    print("✓ Space diagonal win test passed!")

def test_state_vector():
    """Test state vector conversion."""
    game = Game3D()
    game.board[0, 0, 0] = 1
    game.board[1, 1, 1] = -1
    
    vector = game.get_state_vector()
    assert len(vector) == 192  # 64*3
    
    # Check that the vector correctly represents the board
    player1_part = vector[:64]
    player2_part = vector[64:128]
    current_player_part = vector[128:]
    
    # Player 1's piece should be at position (0,0,0) -> index 0
    assert player1_part[0] == 1
    # Player 2's piece should be at position (1,1,1) -> index 1*16 + 1*4 + 1 = 21
    assert player2_part[21] == 1
    # Current player should be 1
    assert all(current_player_part == 1)
    
    print("✓ State vector test passed!")

if __name__ == "__main__":
    print("Running 3D Connect 4 tests...")
    test_winning_lines_count()
    test_basic_gameplay()
    test_win_detection()
    test_state_vector()
    print("\n✓ All tests passed!")