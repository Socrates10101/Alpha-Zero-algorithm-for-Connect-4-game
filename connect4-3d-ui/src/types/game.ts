export type Player = 'yellow' | 'red' | null;

export interface BoardPosition {
  row: number;
  column: number;
}

export interface GameState {
  board: Player[][];
  currentPlayer: Player;
  winner: Player;
  isDraw: boolean;
  winningPositions: BoardPosition[];
}

export interface Move {
  column: number;
  player: Player;
}