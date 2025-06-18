import { useState, useEffect, useCallback } from 'react';
import { Board3D_4x4x4 } from './Board3D_4x4x4';
import type { GameState3D, Player } from '../types/game3d';
import type { GameRecord } from '../utils/gameRecorder';
import './GameReplay.css';

interface GameReplayProps {
  gameRecord: GameRecord;
  onClose: () => void;
}

export function GameReplay({ gameRecord, onClose }: GameReplayProps) {
  const [currentMoveIndex, setCurrentMoveIndex] = useState(-1);
  const [isPlaying, setIsPlaying] = useState(false);
  const [gameState, setGameState] = useState<GameState3D>(() => ({
    board: Array(4).fill(null).map(() => 
      Array(4).fill(null).map(() => 
        Array(4).fill(null)
      )
    ),
    currentPlayer: 'yellow' as Player,
    winner: null,
    isDraw: false,
    winningPositions: []
  }));
  const [isAnimating, setIsAnimating] = useState(false);

  // Build game state from moves
  const buildGameStateAtMove = useCallback((moveIndex: number): GameState3D => {
    const board: Player[][][] = Array(4).fill(null).map(() => 
      Array(4).fill(null).map(() => 
        Array(4).fill(null)
      )
    );

    // Apply all moves up to moveIndex
    for (let i = 0; i <= moveIndex && i < gameRecord.moves.length; i++) {
      const move = gameRecord.moves[i];
      board[move.position.x][move.position.y][move.position.z] = move.player;
    }

    // Determine current player
    const currentPlayer = moveIndex >= gameRecord.moves.length - 1 
      ? gameRecord.winner || 'yellow'
      : gameRecord.moves[moveIndex + 1]?.player || 'yellow';

    // Check if this is the winning move
    const isLastMove = moveIndex === gameRecord.moves.length - 1;
    const winner = isLastMove ? gameRecord.winner : null;

    return {
      board,
      currentPlayer,
      winner,
      isDraw: isLastMove && !winner,
      winningPositions: winner && isLastMove ? getWinningPositions(board, gameRecord.moves[moveIndex].position) : []
    };
  }, [gameRecord]);

  // Get winning positions
  const getWinningPositions = (board: Player[][][], lastMove: { x: number; y: number; z: number }) => {
    const player = board[lastMove.x][lastMove.y][lastMove.z];
    if (!player) return [];

    // All 13 possible directions in 3D space
    const directions = [
      { dx: 1, dy: 0, dz: 0 },   // x-axis
      { dx: 0, dy: 1, dz: 0 },   // y-axis
      { dx: 0, dy: 0, dz: 1 },   // z-axis
      { dx: 1, dy: 1, dz: 0 },   // xy diagonal
      { dx: 1, dy: -1, dz: 0 },  // xy diagonal
      { dx: 1, dy: 0, dz: 1 },   // xz diagonal
      { dx: 1, dy: 0, dz: -1 },  // xz diagonal
      { dx: 0, dy: 1, dz: 1 },   // yz diagonal
      { dx: 0, dy: 1, dz: -1 },  // yz diagonal
      { dx: 1, dy: 1, dz: 1 },   // main diagonal
      { dx: 1, dy: 1, dz: -1 },  // diagonal
      { dx: 1, dy: -1, dz: 1 },  // diagonal
      { dx: 1, dy: -1, dz: -1 }  // diagonal
    ];

    for (const { dx, dy, dz } of directions) {
      const positions = [lastMove];
      
      // Check positive direction
      for (let i = 1; i < 4; i++) {
        const x = lastMove.x + dx * i;
        const y = lastMove.y + dy * i;
        const z = lastMove.z + dz * i;
        if (x < 0 || x >= 4 || y < 0 || y >= 4 || z < 0 || z >= 4 || board[x][y][z] !== player) break;
        positions.push({ x, y, z });
      }
      
      // Check negative direction
      for (let i = 1; i < 4; i++) {
        const x = lastMove.x - dx * i;
        const y = lastMove.y - dy * i;
        const z = lastMove.z - dz * i;
        if (x < 0 || x >= 4 || y < 0 || y >= 4 || z < 0 || z >= 4 || board[x][y][z] !== player) break;
        positions.push({ x, y, z });
      }
      
      if (positions.length >= 4) {
        return positions;
      }
    }
    
    return [];
  };

  // Play next move
  const playNextMove = useCallback(() => {
    if (currentMoveIndex >= gameRecord.moves.length - 1) {
      setIsPlaying(false);
      return;
    }

    setIsAnimating(true);
    setCurrentMoveIndex(prev => prev + 1);
    
    setTimeout(() => {
      setIsAnimating(false);
    }, 700);
  }, [currentMoveIndex, gameRecord.moves.length]);

  // Auto-play effect
  useEffect(() => {
    if (isPlaying && !isAnimating) {
      const timer = setTimeout(() => {
        playNextMove();
      }, 1000); // 1 second between moves

      return () => clearTimeout(timer);
    }
  }, [isPlaying, isAnimating, playNextMove]);

  // Update game state when move index changes
  useEffect(() => {
    if (currentMoveIndex >= -1) {
      setGameState(buildGameStateAtMove(currentMoveIndex));
    }
  }, [currentMoveIndex, buildGameStateAtMove]);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleReset = () => {
    setIsPlaying(false);
    setCurrentMoveIndex(-1);
  };

  const handleStepForward = () => {
    if (currentMoveIndex < gameRecord.moves.length - 1) {
      setIsPlaying(false);
      playNextMove();
    }
  };

  const handleStepBackward = () => {
    if (currentMoveIndex >= 0) {
      setIsPlaying(false);
      setCurrentMoveIndex(prev => prev - 1);
    }
  };

  return (
    <div className="game-replay-overlay">
      <div className="game-replay-container">
        <div className="replay-header">
          <h2>Game Replay</h2>
          <div className="replay-info">
            <span>Date: {new Date(gameRecord.startTime).toLocaleString()}</span>
            <span>Winner: {gameRecord.winner?.toUpperCase() || 'Draw'}</span>
            <span>Total Moves: {gameRecord.totalMoves}</span>
          </div>
          <button className="close-replay-btn" onClick={onClose}>×</button>
        </div>

        <div className="replay-board">
          <Board3D_4x4x4
            gameState={gameState}
            onCellClick={() => {}}
            onCellHover={() => {}}
            isAnimating={isAnimating}
            animatingPosition={null}
            selectedCell={{ x: -1, z: -1 }}
            isKeyboardMode={false}
          />
        </div>

        <div className="replay-controls">
          <div className="move-info">
            Move {currentMoveIndex + 1} / {gameRecord.moves.length}
            {currentMoveIndex >= 0 && currentMoveIndex < gameRecord.moves.length && (
              <span className="current-move-detail">
                {' - '}
                {gameRecord.moves[currentMoveIndex].player.toUpperCase()} at 
                ({gameRecord.moves[currentMoveIndex].position.x}, {gameRecord.moves[currentMoveIndex].position.z})
              </span>
            )}
          </div>

          <div className="control-buttons">
            <button 
              onClick={handleReset} 
              className="control-btn"
              title="Reset"
            >
              ⟲
            </button>
            <button 
              onClick={handleStepBackward} 
              className="control-btn"
              disabled={currentMoveIndex < 0}
              title="Previous move"
            >
              ◀
            </button>
            <button 
              onClick={handlePlayPause} 
              className="control-btn play-pause"
              title={isPlaying ? "Pause" : "Play"}
            >
              {isPlaying ? '⏸' : '▶'}
            </button>
            <button 
              onClick={handleStepForward} 
              className="control-btn"
              disabled={currentMoveIndex >= gameRecord.moves.length - 1}
              title="Next move"
            >
              ▶
            </button>
          </div>

          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ 
                width: `${((currentMoveIndex + 1) / gameRecord.moves.length) * 100}%` 
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}