import { useState } from 'react';
import { gameRecorder } from '../utils/gameRecorder';
import { AIBattleView } from './AIBattleView';
import type { GameRecord } from '../utils/gameRecorder';
import './AIBattleMode.css';

export function AIBattleMode() {
  const [showBattleList, setShowBattleList] = useState(false);
  const [battleViewGame, setBattleViewGame] = useState<GameRecord | null>(null);
  const games = gameRecorder.getAllGames();
  
  // Filter games for AI battles (you can add custom filtering logic here)
  const aiBattles = games.filter(game => game.totalMoves > 0);

  return (
    <>
      <button
        className="ai-battle-mode-btn"
        onClick={() => setShowBattleList(!showBattleList)}
        title="AI Battle Mode"
      >
        ⚔️ AI Battle Mode
      </button>

      {showBattleList && (
        <div className="ai-battle-list-panel">
          <div className="battle-list-header">
            <h3>AI Battle Replays</h3>
            <button className="close-btn" onClick={() => setShowBattleList(false)}>×</button>
          </div>

          <div className="battle-list-content">
            {aiBattles.length === 0 ? (
              <p className="no-battles">No battles available</p>
            ) : (
              <div className="battles-grid">
                {aiBattles.map((game) => (
                  <div
                    key={game.gameId}
                    className="battle-card"
                    onClick={() => {
                      setBattleViewGame(game);
                      setShowBattleList(false);
                    }}
                  >
                    <div className="battle-card-header">
                      <span className={`battle-winner ${game.winner}`}>
                        {game.winner ? `${game.winner.toUpperCase()} WINS` : 'DRAW'}
                      </span>
                    </div>
                    <div className="battle-card-stats">
                      <div className="stat">
                        <span className="stat-label">Moves</span>
                        <span className="stat-value">{game.totalMoves}</span>
                      </div>
                      <div className="stat">
                        <span className="stat-label">Date</span>
                        <span className="stat-value">
                          {new Date(game.startTime).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                    <div className="battle-card-footer">
                      <button className="watch-battle-btn">
                        Watch Battle →
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
      
      {battleViewGame && (
        <AIBattleView
          gameRecord={battleViewGame}
          onClose={() => setBattleViewGame(null)}
        />
      )}
    </>
  );
}