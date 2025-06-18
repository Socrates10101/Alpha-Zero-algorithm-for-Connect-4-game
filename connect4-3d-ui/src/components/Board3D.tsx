import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import type { GameState } from '../types/game';
import { BoardGrid } from './BoardGrid';
import { GamePieces } from './GamePieces';
import { Lighting } from './Lighting';

interface Board3DProps {
  gameState: GameState;
  onColumnClick: (column: number) => void;
  isAnimating: boolean;
}

export function Board3D({ gameState, onColumnClick, isAnimating }: Board3DProps) {
  return (
    <div style={{ width: '100%', height: '600px' }}>
      <Canvas>
        <PerspectiveCamera makeDefault position={[0, 5, 10]} />
        <OrbitControls 
          enablePan={false} 
          minDistance={8} 
          maxDistance={20}
          maxPolarAngle={Math.PI / 2.5}
        />
        <Lighting />
        <BoardGrid onColumnClick={onColumnClick} isAnimating={isAnimating} />
        <GamePieces board={gameState.board} winningPositions={gameState.winningPositions} />
      </Canvas>
    </div>
  );
}