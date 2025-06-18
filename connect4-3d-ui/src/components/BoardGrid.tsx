import { useRef, useState } from 'react';
import { Mesh } from 'three';
import { useFrame } from '@react-three/fiber';

interface BoardGridProps {
  onColumnClick: (column: number) => void;
  isAnimating: boolean;
}

export function BoardGrid({ onColumnClick, isAnimating }: BoardGridProps) {
  const groupRef = useRef<Mesh>(null);
  const [hoveredColumn, setHoveredColumn] = useState<number | null>(null);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.1) * 0.02;
    }
  });

  const columns = 7;
  const rows = 6;
  const cellSize = 1;
  const gap = 0.1;

  return (
    <group ref={groupRef}>
      {/* Board Base */}
      <mesh position={[0, -0.5, 0]}>
        <boxGeometry args={[columns * cellSize + gap * 2, 0.5, rows * cellSize + gap * 2]} />
        <meshStandardMaterial color="#1e3a8a" />
      </mesh>

      {/* Grid Holes */}
      {Array.from({ length: columns }).map((_, col) =>
        Array.from({ length: rows }).map((_, row) => {
          const x = (col - columns / 2 + 0.5) * cellSize;
          const y = (row - rows / 2 + 0.5) * cellSize;
          const z = 0;

          return (
            <group key={`${col}-${row}`} position={[x, y, z]}>
              {/* Hole */}
              <mesh>
                <cylinderGeometry args={[0.4, 0.4, 0.5, 32]} />
                <meshStandardMaterial color="#0f172a" />
              </mesh>
              {/* Click area for column */}
              {row === 0 && (
                <mesh
                  position={[0, rows * cellSize / 2, 0]}
                  visible={false}
                  onClick={() => !isAnimating && onColumnClick(col)}
                  onPointerEnter={() => setHoveredColumn(col)}
                  onPointerLeave={() => setHoveredColumn(null)}
                >
                  <boxGeometry args={[cellSize, rows * cellSize, 1]} />
                </mesh>
              )}
            </group>
          );
        })
      )}

      {/* Hover indicator */}
      {hoveredColumn !== null && !isAnimating && (
        <mesh position={[(hoveredColumn - columns / 2 + 0.5) * cellSize, rows * cellSize / 2 + 1, 0]}>
          <cylinderGeometry args={[0.35, 0.35, 0.1, 32]} />
          <meshStandardMaterial color="#60a5fa" opacity={0.5} transparent />
        </mesh>
      )}
    </group>
  );
}