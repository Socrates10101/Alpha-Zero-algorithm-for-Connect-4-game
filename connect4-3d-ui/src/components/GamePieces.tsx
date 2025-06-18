import { useRef, useEffect } from 'react';
import { Mesh, Vector3 } from 'three';
import { useFrame } from '@react-three/fiber';
import type { Player, BoardPosition } from '../types/game';

interface GamePiecesProps {
  board: Player[][];
  winningPositions: BoardPosition[];
}

interface AnimatedPieceProps {
  position: Vector3;
  color: string;
  isWinning: boolean;
  delay: number;
}

function AnimatedPiece({ position, color, isWinning, delay }: AnimatedPieceProps) {
  const meshRef = useRef<Mesh>(null);
  const startY = 8;
  const targetY = position.y;
  const animationStartTime = useRef(0);
  const isAnimating = useRef(true);

  useEffect(() => {
    animationStartTime.current = Date.now() + delay;
    isAnimating.current = true;
  }, [position, delay]);

  useFrame(() => {
    if (!meshRef.current) return;

    const now = Date.now();
    
    // Handle drop animation
    if (isAnimating.current) {
      const elapsed = now - animationStartTime.current;
      
      if (elapsed < 0) {
        meshRef.current.position.y = startY;
        return;
      }

      const duration = 600;
      const progress = Math.min(elapsed / duration, 1);
      
      // Bounce effect
      const easeOutBounce = (t: number) => {
        if (t < 1 / 2.75) {
          return 7.5625 * t * t;
        } else if (t < 2 / 2.75) {
          t -= 1.5 / 2.75;
          return 7.5625 * t * t + 0.75;
        } else if (t < 2.5 / 2.75) {
          t -= 2.25 / 2.75;
          return 7.5625 * t * t + 0.9375;
        } else {
          t -= 2.625 / 2.75;
          return 7.5625 * t * t + 0.984375;
        }
      };

      meshRef.current.position.y = startY + (targetY - startY) * easeOutBounce(progress);

      if (progress >= 1) {
        meshRef.current.position.y = targetY; // Ensure final position
        isAnimating.current = false;
      }
    }

    // Winning piece animation
    if (isWinning && !isAnimating.current) {
      meshRef.current.rotation.y += 0.05;
      meshRef.current.scale.setScalar(1 + Math.sin(now * 0.005) * 0.1);
    }
  });

  return (
    <mesh ref={meshRef} position={position}>
      <cylinderGeometry args={[0.35, 0.35, 0.4, 32]} />
      <meshStandardMaterial 
        color={color} 
        emissive={isWinning ? color : undefined}
        emissiveIntensity={isWinning ? 0.3 : 0}
      />
    </mesh>
  );
}

export function GamePieces({ board, winningPositions }: GamePiecesProps) {
  const columns = 7;
  const rows = 6;
  const cellSize = 1;

  const pieces: JSX.Element[] = [];
  let pieceIndex = 0;

  board.forEach((column, colIndex) => {
    column.forEach((cell, rowIndex) => {
      if (cell) {
        const x = (colIndex - columns / 2 + 0.5) * cellSize;
        const y = (rowIndex - rows / 2 + 0.5) * cellSize;
        const z = 0;
        
        const isWinning = winningPositions.some(
          pos => pos.column === colIndex && pos.row === rowIndex
        );

        pieces.push(
          <AnimatedPiece
            key={`${colIndex}-${rowIndex}`}
            position={new Vector3(x, y, z)}
            color={cell === 'yellow' ? '#facc15' : '#ef4444'}
            isWinning={isWinning}
            delay={0}
          />
        );
        pieceIndex++;
      }
    });
  });

  return <>{pieces}</>;
}