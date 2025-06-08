# 3D Connect 4 Implementation

This document describes the new 3D Connect 4 implementation that has been added to the existing 2D Connect 4 AlphaZero project.

## Overview

The 3D Connect 4 implementation extends the classic Connect 4 game to three dimensions, using a 4×4×4 cubic board instead of the traditional 6×7 flat board. Players take turns dropping pieces into columns, and the goal is to get 4 pieces in a row along any possible straight line in 3D space.

## Key Features

### Game Rules
- **Board**: 4×4×4 cube (64 total positions)
- **Moves**: Players choose a column (x, y) and pieces fall to the lowest available z-position
- **Win Condition**: 4 pieces in any straight line (76 possible winning lines total)
- **Draw**: All 64 positions filled with no winner

### Winning Lines (76 total)
1. **Layer lines (40)**: Within each z-level
   - Horizontal lines: 4 per layer × 4 layers = 16
   - Vertical lines: 4 per layer × 4 layers = 16  
   - Diagonal lines: 2 per layer × 4 layers = 8

2. **Vertical lines (16)**: Through z-axis, one for each (x,y) position

3. **Inter-layer diagonals (16)**:
   - X-Z plane diagonals: 8 lines
   - Y-Z plane diagonals: 8 lines

4. **Space diagonals (4)**: Corner-to-corner through the entire cube

## File Structure

### New 3D Files
- `Game3D.py` - Core 3D game logic and board representation
- `config3d.py` - Configuration parameters for 3D Connect 4
- `ResNet3D.py` - Neural network architecture adapted for 3D
- `MCTS_NN3D.py` - Monte Carlo Tree Search for 3D game
- `game_selector.py` - Unified interface to switch between 2D and 3D games
- `test_game3d.py` - Unit tests for 3D game logic
- `test_integration.py` - Integration tests for all 3D components
- `README_3D_CONNECT4.md` - This documentation

### Preserved Original Files
All existing 2D Connect 4 files remain unchanged:
- `Game_bitboard.py` - Original 2D game logic
- `config.py` - Original 2D configuration
- `ResNet.py` - Original 2D neural network
- `MCTS_NN.py` - Original 2D MCTS
- `Main.py` - Original 2D training loop
- All other existing files...

## Usage

### Quick Start
1. **Run the game selector**:
   ```bash
   python game_selector.py
   ```

2. **Choose game mode**:
   - Enter `2d` for classic Connect 4 (6×7 board)
   - Enter `3d` for 3D Connect 4 (4×4×4 cube)
   - Enter `q` to quit

3. **Select action**:
   - `1`: Run demo to see the game in action
   - `2`: Start training (full training for 3D still in development)
   - `3`: Return to main menu

### Direct Testing
- **Test 3D game logic**: `python test_game3d.py`
- **Integration tests**: `python test_integration.py`

### Example 3D Game Usage
```python
from Game3D import Game3D

# Create new game
game = Game3D()

# Display board
game.display()

# Make moves (x, y coordinates)
game = game.make_move(1, 1)  # Center column
game = game.make_move(2, 2)  # Another column

# Check game status
print(f"Game over: {game.is_game_over()}")
print(f"Winner: {game.get_winner()}")
print(f"Available moves: {game.allowed_moves()}")
```

## Technical Details

### State Representation
- **3D Board**: 4×4×4 numpy array
- **State Vector**: 192 dimensions (64×3 for player1, player2, current_player)
- **Move Representation**: (x, y) tuples for column selection
- **Neural Network Input**: 12 channels of 4×4 (representing z-layers)

### Neural Network Architecture
- **Input**: 12 channels × 4×4 (3D board layers)
- **Output**: 
  - Policy head: 16 possible moves (4×4 columns)
  - Value head: Single value for position evaluation
- **Architecture**: ResNet-based, similar to 2D version but adapted for 3D input/output

### Performance
- **Winning line computation**: Pre-computed for efficiency (76 lines)
- **Move validation**: O(1) using column height tracking
- **State conversion**: Optimized for neural network input

## Implementation Highlights

### Compatibility
- Both 2D and 3D games can run in the same environment
- No conflicts between implementations
- Easy switching via game selector

### Modular Design
- Clean separation between 2D and 3D components
- Consistent API design across both versions
- Reusable patterns from original implementation

### Testing
- Comprehensive unit tests for game logic
- Integration tests for AI components
- Verification of 76 winning lines
- Neural network input/output validation

## Current Status

### ✅ Completed
- [x] 3D game logic and rules
- [x] 4×4×4 board implementation
- [x] 76 winning lines computation
- [x] Neural network architecture
- [x] MCTS adaptation for 3D
- [x] Game selector interface
- [x] Comprehensive testing
- [x] Full compatibility with existing 2D implementation

### 🚧 In Development
- [ ] Complete training pipeline for 3D (main_functions3d.py)
- [ ] Self-play data generation for 3D
- [ ] ELO rating system for 3D
- [ ] Human vs AI interface for 3D
- [ ] Advanced GUI for 3D visualization

### 🎯 Future Enhancements
- [ ] 3D board visualization in GUI
- [ ] Tournament mode between 2D and 3D AIs
- [ ] Performance optimizations for 3D MCTS
- [ ] Different board sizes (e.g., 5×5×5)

## Strategy Tips for 3D Connect 4

1. **Control the center**: Positions (1,1) and (2,2) intersect many winning lines
2. **Think vertically**: Don't forget about vertical connections through z-axis
3. **Block diagonals**: Space diagonals are powerful but often overlooked
4. **Layer awareness**: Control multiple layers simultaneously
5. **Force multiple threats**: Create situations where opponent can't block all threats

## Testing Results

All integration tests pass:
- ✅ Game selector requirements
- ✅ 3D Connect 4 basic functionality  
- ✅ 3D neural network structure
- ✅ 3D MCTS components
- ✅ 2D/3D compatibility

## Contributing

When extending the 3D implementation:
1. Follow the existing naming conventions (append `3D` or `3d`)
2. Maintain compatibility with the 2D version
3. Add appropriate tests for new functionality
4. Update this documentation

## License

This 3D Connect 4 implementation follows the same BSD 3-Clause License as the original project.