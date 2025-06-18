import { useRef, useEffect, useMemo } from 'react';
import { Mesh, Vector3 } from 'three';
import { useFrame } from '@react-three/fiber';
import { Sphere } from '@react-three/drei';
import type { Player, Position3D } from '../types/game3d';

interface GamePieces3DProps {
  board: Player[][][];
  winningPositions: Position3D[];
}

interface AnimatedPiece3DProps {
  position: Vector3;
  color: string;
  isWinning: boolean;
  pieceId: string;
  shouldAnimate: boolean;
}

function AnimatedPiece3D({ position, color, isWinning, pieceId, shouldAnimate }: AnimatedPiece3DProps) {
  const meshRef = useRef<Mesh>(null);
  const startY = position.y + 5; // Start 5 units above target position
  const targetY = position.y;
  const animationStartTime = useRef<number | null>(null);
  const isInitialized = useRef(false);

  useEffect(() => {
    if (!isInitialized.current) {
      isInitialized.current = true;
      
      if (shouldAnimate) {
        // This is a new piece, animate it
        animationStartTime.current = Date.now();
        if (meshRef.current) {
          meshRef.current.position.y = startY;
        }
      } else {
        // This is an existing piece, place it directly
        if (meshRef.current) {
          meshRef.current.position.y = targetY;
        }
      }
    }
  }, [shouldAnimate, targetY, startY]);

  useFrame(() => {
    if (!meshRef.current) return;

    const now = Date.now();
    
    // Handle drop animation
    if (animationStartTime.current !== null) {
      const elapsed = now - animationStartTime.current;
      const duration = 800; // Slightly longer for better visibility
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
        meshRef.current.position.y = targetY;
        animationStartTime.current = null; // Animation complete
      }
    }

    // Winning piece animation
    if (isWinning && animationStartTime.current === null) {
      meshRef.current.rotation.y += 0.05;
      meshRef.current.rotation.x += 0.03;
      const scale = 0.35 + Math.sin(now * 0.005) * 0.05;
      meshRef.current.scale.setScalar(scale);
    }
  });

  // Set initial position
  const initialPos = shouldAnimate ? new Vector3(position.x, startY, position.z) : position;

  return (
    <Sphere ref={meshRef} args={[0.35, 32, 32]} position={initialPos}>
      <meshStandardMaterial 
        color={color} 
        metalness={0.3}
        roughness={0.4}
        emissive={isWinning ? color : undefined}
        emissiveIntensity={isWinning ? 0.3 : 0}
      />
    </Sphere>
  );
}

export function GamePieces3D({ board, winningPositions }: GamePieces3DProps) {
  const SIZE = 4;
  const CELL_SIZE = 1;
  const GAP = 0.1;

  // Track which pieces existed in the previous render
  const previousPiecesRef = useRef<Set<string>>(new Set());
  
  // Create pieces array
  const pieces = useMemo(() => {
    const piecesArray: JSX.Element[] = [];
    const currentPieces = new Set<string>();

    // First, collect all current pieces
    board.forEach((plane, x) => {
      plane.forEach((row, y) => {
        row.forEach((cell, z) => {
          if (cell) {
            const pieceId = `${x}-${y}-${z}`;
            currentPieces.add(pieceId);
          }
        });
      });
    });

    // Now create the piece components
    board.forEach((plane, x) => {
      plane.forEach((row, y) => {
        row.forEach((cell, z) => {
          if (cell) {
            const posX = x * (CELL_SIZE + GAP);
            const posY = y * (CELL_SIZE + GAP);
            const posZ = z * (CELL_SIZE + GAP);
            
            const isWinning = winningPositions.some(
              pos => pos.x === x && pos.y === y && pos.z === z
            );

            // Simple key without color to track position only
            const pieceId = `${x}-${y}-${z}`;
            
            // Check if this piece is new (not in previous render)
            const shouldAnimate = !previousPiecesRef.current.has(pieceId);

            piecesArray.push(
              <AnimatedPiece3D
                key={`${pieceId}-${cell}`} // Include color in key for proper React reconciliation
                pieceId={pieceId}
                position={new Vector3(posX, posY, posZ)}
                color={cell === 'yellow' ? '#facc15' : '#ef4444'}
                isWinning={isWinning}
                shouldAnimate={shouldAnimate}
              />
            );
          }
        });
      });
    });

    // Update the previous pieces set for next render
    previousPiecesRef.current = currentPieces;
    
    return piecesArray;
  }, [board, winningPositions, CELL_SIZE, GAP]);

  return <>{pieces}</>;
}