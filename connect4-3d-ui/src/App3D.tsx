import './App.css';
import { useState, useEffect, useCallback } from 'react';
import { Board3D_4x4x4 } from './components/Board3D_4x4x4';
import { useConnect4Game3D } from './hooks/useConnect4Game3D';
import { LayerVisualization } from './components/LayerVisualization';
import { GameHistory } from './components/GameHistory';
import { AIBattleMode } from './components/AIBattleMode';

function App3D() {
  const { gameState, makeMove, resetGame, isAnimating, animatingPosition } = useConnect4Game3D();
  const [gameMode] = useState<'pvp' | 'pve'>('pvp');
  const [selectedCell, setSelectedCell] = useState<{ x: number; z: number }>({ x: 0, z: 0 });
  const [keyboardMode, setKeyboardMode] = useState(false);

  // Handle mouse hover
  const handleCellHover = useCallback((x: number, z: number) => {
    if (!gameState.winner) {
      setSelectedCell({ x, z });
      setKeyboardMode(false);
    }
  }, [gameState.winner]);

  const handleKeyPress = useCallback((e: KeyboardEvent) => {
    if (gameState.winner || gameState.isDraw || isAnimating) return;

    const { x, z } = selectedCell;
    
    switch(e.key) {
      case 'ArrowUp':
        e.preventDefault();
        if (!gameState.winner) {
          setKeyboardMode(true);
          setSelectedCell({ x, z: Math.max(0, z - 1) });
        }
        break;
      case 'ArrowDown':
        e.preventDefault();
        if (!gameState.winner) {
          setKeyboardMode(true);
          setSelectedCell({ x, z: Math.min(3, z + 1) });
        }
        break;
      case 'ArrowLeft':
        e.preventDefault();
        if (!gameState.winner) {
          setKeyboardMode(true);
          setSelectedCell({ x: Math.max(0, x - 1), z });
        }
        break;
      case 'ArrowRight':
        e.preventDefault();
        if (!gameState.winner) {
          setKeyboardMode(true);
          setSelectedCell({ x: Math.min(3, x + 1), z });
        }
        break;
      case 'Enter':
      case ' ':
        e.preventDefault();
        if (!gameState.winner) {
          makeMove(selectedCell.x, selectedCell.z);
        }
        break;
      case 'Escape':
        e.preventDefault();
        setKeyboardMode(false);
        break;
    }
  }, [selectedCell, makeMove, gameState, isAnimating]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [handleKeyPress]);

  return (
    <div className="App">
      <h1>Connect 4 - 3D Edition (4×4×4)</h1>
      
      <div className="game-info">
        {gameState.winner ? (
          <></>
        ) : gameState.isDraw ? (
          <p className="draw">It's a draw!</p>
        ) : (
          <p className={`current-player ${gameState.currentPlayer}`}>
            Current player: {gameState.currentPlayer.charAt(0).toUpperCase() + gameState.currentPlayer.slice(1)}
          </p>
        )}
      </div>

      <div className="instructions">
        <p>Click on any column to drop a piece. Connect 4 in any direction to win!</p>
        <p className="controls-hint">
          🖱️ Drag to rotate • Scroll to zoom • Right-click drag to pan
        </p>
        <p className="controls-hint">
          ⌨️ Arrow keys to select • Enter/Space to drop • ESC to exit keyboard mode
        </p>
      </div>

      <Board3D_4x4x4 
        gameState={gameState} 
        onCellClick={makeMove}
        onCellHover={handleCellHover}
        isAnimating={isAnimating}
        animatingPosition={animatingPosition}
        selectedCell={selectedCell}
        isKeyboardMode={keyboardMode}
      />

      <LayerVisualization
        board={gameState.board}
        currentPlayer={gameState.currentPlayer}
        selectedCell={selectedCell}
        winner={gameState.winner}
      />

      <div className="game-controls-bottom">
        <button onClick={() => {
          console.log('New Game clicked');
          resetGame();
        }} className="reset-button">
          New Game
        </button>
        <p className="save-info">Game records are automatically saved when finished</p>
      </div>

      <GameHistory />
      <AIBattleMode />
    </div>
  );
}

export default App3D;