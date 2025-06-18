import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import type { GameState3D } from '../types/game3d';
import { BoardGrid3D } from './BoardGrid3D';
import { GamePieces3D } from './GamePieces3D';
import { Lighting } from './Lighting';
import { WinningLine3D } from './WinningLine3D';
import { VictoryEffects } from './VictoryEffects';
import { SpaceEnvironment } from './SpaceEnvironment';

interface Board3D_4x4x4Props {
  gameState: GameState3D;
  onCellClick: (x: number, z: number) => void;
  onCellHover: (x: number, z: number) => void;
  isAnimating: boolean;
  animatingPosition?: { x: number; z: number } | null;
  selectedCell: { x: number; z: number };
  isKeyboardMode: boolean;
}

export function Board3D_4x4x4({ gameState, onCellClick, onCellHover, isAnimating, animatingPosition, selectedCell, isKeyboardMode }: Board3D_4x4x4Props) {
  return (
    <div style={{ width: '100%', height: '80vh', minHeight: '600px', position: 'relative' }}>
      <Canvas shadows>
        <PerspectiveCamera makeDefault position={[10, 10, 10]} fov={60} />
        <OrbitControls 
          enablePan={true} 
          enableZoom={true}
          enableRotate={true}
          minDistance={8} 
          maxDistance={25}
          target={[1.5, 1.5, 1.5]}
          autoRotate={false}
          autoRotateSpeed={2}
          rotateSpeed={0.8}
          zoomSpeed={1}
          panSpeed={0.8}
          minPolarAngle={Math.PI / 6}
          maxPolarAngle={Math.PI / 2.2}
        />
        
        {/* Space environment */}
        <SpaceEnvironment />
        
        <Lighting />
        <BoardGrid3D 
          onCellClick={onCellClick}
          onCellHover={onCellHover}
          isAnimating={isAnimating}
          animatingPosition={animatingPosition}
          board={gameState.board}
          currentPlayer={gameState.currentPlayer}
          selectedCell={selectedCell}
          isKeyboardMode={isKeyboardMode}
          hasWinner={!!gameState.winner}
        />
        <GamePieces3D board={gameState.board} winningPositions={gameState.winningPositions} />
        
        {/* Winning line and effects */}
        {gameState.winner && gameState.winningPositions.length > 0 && (
          <>
            <WinningLine3D 
              winningPositions={gameState.winningPositions}
              color={gameState.winner === 'yellow' ? '#facc15' : '#ef4444'}
            />
            <VictoryEffects winner={gameState.winner} />
          </>
        )}
      </Canvas>
    </div>
  );
}