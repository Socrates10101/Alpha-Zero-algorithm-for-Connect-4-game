import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface GhostPieceProps {
  position: [number, number, number];
  color: string;
  isKeyboardSelected?: boolean;
}

export function GhostPiece({ position, color, isKeyboardSelected = false }: GhostPieceProps) {
  const groupRef = useRef<THREE.Group>(null);
  
  useFrame(({ clock }) => {
    if (!groupRef.current) return;
    
    const time = clock.getElapsedTime();
    
    if (isKeyboardSelected) {
      // Keyboard mode - larger bounce
      const bounce = Math.sin(time * 3) * 0.15;
      groupRef.current.position.y = position[1] + bounce;
      groupRef.current.rotation.y = time * 2;
    } else {
      // Mouse hover mode - subtle bounce
      const bounce = Math.abs(Math.sin(time * 4)) * 0.05;
      groupRef.current.position.y = position[1] + bounce;
      groupRef.current.rotation.y = time;
    }
  });

  return (
    <group ref={groupRef} position={[position[0], position[1], position[2]]}>
      {/* Main ghost piece - wireframe style */}
      <mesh>
        <sphereGeometry args={[0.35, 16, 16]} />
        <meshBasicMaterial 
          color={color}
          wireframe={true}
          opacity={0.8} 
          transparent={true}
        />
      </mesh>
      
      {/* Inner solid piece */}
      <mesh>
        <sphereGeometry args={[0.33, 32, 32]} />
        <meshStandardMaterial 
          color={color}
          opacity={0.3} 
          transparent={true}
          emissive={color}
          emissiveIntensity={0.2}
        />
      </mesh>
      
      {/* Position ring on ground */}
      <mesh position={[0, -position[1], 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.35, 0.42, 32]} />
        <meshStandardMaterial 
          color={color}
          emissive={color}
          emissiveIntensity={0.8}
        />
      </mesh>
      
      {/* Inner ring */}
      <mesh position={[0, -position[1] + 0.01, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.25, 0.32, 32]} />
        <meshBasicMaterial 
          color={color}
          opacity={0.6}
          transparent={true}
        />
      </mesh>
    </group>
  );
}