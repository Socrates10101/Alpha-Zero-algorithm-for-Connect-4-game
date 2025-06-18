import { useState, useCallback } from 'react';
import type { GameState, Player, BoardPosition } from '../types/game';

const ROWS = 6;
const COLUMNS = 7;

export function useConnect4Game() {
  const [gameState, setGameState] = useState<GameState>(() => ({
    board: Array(COLUMNS).fill(null).map(() => Array(ROWS).fill(null)),
    currentPlayer: 'yellow',
    winner: null,
    isDraw: false,
    winningPositions: []
  }));

  const [isAnimating, setIsAnimating] = useState(false);

  const checkWinner = useCallback((board: Player[][], lastCol: number, lastRow: number): { winner: Player; positions: BoardPosition[] } | null => {
    const player = board[lastCol][lastRow];
    if (!player) return null;

    // Check all directions
    const directions = [
      { dx: 1, dy: 0 },   // horizontal
      { dx: 0, dy: 1 },   // vertical
      { dx: 1, dy: 1 },   // diagonal /
      { dx: 1, dy: -1 }   // diagonal \
    ];

    for (const { dx, dy } of directions) {
      const positions: BoardPosition[] = [{ row: lastRow, column: lastCol }];
      
      // Check positive direction
      for (let i = 1; i < 4; i++) {
        const col = lastCol + dx * i;
        const row = lastRow + dy * i;
        if (col < 0 || col >= COLUMNS || row < 0 || row >= ROWS || board[col][row] !== player) break;
        positions.push({ row, column: col });
      }
      
      // Check negative direction
      for (let i = 1; i < 4; i++) {
        const col = lastCol - dx * i;
        const row = lastRow - dy * i;
        if (col < 0 || col >= COLUMNS || row < 0 || row >= ROWS || board[col][row] !== player) break;
        positions.push({ row, column: col });
      }
      
      if (positions.length >= 4) {
        return { winner: player, positions };
      }
    }
    
    return null;
  }, []);

  const makeMove = useCallback((column: number) => {
    if (gameState.winner || gameState.isDraw || isAnimating) return false;

    const newBoard = gameState.board.map(col => [...col]);
    const row = newBoard[column].findIndex(cell => cell === null);
    
    if (row === -1) return false;

    setIsAnimating(true);
    newBoard[column][row] = gameState.currentPlayer;

    const winnerInfo = checkWinner(newBoard, column, row);
    const isDraw = !winnerInfo && newBoard.every(col => col.every(cell => cell !== null));

    setGameState({
      board: newBoard,
      currentPlayer: gameState.currentPlayer === 'yellow' ? 'red' : 'yellow',
      winner: winnerInfo?.winner || null,
      isDraw,
      winningPositions: winnerInfo?.positions || []
    });

    setTimeout(() => setIsAnimating(false), 700);
    return true;
  }, [gameState, checkWinner, isAnimating]);

  const resetGame = useCallback(() => {
    setGameState({
      board: Array(COLUMNS).fill(null).map(() => Array(ROWS).fill(null)),
      currentPlayer: 'yellow',
      winner: null,
      isDraw: false,
      winningPositions: []
    });
    setIsAnimating(false);
  }, []);

  return {
    gameState,
    makeMove,
    resetGame,
    isAnimating
  };
}