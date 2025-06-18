import { useRef } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { Stars, Environment, Float } from '@react-three/drei';
import * as THREE from 'three';

export function SpaceEnvironment() {
  const meshRef = useRef<THREE.Mesh>(null);
  const { scene } = useThree();

  // Set fog for depth
  scene.fog = new THREE.FogExp2(0x60a5fa, 0.01);

  useFrame(({ clock }) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = clock.elapsedTime * 0.05;
    }
  });

  return (
    <>
      {/* Starfield */}
      <Stars 
        radius={100}
        depth={50}
        count={3000}
        factor={4}
        saturation={0}
        fade
        speed={1}
      />

      {/* Floating geometric shapes for depth */}
      {Array.from({ length: 20 }).map((_, i) => {
        const x = (Math.random() - 0.5) * 30;
        const y = (Math.random() - 0.5) * 20;
        const z = -10 - Math.random() * 20;
        const scale = 0.5 + Math.random() * 1.5;
        
        return (
          <Float
            key={i}
            speed={0.5 + Math.random()}
            rotationIntensity={0.5}
            floatIntensity={1}
            floatingRange={[-0.5, 0.5]}
          >
            <mesh position={[x, y, z]} scale={scale}>
              <icosahedronGeometry args={[1, 0]} />
              <meshStandardMaterial
                color="#93c5fd"
                emissive="#60a5fa"
                emissiveIntensity={0.3}
                metalness={0.8}
                roughness={0.2}
                transparent
                opacity={0.4}
              />
            </mesh>
          </Float>
        );
      })}

      {/* Nebula-like clouds */}
      <mesh ref={meshRef} position={[0, 0, -30]} scale={[50, 50, 50]}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshStandardMaterial
          color="#93c5fd"
          emissive="#60a5fa"
          emissiveIntensity={0.3}
          transparent
          opacity={0.08}
          side={THREE.BackSide}
        />
      </mesh>

      {/* Additional ambient lighting for space feel */}
      <ambientLight intensity={0.15} color="#93c5fd" />
      
      {/* Environment preset for reflections */}
      <Environment preset="night" />
    </>
  );
}