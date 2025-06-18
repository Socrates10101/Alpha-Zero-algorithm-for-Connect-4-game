import { useState, useCallback, useEffect } from 'react';
import type { GameState3D, Player, Position3D } from '../types/game3d';
import { gameRecorder } from '../utils/gameRecorder';

const SIZE = 4; // 4x4x4 grid

export function useConnect4Game3D() {
  const [gameState, setGameState] = useState<GameState3D>(() => ({
    board: Array(SIZE).fill(null).map(() => 
      Array(SIZE).fill(null).map(() => 
        Array(SIZE).fill(null)
      )
    ),
    currentPlayer: 'yellow',
    winner: null,
    isDraw: false,
    winningPositions: []
  }));

  const [isAnimating, setIsAnimating] = useState(false);
  const [animatingPosition, setAnimatingPosition] = useState<{x: number, z: number} | null>(null);

  // Start recording when component mounts
  useEffect(() => {
    gameRecorder.startNewGame();
  }, []);

  const checkWinner = useCallback((board: Player[][][], lastPos: Position3D): { winner: Player; positions: Position3D[] } | null => {
    const player = board[lastPos.x][lastPos.y][lastPos.z];
    if (!player) return null;

    // All 13 possible directions in 3D space
    const directions = [
      // 2D directions on each plane
      { dx: 1, dy: 0, dz: 0 },   // x-axis
      { dx: 0, dy: 1, dz: 0 },   // y-axis
      { dx: 0, dy: 0, dz: 1 },   // z-axis
      { dx: 1, dy: 1, dz: 0 },   // xy diagonal
      { dx: 1, dy: -1, dz: 0 },  // xy diagonal
      { dx: 1, dy: 0, dz: 1 },   // xz diagonal
      { dx: 1, dy: 0, dz: -1 },  // xz diagonal
      { dx: 0, dy: 1, dz: 1 },   // yz diagonal
      { dx: 0, dy: 1, dz: -1 },  // yz diagonal
      // 3D diagonals
      { dx: 1, dy: 1, dz: 1 },   // main diagonal
      { dx: 1, dy: 1, dz: -1 },  // diagonal
      { dx: 1, dy: -1, dz: 1 },  // diagonal
      { dx: 1, dy: -1, dz: -1 }  // diagonal
    ];

    for (const { dx, dy, dz } of directions) {
      const positions: Position3D[] = [{ ...lastPos }];
      
      // Check positive direction
      for (let i = 1; i < 4; i++) {
        const x = lastPos.x + dx * i;
        const y = lastPos.y + dy * i;
        const z = lastPos.z + dz * i;
        if (x < 0 || x >= SIZE || y < 0 || y >= SIZE || z < 0 || z >= SIZE || board[x][y][z] !== player) break;
        positions.push({ x, y, z });
      }
      
      // Check negative direction
      for (let i = 1; i < 4; i++) {
        const x = lastPos.x - dx * i;
        const y = lastPos.y - dy * i;
        const z = lastPos.z - dz * i;
        if (x < 0 || x >= SIZE || y < 0 || y >= SIZE || z < 0 || z >= SIZE || board[x][y][z] !== player) break;
        positions.push({ x, y, z });
      }
      
      if (positions.length >= 4) {
        return { winner: player, positions };
      }
    }
    
    return null;
  }, []);

  const makeMove = useCallback((x: number, z: number) => {
    if (gameState.winner || gameState.isDraw || isAnimating) return false;

    const newBoard = gameState.board.map(plane => 
      plane.map(row => [...row])
    );
    
    // Find the lowest empty position in the column
    let y = -1;
    for (let i = 0; i < SIZE; i++) {
      if (newBoard[x][i][z] === null) {
        y = i;
        break;
      }
    }
    
    if (y === -1) return false;

    setIsAnimating(true);
    setAnimatingPosition({x, z});
    newBoard[x][y][z] = gameState.currentPlayer;

    // Record the move
    gameRecorder.recordMove(
      { x, z, player: gameState.currentPlayer },
      newBoard,
      y
    );

    const winnerInfo = checkWinner(newBoard, { x, y, z });
    const isDraw = !winnerInfo && newBoard.every(plane => 
      plane.every(row => 
        row.every(cell => cell !== null)
      )
    );

    const winner = winnerInfo?.winner || null;
    
    setGameState({
      board: newBoard,
      currentPlayer: gameState.currentPlayer === 'yellow' ? 'red' : 'yellow',
      winner,
      isDraw,
      winningPositions: winnerInfo?.positions || []
    });

    // End game recording if game is over
    if (winner || isDraw) {
      setTimeout(() => {
        gameRecorder.endGame(winner);
      }, 800); // Wait for animation to complete
    }

    setTimeout(() => {
      setIsAnimating(false);
      setAnimatingPosition(null);
    }, 700);
    return true;
  }, [gameState, checkWinner, isAnimating]);

  const resetGame = useCallback(() => {
    setGameState({
      board: Array(SIZE).fill(null).map(() => 
        Array(SIZE).fill(null).map(() => 
          Array(SIZE).fill(null)
        )
      ),
      currentPlayer: 'yellow',
      winner: null,
      isDraw: false,
      winningPositions: []
    });
    setIsAnimating(false);
    // Start recording new game
    gameRecorder.startNewGame();
  }, []);

  return {
    gameState,
    makeMove,
    resetGame,
    isAnimating,
    animatingPosition
  };
}