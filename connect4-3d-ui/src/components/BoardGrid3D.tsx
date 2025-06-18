import { Box } from '@react-three/drei';
import type { Player } from '../types/game3d';
import { GhostPiece } from './GhostPiece';

interface BoardGrid3DProps {
  onCellClick: (x: number, z: number) => void;
  onCellHover: (x: number, z: number) => void;
  isAnimating: boolean;
  animatingPosition?: { x: number; z: number } | null;
  board?: Player[][][];
  currentPlayer?: Player;
  selectedCell: { x: number; z: number };
  isKeyboardMode: boolean;
  hasWinner?: boolean;
}

export function BoardGrid3D({ onCellClick, onCellHover, isAnimating, animatingPosition, board, currentPlayer, selectedCell, isKeyboardMode, hasWinner }: BoardGrid3DProps) {
  const SIZE = 4;
  const CELL_SIZE = 1;
  const GAP = 0.1;

  // Find the next available Y position for a given X, Z
  const getNextY = (x: number, z: number): number | null => {
    if (!board) return 0;
    for (let y = 0; y < SIZE; y++) {
      if (board[x][y][z] === null) {
        return y;
      }
    }
    return null;
  };

  return (
    <group>
      {/* Create the 3D grid structure */}
      {Array.from({ length: SIZE }).map((_, x) =>
        Array.from({ length: SIZE }).map((_, z) => {
          const posX = x * (CELL_SIZE + GAP);
          const posZ = z * (CELL_SIZE + GAP);
          const isSelected = selectedCell.x === x && selectedCell.z === z;

          return (
            <group key={`${x}-${z}`}>
              {/* Vertical pillars for the grid - glass-like */}
              <Box
                position={[posX, 1.5, posZ]}
                args={[0.1, 4, 0.1]}
              >
                <meshPhysicalMaterial 
                  color="#60a5fa"
                  metalness={0.8}
                  roughness={0.2}
                  transparent
                  opacity={0.6}
                  emissive="#3b82f6"
                  emissiveIntensity={0.1}
                />
              </Box>

              {/* Horizontal connections between pillars */}
              {Array.from({ length: SIZE }).map((_, y) => (
                <group key={`horizontal-${x}-${y}-${z}`}>
                  {/* X direction */}
                  {x < SIZE - 1 && (
                    <Box
                      position={[posX + (CELL_SIZE + GAP) / 2, y * (CELL_SIZE + GAP), posZ]}
                      args={[CELL_SIZE + GAP, 0.05, 0.05]}
                    >
                      <meshPhysicalMaterial 
                        color="#60a5fa"
                        metalness={0.8}
                        roughness={0.2}
                        transparent
                        opacity={0.4}
                        emissive="#3b82f6"
                        emissiveIntensity={0.05}
                      />
                    </Box>
                  )}
                  {/* Z direction */}
                  {z < SIZE - 1 && (
                    <Box
                      position={[posX, y * (CELL_SIZE + GAP), posZ + (CELL_SIZE + GAP) / 2]}
                      args={[0.05, 0.05, CELL_SIZE + GAP]}
                    >
                      <meshPhysicalMaterial 
                        color="#60a5fa"
                        metalness={0.8}
                        roughness={0.2}
                        transparent
                        opacity={0.4}
                        emissive="#3b82f6"
                        emissiveIntensity={0.05}
                      />
                    </Box>
                  )}
                </group>
              ))}

              {/* Larger invisible click/hover area for better detection */}
              <mesh
                position={[posX, 2, posZ]}
                visible={false}
                onClick={(e) => {
                  e.stopPropagation();
                  if (!isAnimating && !hasWinner) onCellClick(x, z);
                }}
                onPointerEnter={(e) => {
                  e.stopPropagation();
                  if (!hasWinner) onCellHover(x, z);
                }}
                onPointerMove={(e) => {
                  e.stopPropagation();
                  if (!hasWinner && (selectedCell.x !== x || selectedCell.z !== z)) {
                    onCellHover(x, z);
                  }
                }}
              >
                <boxGeometry args={[CELL_SIZE + GAP * 2, 6, CELL_SIZE + GAP * 2]} />
              </mesh>

              {/* Visual feedback for selected column (not when game has winner) */}
              {isSelected && !hasWinner && (
                <Box
                  position={[posX, 2, posZ]}
                  args={[CELL_SIZE * 0.9, 4.5, CELL_SIZE * 0.9]}
                >
                  <meshStandardMaterial 
                    color={isKeyboardMode ? "#f59e0b" : "#60a5fa"} 
                    opacity={0.15} 
                    transparent 
                    emissive={isKeyboardMode ? "#f59e0b" : "#60a5fa"}
                    emissiveIntensity={0.2}
                  />
                </Box>
              )}

              {/* Selection indicator - show ghost piece at drop position (not when game has winner) */}
              {isSelected && !hasWinner && board && currentPlayer && (
                (() => {
                  // Only hide ghost piece if this specific column is animating
                  const isThisColumnAnimating = isAnimating && animatingPosition && 
                    animatingPosition.x === x && animatingPosition.z === z;
                  
                  if (isThisColumnAnimating) {
                    return null;
                  }
                  
                  const nextY = getNextY(x, z);
                  if (nextY !== null) {
                    const ghostPosition = [posX, nextY * (CELL_SIZE + GAP), posZ];
                    console.log('Ghost piece position calculated:', {
                      gridCoordinates: { x, y: nextY, z },
                      worldPosition: { x: ghostPosition[0], y: ghostPosition[1], z: ghostPosition[2] },
                      cellSize: CELL_SIZE,
                      gap: GAP,
                      calculation: `y = ${nextY} * (${CELL_SIZE} + ${GAP}) = ${nextY * (CELL_SIZE + GAP)}`
                    });
                    return (
                      <GhostPiece
                        position={ghostPosition as [number, number, number]}
                        color={currentPlayer === 'yellow' ? '#facc15' : '#ef4444'}
                        isKeyboardSelected={isKeyboardMode}
                      />
                    );
                  }
                  return null;
                })()
              )}
            </group>
          );
        })
      )}

      {/* Base platform - transparent glass-like */}
      <Box position={[1.5, -0.25, 1.5]} args={[5, 0.5, 5]}>
        <meshPhysicalMaterial 
          color="#1e3a8a"
          metalness={0.9}
          roughness={0.1}
          transparent
          opacity={0.3}
          transmission={0.5}
          thickness={0.5}
          envMapIntensity={1}
        />
      </Box>
      
      {/* Glass floor reflection */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[1.5, -0.51, 1.5]} receiveShadow>
        <planeGeometry args={[10, 10]} />
        <meshStandardMaterial
          color="#1e40af"
          metalness={0.9}
          roughness={0.1}
          transparent
          opacity={0.15}
        />
      </mesh>
    </group>
  );
}