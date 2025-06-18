export type Player = 'yellow' | 'red' | null;

export interface Position3D {
  x: number;
  y: number;
  z: number;
}

export interface GameState3D {
  board: Player[][][]; // [x][y][z]
  currentPlayer: Player;
  winner: Player;
  isDraw: boolean;
  winningPositions: Position3D[];
}

export interface Move3D {
  x: number;
  z: number;
  player: Player;
}