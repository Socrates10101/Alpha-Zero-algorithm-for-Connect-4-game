import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Text } from '@react-three/drei';
import * as THREE from 'three';
import type { Player } from '../types/game3d';

interface AIBattleVictoryEffectsProps {
  winner: Player;
}

export function AIBattleVictoryEffects({ winner }: AIBattleVictoryEffectsProps) {
  const groupRef = useRef<THREE.Group>(null);
  const startTime = useRef(Date.now());

  const winnerColor = winner === 'yellow' ? '#facc15' : '#ef4444';
  const winnerText = winner === 'yellow' ? 'YELLOW' : 'RED';

  useFrame(() => {
    if (!groupRef.current) return;

    const elapsed = (Date.now() - startTime.current) / 1000;
    
    // Simple fade in
    const fadeIn = Math.min(elapsed / 0.3, 1);
    groupRef.current.opacity = fadeIn;
  });

  return (
    <group ref={groupRef} position={[1.5, 4, 1.5]}>
      {/* Simple winner text */}
      <Text
        fontSize={0.6}
        anchorX="center"
        anchorY="middle"
        letterSpacing={0.15}
      >
        {winnerText}
        <meshBasicMaterial 
          color="#000000"
          transparent
          opacity={0.9}
        />
      </Text>
      
      {/* Subtitle */}
      <Text
        fontSize={0.3}
        anchorX="center"
        anchorY="middle"
        position={[0, -0.5, 0]}
      >
        WINNER
        <meshBasicMaterial 
          color="#000000"
          transparent
          opacity={0.7}
        />
      </Text>
      
      {/* Simple underline */}
      <mesh position={[0, -0.7, 0]}>
        <planeGeometry args={[2, 0.02]} />
        <meshBasicMaterial
          color={winnerColor}
          transparent
          opacity={0.8}
        />
      </mesh>
    </group>
  );
}