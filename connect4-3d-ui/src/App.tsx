import './App.css';
import { useState } from 'react';
import { Board3D } from './components/Board3D';
import { useConnect4Game } from './hooks/useConnect4Game';
import { useAIPlayer } from './hooks/useAIPlayer';

function App() {
  const { gameState, makeMove, resetGame, isAnimating } = useConnect4Game();
  const [gameMode, setGameMode] = useState<'pvp' | 'pve'>('pvp');
  const [aiPlayer, setAiPlayer] = useState<'yellow' | 'red'>('red');
  
  const { isThinking } = useAIPlayer(gameState, makeMove, {
    enabled: gameMode === 'pve',
    aiPlayer
  });

  return (
    <div className="App">
      <div className="title-container">
        <h1 data-text="CONNECT 4 3D">CONNECT 4 3D</h1>
      </div>
      
      <div className="game-controls">
        <div className="mode-selector">
          <label>
            <input
              type="radio"
              value="pvp"
              checked={gameMode === 'pvp'}
              onChange={(e) => {
                setGameMode(e.target.value as 'pvp' | 'pve');
                resetGame();
              }}
            />
            Player vs Player
          </label>
          <label>
            <input
              type="radio"
              value="pve"
              checked={gameMode === 'pve'}
              onChange={(e) => {
                setGameMode(e.target.value as 'pvp' | 'pve');
                resetGame();
              }}
            />
            Player vs AI
          </label>
        </div>
        {gameMode === 'pve' && (
          <div className="ai-selector">
            <label>AI plays as: </label>
            <select value={aiPlayer} onChange={(e) => {
              setAiPlayer(e.target.value as 'yellow' | 'red');
              resetGame();
            }}>
              <option value="yellow">Yellow (First)</option>
              <option value="red">Red (Second)</option>
            </select>
          </div>
        )}
      </div>
      
      <div className="game-info">
        {gameState.winner ? (
          <p className={`winner ${gameState.winner}`}>
            {gameState.winner.charAt(0).toUpperCase() + gameState.winner.slice(1)} wins!
          </p>
        ) : gameState.isDraw ? (
          <p className="draw">It's a draw!</p>
        ) : (
          <p className={`current-player ${gameState.currentPlayer}`}>
            {isThinking ? (
              <>AI is thinking...</>
            ) : (
              <>Current player: {gameState.currentPlayer.charAt(0).toUpperCase() + gameState.currentPlayer.slice(1)}</>
            )}
          </p>
        )}
      </div>

      <Board3D 
        gameState={gameState} 
        onColumnClick={makeMove}
        isAnimating={isAnimating || isThinking}
      />

      <button onClick={() => {
        console.log('New Game clicked');
        resetGame();
      }} className="reset-button">
        New Game
      </button>
    </div>
  );
}

export default App;
