import { useState, useEffect, useCallback, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import type { GameState3D, Player } from '../types/game3d';
import type { GameRecord } from '../utils/gameRecorder';
import { BoardGrid3D } from './BoardGrid3D';
import { GamePieces3D } from './GamePieces3D';
import { Lighting } from './Lighting';
import { WinningLine3D } from './WinningLine3D';
import { AIBattleVictoryEffects } from './AIBattleVictoryEffects';
import './AIBattleView.css';

interface AIBattleViewProps {
  gameRecord: GameRecord;
  onClose: () => void;
}

type PlaybackSpeed = 1 | 2 | 4;

export function AIBattleView({ gameRecord, onClose }: AIBattleViewProps) {
  const [currentMoveIndex, setCurrentMoveIndex] = useState(-1);
  const [isPlaying, setIsPlaying] = useState(true); // Auto-play by default
  const [playbackSpeed, setPlaybackSpeed] = useState<PlaybackSpeed>(1);
  const [showThinking, setShowThinking] = useState(false);
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
  const animationTimeoutRef = useRef<number | null>(null);
  const thinkingTimeoutRef = useRef<number | null>(null);
  const playTimeoutRef = useRef<number | null>(null);

  // Cleanup timeouts on unmount
  useEffect(() => {
    return () => {
      if (animationTimeoutRef.current) clearTimeout(animationTimeoutRef.current);
      if (thinkingTimeoutRef.current) clearTimeout(thinkingTimeoutRef.current);
      if (playTimeoutRef.current) clearTimeout(playTimeoutRef.current);
    };
  }, []);

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

  // Play next move with thinking animation
  const playNextMove = useCallback(() => {
    if (currentMoveIndex >= gameRecord.moves.length - 1) {
      setIsPlaying(false);
      return;
    }

    // Show thinking indicator
    setShowThinking(true);
    
    // Brief thinking delay (varies by speed)
    const thinkingDelay = 300 / playbackSpeed;
    
    thinkingTimeoutRef.current = window.setTimeout(() => {
      setShowThinking(false);
      setIsAnimating(true);
      setCurrentMoveIndex(prev => prev + 1);
      
      // Fast drop animation
      const animationDelay = 400 / playbackSpeed;
      animationTimeoutRef.current = window.setTimeout(() => {
        setIsAnimating(false);
      }, animationDelay);
    }, thinkingDelay);
  }, [currentMoveIndex, gameRecord.moves.length, playbackSpeed]);

  // Auto-play effect
  useEffect(() => {
    if (isPlaying && !isAnimating && !showThinking) {
      const delay = 800 / playbackSpeed; // Base delay between moves
      playTimeoutRef.current = window.setTimeout(() => {
        playNextMove();
      }, delay);

      return () => {
        if (playTimeoutRef.current) clearTimeout(playTimeoutRef.current);
      };
    }
  }, [isPlaying, isAnimating, showThinking, playNextMove, playbackSpeed]);

  // Update game state when move index changes
  useEffect(() => {
    if (currentMoveIndex >= -1) {
      setGameState(buildGameStateAtMove(currentMoveIndex));
    }
  }, [currentMoveIndex, buildGameStateAtMove]);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleSpeedChange = (speed: PlaybackSpeed) => {
    setPlaybackSpeed(speed);
  };

  // Calculate progress percentage
  const progress = ((currentMoveIndex + 1) / gameRecord.moves.length) * 100;

  // Get current move info
  const currentMove = currentMoveIndex >= 0 && currentMoveIndex < gameRecord.moves.length 
    ? gameRecord.moves[currentMoveIndex] 
    : null;

  // Calculate game duration
  const gameDuration = new Date(gameRecord.endTime).getTime() - new Date(gameRecord.startTime).getTime();
  const durationMinutes = Math.floor(gameDuration / 60000);
  const durationSeconds = Math.floor((gameDuration % 60000) / 1000);

  return (
    <div className="ai-battle-view">
      <div className="battle-header">
        <div className="battle-title">
          <h1>AI Battle Replay</h1>
          <div className="battle-subtitle">
            {new Date(gameRecord.startTime).toLocaleDateString()} • {gameRecord.totalMoves} moves
          </div>
        </div>
        <button className="close-battle-btn" onClick={onClose}>×</button>
      </div>

      <div className="battle-arena">
        <Canvas shadows className="battle-canvas">
          <PerspectiveCamera makeDefault position={[12, 8, 12]} fov={55} />
          <OrbitControls 
            enablePan={false} 
            enableZoom={false}
            enableRotate={true}
            target={[1.5, 1.5, 1.5]}
            autoRotate={true}
            autoRotateSpeed={0.5}
            rotateSpeed={0.5}
            minPolarAngle={Math.PI / 4}
            maxPolarAngle={Math.PI / 2.5}
          />
          
          {/* White background */}
          <color attach="background" args={['#f8fafc']} />
          <fog attach="fog" args={['#e2e8f0', 10, 40]} />
          
          {/* Bright, even lighting for white background */}
          <ambientLight intensity={0.9} />
          <pointLight position={[10, 10, 10]} intensity={0.8} />
          <pointLight position={[-10, 10, -10]} intensity={0.8} />
          <directionalLight position={[5, 10, 5]} intensity={0.4} castShadow />
          <BoardGrid3D 
            onCellClick={() => {}}
            onCellHover={() => {}}
            isAnimating={isAnimating}
            animatingPosition={null}
            board={gameState.board}
            currentPlayer={gameState.currentPlayer}
            selectedCell={{ x: -1, z: -1 }}
            isKeyboardMode={false}
            hasWinner={!!gameState.winner}
          />
          <GamePieces3D board={gameState.board} winningPositions={gameState.winningPositions} />
          
          {/* Winning line and effects */}
          {gameState.winner && gameState.winningPositions.length > 0 && (
            <>
              <WinningLine3D 
                winningPositions={gameState.winningPositions}
                color={gameState.winner === 'yellow' ? '#facc15' : '#ef4444'}
              />
              <AIBattleVictoryEffects winner={gameState.winner} />
            </>
          )}
        </Canvas>

        {/* AI Thinking Indicator */}
        {showThinking && currentMoveIndex < gameRecord.moves.length - 1 && (
          <div className="ai-thinking">
            <div className="thinking-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <div className="thinking-text">
              {gameRecord.moves[currentMoveIndex + 1]?.player.toUpperCase()} AI analyzing...
            </div>
          </div>
        )}

        {/* Move Information */}
        {currentMove && currentMove.player && (
          <div className={`move-info-panel ${currentMove.player}`}>
            <div className="move-number">Move {currentMoveIndex + 1}</div>
            <div className="move-player">{currentMove.player.toUpperCase()}</div>
            <div className="move-position">
              Position: ({currentMove.position.x}, {currentMove.position.y}, {currentMove.position.z})
            </div>
          </div>
        )}
      </div>

      <div className="battle-controls">
        <div className="progress-section">
          <div className="progress-bar-container">
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="progress-labels">
              <span>Move {currentMoveIndex + 1} / {gameRecord.moves.length}</span>
              {gameState.winner && (
                <span className={`winner-label ${gameState.winner}`}>
                  {gameState.winner.toUpperCase()} WINS!
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="control-section">
          <button 
            onClick={handlePlayPause} 
            className="play-pause-btn"
            title={isPlaying ? "Pause" : "Play"}
          >
            {isPlaying ? '⏸' : '▶'}
          </button>

          <div className="speed-controls">
            <span className="speed-label">Speed:</span>
            {[1, 2, 4].map((speed) => (
              <button
                key={speed}
                className={`speed-btn ${playbackSpeed === speed ? 'active' : ''}`}
                onClick={() => handleSpeedChange(speed as PlaybackSpeed)}
              >
                {speed}x
              </button>
            ))}
          </div>
        </div>

        <div className="stats-section">
          <div className="stat-item">
            <span className="stat-label">Duration:</span>
            <span className="stat-value">{durationMinutes}:{durationSeconds.toString().padStart(2, '0')}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Winner:</span>
            <span className={`stat-value ${gameRecord.winner}`}>
              {gameRecord.winner ? gameRecord.winner.toUpperCase() : 'DRAW'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}