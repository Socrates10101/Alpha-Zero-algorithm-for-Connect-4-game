import type { GameState3D, Move3D, Player } from '../types/game3d';
import { gameStorage } from './gameStorage';

export interface GameRecord {
  gameId: string;
  startTime: string;
  endTime: string;
  winner: Player;
  totalMoves: number;
  moves: MoveRecord[];
  boardSize: {
    x: number;
    y: number;
    z: number;
  };
}

interface MoveRecord {
  moveNumber: number;
  player: Player;
  position: {
    x: number;
    y: number;
    z: number;
  };
  timestamp: string;
  boardStateAfter: string; // Compact representation
}

export class GameRecorder {
  private currentGame: GameRecord | null = null;
  private moves: MoveRecord[] = [];

  startNewGame() {
    this.currentGame = {
      gameId: `game_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      startTime: new Date().toISOString(),
      endTime: '',
      winner: null,
      totalMoves: 0,
      moves: [],
      boardSize: {
        x: 4,
        y: 4,
        z: 4
      }
    };
    this.moves = [];
  }

  recordMove(move: Move3D, boardState: Player[][][], resultingY: number) {
    if (!this.currentGame) return;

    const moveRecord: MoveRecord = {
      moveNumber: this.moves.length + 1,
      player: move.player,
      position: {
        x: move.x,
        y: resultingY,
        z: move.z
      },
      timestamp: new Date().toISOString(),
      boardStateAfter: this.encodeBoardState(boardState)
    };

    this.moves.push(moveRecord);
    this.currentGame.moves = this.moves;
    this.currentGame.totalMoves = this.moves.length;
  }

  endGame(winner: Player) {
    if (!this.currentGame) return;

    this.currentGame.endTime = new Date().toISOString();
    this.currentGame.winner = winner;

    // Save the game
    this.saveGameRecord();
  }

  private encodeBoardState(board: Player[][][]): string {
    // Compact representation: Y=Yellow, R=Red, ·=empty
    let encoded = '';
    for (let y = 3; y >= 0; y--) {
      for (let z = 0; z < 4; z++) {
        for (let x = 0; x < 4; x++) {
          const cell = board[x][y][z];
          encoded += cell === 'yellow' ? 'Y' : cell === 'red' ? 'R' : '·';
        }
        encoded += ' ';
      }
      encoded += '\n';
    }
    return encoded.trim();
  }

  private saveGameRecord() {
    if (!this.currentGame) return;

    // Save to storage instead of downloading
    gameStorage.saveGame(this.currentGame);

    // Show notification to user
    const notification = document.createElement('div');
    notification.className = 'game-saved-notification';
    notification.textContent = 'Game record saved!';
    document.body.appendChild(notification);

    // Remove notification after 3 seconds
    setTimeout(() => {
      notification.classList.add('fade-out');
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 500);
    }, 3000);
  }

  // Methods for accessing saved games
  getAllGames() {
    return gameStorage.getAllGames();
  }

  getGame(gameId: string) {
    return gameStorage.getGame(gameId);
  }

  exportGameAsPython(gameId: string) {
    return gameStorage.exportGameAsPython(gameId);
  }

  exportAllGamesAsJson() {
    return gameStorage.exportGamesAsJson();
  }
}

// Create a singleton instance
export const gameRecorder = new GameRecorder();