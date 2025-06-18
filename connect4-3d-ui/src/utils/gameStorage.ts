import type { GameRecord } from './gameRecorder';

const STORAGE_KEY = 'connect4_3d_games';

export class GameStorage {
  private games: GameRecord[] = [];

  constructor() {
    this.loadGames();
  }

  private loadGames() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        this.games = JSON.parse(stored);
      }
    } catch (error) {
      console.error('Failed to load games from storage:', error);
      this.games = [];
    }
  }

  saveGame(gameRecord: GameRecord) {
    this.games.push(gameRecord);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.games));
      console.log(`Game saved: ${gameRecord.gameId}`);
      
      // Also log the game data structure for developers
      console.log('Game data structure:', gameRecord);
      
      // Generate and log the Python code
      const pythonCode = this.generatePythonCode(gameRecord);
      console.log('Python code for this game:');
      console.log(pythonCode);
      
    } catch (error) {
      console.error('Failed to save game to storage:', error);
    }
  }

  getAllGames(): GameRecord[] {
    return [...this.games];
  }

  getGame(gameId: string): GameRecord | undefined {
    return this.games.find(game => game.gameId === gameId);
  }

  // Get game by index for easier access
  getGameByIndex(index: number): GameRecord | undefined {
    return this.games[index];
  }

  clearAllGames() {
    this.games = [];
    localStorage.removeItem(STORAGE_KEY);
  }

  exportGamesAsJson(): string {
    return JSON.stringify(this.games, null, 2);
  }

  exportGameAsPython(gameId: string): string | null {
    const game = this.getGame(gameId);
    if (!game) return null;
    return this.generatePythonCode(game);
  }

  private generatePythonCode(game: GameRecord): string {
    const pythonCode = `#!/usr/bin/env python3
"""
Connect 4 3D Game Replay
Game ID: ${game.gameId}
Date: ${new Date(game.startTime).toLocaleString()}
Winner: ${game.winner || 'Draw'}
Total Moves: ${game.totalMoves}
"""

import numpy as np
from typing import Optional, Tuple, List

class Connect4_3D:
    def __init__(self):
        self.board = np.full((4, 4, 4), None)  # x, y, z
        self.current_player = 'yellow'
        self.moves_history = []
        
    def drop_piece(self, x: int, z: int) -> Optional[int]:
        """Drop a piece at position (x, z) and return the y level it lands on"""
        for y in range(4):
            if self.board[x, y, z] is None:
                self.board[x, y, z] = self.current_player
                self.moves_history.append((x, y, z, self.current_player))
                return y
        return None
    
    def switch_player(self):
        """Switch to the other player"""
        self.current_player = 'red' if self.current_player == 'yellow' else 'yellow'
    
    def check_winner(self, last_move: Tuple[int, int, int]) -> bool:
        """Check if the last move created a winning line"""
        x, y, z = last_move
        player = self.board[x, y, z]
        
        # All 13 possible directions in 3D
        directions = [
            (1, 0, 0), (-1, 0, 0),  # X axis
            (0, 1, 0), (0, -1, 0),  # Y axis
            (0, 0, 1), (0, 0, -1),  # Z axis
            (1, 1, 0), (-1, -1, 0), (1, -1, 0), (-1, 1, 0),  # XY diagonals
            (1, 0, 1), (-1, 0, -1), (1, 0, -1), (-1, 0, 1),  # XZ diagonals
            (0, 1, 1), (0, -1, -1), (0, 1, -1), (0, -1, 1),  # YZ diagonals
            (1, 1, 1), (-1, -1, -1), (1, -1, -1), (-1, 1, 1),  # 3D diagonals
            (1, 1, -1), (-1, -1, 1), (1, -1, 1), (-1, 1, -1)
        ]
        
        for dx, dy, dz in directions:
            count = 1
            # Check positive direction
            for i in range(1, 4):
                nx, ny, nz = x + i*dx, y + i*dy, z + i*dz
                if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4:
                    if self.board[nx, ny, nz] == player:
                        count += 1
                    else:
                        break
                else:
                    break
            
            # Check negative direction
            for i in range(1, 4):
                nx, ny, nz = x - i*dx, y - i*dy, z - i*dz
                if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4:
                    if self.board[nx, ny, nz] == player:
                        count += 1
                    else:
                        break
                else:
                    break
            
            if count >= 4:
                return True
        
        return False
    
    def print_board(self):
        """Print the board in a readable format"""
        print("\\nCurrent Board State:")
        print("=" * 60)
        for y in range(3, -1, -1):
            print(f"\\nLayer {y + 1}:")
            for z in range(4):
                row = ""
                for x in range(4):
                    cell = self.board[x, y, z]
                    if cell == 'yellow':
                        row += "Y "
                    elif cell == 'red':
                        row += "R "
                    else:
                        row += "· "
                print(f"  {row}")

# Replay the actual game
def replay_game():
    game = Connect4_3D()
    
    # Game moves from the actual play session
    moves = [
${game.moves.map(move => 
  `        (${move.position.x}, ${move.position.z}),  # Move ${move.moveNumber}: ${move.player} → drops to level ${move.position.y}`
).join('\n')}
    ]
    
    print("Starting Connect 4 3D Game Replay")
    print("=" * 60)
    
    for i, (x, z) in enumerate(moves):
        print(f"\\nMove {i + 1}: {game.current_player.upper()} plays at ({x}, {z})")
        
        y = game.drop_piece(x, z)
        if y is not None:
            print(f"  Piece drops to level {y}")
            
            if game.check_winner((x, y, z)):
                print(f"\\n🎉 {game.current_player.upper()} WINS! 🎉")
                game.print_board()
                break
            
            game.switch_player()
        else:
            print("  Invalid move - column full!")
    
    print("\\nFinal moves history:")
    for move in game.moves_history:
        x, y, z, player = move
        print(f"  {player}: ({x}, {y}, {z})")

if __name__ == "__main__":
    replay_game()
`;

    return pythonCode;
  }
}

// Create a singleton instance
export const gameStorage = new GameStorage();