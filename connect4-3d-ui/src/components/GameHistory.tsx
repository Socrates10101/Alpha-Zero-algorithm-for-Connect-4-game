import { useState } from 'react';
import { gameRecorder } from '../utils/gameRecorder';
import { GameReplay } from './GameReplay';
import type { GameRecord } from '../utils/gameRecorder';
import './GameHistory.css';

export function GameHistory() {
  const [showHistory, setShowHistory] = useState(false);
  const [replayingGame, setReplayingGame] = useState<GameRecord | null>(null);
  const games = gameRecorder.getAllGames();

  const handleExportPython = (gameId: string) => {
    const pythonCode = gameRecorder.exportGameAsPython(gameId);
    if (pythonCode) {
      const blob = new Blob([pythonCode], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `connect4_3d_${gameId}.py`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  const handleExportAllJson = () => {
    const jsonData = gameRecorder.exportAllGamesAsJson();
    const blob = new Blob([jsonData], { type: 'application/json;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `connect4_3d_all_games_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <>
      <button
        className="history-toggle"
        onClick={() => setShowHistory(!showHistory)}
      >
        Game History ({games.length})
      </button>

      {showHistory && (
        <div className="game-history-panel">
          <div className="history-header">
            <h3>Game History</h3>
            <button className="close-btn" onClick={() => setShowHistory(false)}>×</button>
          </div>

          <div className="history-content">
            {games.length === 0 ? (
              <p className="no-games">No games recorded yet</p>
            ) : (
              <>
                <div className="export-actions">
                  <button onClick={handleExportAllJson} className="export-all-btn">
                    Export All as JSON
                  </button>
                </div>

                <div className="games-list">
                  {games.map((game) => (
                    <div key={game.gameId} className="game-item">
                      <div 
                        className="game-info clickable"
                        onClick={() => setReplayingGame(game)}
                        title="Click to replay game"
                      >
                        <div className="game-date">
                          {new Date(game.startTime).toLocaleString()}
                        </div>
                        <div className="game-details">
                          <span className={`winner ${game.winner}`}>
                            {game.winner ? `${game.winner.toUpperCase()} wins` : 'Draw'}
                          </span>
                          <span className="moves-count">{game.totalMoves} moves</span>
                        </div>
                      </div>
                      <div className="game-actions">
                        <button
                          onClick={() => setReplayingGame(game)}
                          className="replay-btn"
                          title="Replay game"
                        >
                          ▶ Replay
                        </button>
                        <button
                          onClick={() => handleExportPython(game.gameId)}
                          className="export-btn"
                          title="Export as Python"
                        >
                          Export
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      )}
      
      {replayingGame && (
        <GameReplay
          gameRecord={replayingGame}
          onClose={() => setReplayingGame(null)}
        />
      )}
    </>
  );
}