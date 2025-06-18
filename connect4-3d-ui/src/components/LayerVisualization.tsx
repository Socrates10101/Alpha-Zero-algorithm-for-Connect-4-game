import type { Player } from '../types/game3d';
import './LayerVisualization.css';

interface LayerVisualizationProps {
  board: Player[][][];
  currentPlayer: Player;
  selectedCell: { x: number; z: number };
  winner: Player | null;
}

export function LayerVisualization({ board, currentPlayer, selectedCell, winner }: LayerVisualizationProps) {
  const SIZE = 4;

  // Get the next available Y position for a given X, Z
  const getNextY = (x: number, z: number): number | null => {
    for (let y = 0; y < SIZE; y++) {
      if (board[x][y][z] === null) {
        return y;
      }
    }
    return null;
  };

  return (
    <div className="layer-visualization">
      <h3>Layer View</h3>
      <div className="layers-container">
        {Array.from({ length: SIZE }).map((_, y) => (
          <div key={y} className="layer" data-layer={y}>
            <div className="layer-label">Layer {y + 1}</div>
            <div className="layer-grid">
              {Array.from({ length: SIZE }).map((_, z) => (
                <div key={z} className="layer-row">
                  {Array.from({ length: SIZE }).map((_, x) => {
                    const piece = board[x][y][z];
                    const isSelected = selectedCell.x === x && selectedCell.z === z;
                    const nextY = getNextY(x, z);
                    const isNextPosition = nextY === y && isSelected && !winner;
                    
                    return (
                      <div
                        key={x}
                        className={`cell ${piece || ''} ${isSelected ? 'selected' : ''} ${isNextPosition ? 'next-position' : ''}`}
                        data-x={x}
                        data-y={y}
                        data-z={z}
                      >
                        {piece && (
                          <div className={`piece ${piece}`} />
                        )}
                        {isNextPosition && (
                          <div className={`ghost-piece ${currentPlayer}`} />
                        )}
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      <div className="legend">
        <div className="legend-item">
          <div className="piece yellow small" />
          <span>Yellow</span>
        </div>
        <div className="legend-item">
          <div className="piece red small" />
          <span>Red</span>
        </div>
        <div className="legend-item">
          <div className="ghost-piece-indicator" />
          <span>Next Drop</span>
        </div>
      </div>
    </div>
  );
}