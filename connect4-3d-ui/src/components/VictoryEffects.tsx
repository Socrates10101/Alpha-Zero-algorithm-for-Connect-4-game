import { useRef, useMemo, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { Text, Float } from '@react-three/drei';
import * as THREE from 'three';
import type { Player } from '../types/game3d';
import { ExplosionEffect } from './ExplosionEffect';

interface VictoryEffectsProps {
  winner: Player;
}

export function VictoryEffects({ winner }: VictoryEffectsProps) {
  const groupRef = useRef<THREE.Group>(null);
  const ringRef = useRef<THREE.Mesh>(null);
  const ring2Ref = useRef<THREE.Mesh>(null);
  const particlesRef = useRef<THREE.Points>(null);
  const textRef = useRef<THREE.Mesh>(null);
  const startTime = useRef(Date.now());
  const [showExplosion, setShowExplosion] = useState(true);

  const winnerColor = winner === 'yellow' ? '#facc15' : '#ef4444';
  const winnerText = winner === 'yellow' ? 'YELLOW WINS' : 'RED WINS';
  const accentColor = winner === 'yellow' ? '#fef3c7' : '#fecaca';

  // Hide explosion after 2 seconds
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowExplosion(false);
    }, 2000);
    return () => clearTimeout(timer);
  }, []);

  // Create particle geometry with spiral pattern
  const particles = useMemo(() => {
    const count = 300;
    const positions = new Float32Array(count * 3);
    const scales = new Float32Array(count);
    const velocities = new Float32Array(count * 3);
    
    for (let i = 0; i < count; i++) {
      const t = i / count;
      const theta = t * Math.PI * 8; // Spiral
      const phi = t * Math.PI;
      const radius = 2 + t * 3;
      
      positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = radius * Math.cos(phi) * 0.5;
      positions[i * 3 + 2] = radius * Math.sin(phi) * Math.sin(theta);
      
      scales[i] = (1 - t) * 0.8;
      
      // Velocity for particle movement
      velocities[i * 3] = (Math.random() - 0.5) * 0.02;
      velocities[i * 3 + 1] = Math.random() * 0.02;
      velocities[i * 3 + 2] = (Math.random() - 0.5) * 0.02;
    }
    
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('scale', new THREE.BufferAttribute(scales, 1));
    geometry.setAttribute('velocity', new THREE.BufferAttribute(velocities, 3));
    
    return geometry;
  }, []);

  useFrame(({ clock }) => {
    if (!groupRef.current) return;

    const elapsed = (Date.now() - startTime.current) / 1000;
    
    // Delay main effects until after explosion (0.3s delay)
    const delayedElapsed = Math.max(0, elapsed - 0.3);
    
    // Smooth entrance with bounce
    const entranceProgress = Math.min(delayedElapsed / 1.5, 1);
    const easeOutElastic = (t: number) => {
      const c4 = (2 * Math.PI) / 3;
      return t === 0 ? 0 : t === 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
    };
    const scale = easeOutElastic(entranceProgress);
    
    groupRef.current.scale.setScalar(scale);
    groupRef.current.rotation.y = elapsed * 0.05;

    // Text pulsing (after delay)
    if (textRef.current && delayedElapsed > 0) {
      const textPulse = 1 + Math.sin(delayedElapsed * 3) * 0.05;
      textRef.current.scale.setScalar(textPulse);
    }

    // Ring animations
    if (ringRef.current) {
      ringRef.current.rotation.z = elapsed * 0.3;
      const ringPulse = 1 + Math.sin(elapsed * 2) * 0.08;
      ringRef.current.scale.x = ringPulse;
      ringRef.current.scale.y = ringPulse;
    }

    if (ring2Ref.current) {
      ring2Ref.current.rotation.z = -elapsed * 0.2;
      ring2Ref.current.rotation.x = Math.sin(elapsed * 0.5) * 0.1;
    }

    // Particle animation with flow
    if (particlesRef.current && particlesRef.current.geometry.attributes.position) {
      const positions = particlesRef.current.geometry.attributes.position;
      const velocities = particlesRef.current.geometry.attributes.velocity;
      
      for (let i = 0; i < positions.count; i++) {
        positions.array[i * 3] += velocities.array[i * 3];
        positions.array[i * 3 + 1] += velocities.array[i * 3 + 1];
        positions.array[i * 3 + 2] += velocities.array[i * 3 + 2];
        
        // Reset particles that go too far
        const dist = Math.sqrt(
          positions.array[i * 3] ** 2 + 
          positions.array[i * 3 + 1] ** 2 + 
          positions.array[i * 3 + 2] ** 2
        );
        if (dist > 8) {
          const t = i / positions.count;
          const theta = t * Math.PI * 8;
          const phi = t * Math.PI;
          const radius = 2;
          
          positions.array[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
          positions.array[i * 3 + 1] = radius * Math.cos(phi) * 0.5;
          positions.array[i * 3 + 2] = radius * Math.sin(phi) * Math.sin(theta);
        }
      }
      
      positions.needsUpdate = true;
      particlesRef.current.rotation.y = elapsed * 0.1;
    }
  });

  return (
    <>
      {/* Explosion effect at the start */}
      {showExplosion && (
        <>
          <ExplosionEffect 
            position={[1.5, 2, 1.5]} 
            color={winnerColor} 
            delay={0}
          />
          <ExplosionEffect 
            position={[0.5, 3, 0.5]} 
            color={accentColor} 
            delay={0.1}
          />
          <ExplosionEffect 
            position={[2.5, 3, 2.5]} 
            color={accentColor} 
            delay={0.1}
          />
          <ExplosionEffect 
            position={[1.5, 4, 1.5]} 
            color={winnerColor} 
            delay={0.2}
          />
        </>
      )}
      
      <group ref={groupRef} position={[1.5, 5, 1.5]}>
      {/* Main text with premium material */}
      <Float
        speed={0.5}
        rotationIntensity={0.05}
        floatIntensity={0.3}
      >
        <Text
          ref={textRef}
          fontSize={1.2}
          anchorX="center"
          anchorY="middle"
          letterSpacing={0.15}
        >
          {winnerText}
          <meshPhysicalMaterial
            color={accentColor}
            emissive={winnerColor}
            emissiveIntensity={1.2}
            metalness={0.95}
            roughness={0.05}
            clearcoat={1}
            clearcoatRoughness={0}
            reflectivity={1}
            envMapIntensity={2}
            iridescence={1}
            iridescenceIOR={1.5}
            transmission={0.1}
            thickness={0.5}
          />
        </Text>
      </Float>

      {/* Primary elegant ring */}
      <mesh ref={ringRef} rotation={[Math.PI / 2, 0, 0]} position={[0, -0.5, 0]}>
        <torusGeometry args={[3, 0.08, 32, 200]} />
        <meshPhysicalMaterial
          color={accentColor}
          emissive={winnerColor}
          emissiveIntensity={1.5}
          metalness={1}
          roughness={0}
          clearcoat={1}
          clearcoatRoughness={0}
          transmission={0.3}
          thickness={1}
          ior={2.4}
        />
      </mesh>

      {/* Secondary ring with offset rotation */}
      <mesh ref={ring2Ref} rotation={[Math.PI / 2.2, 0, 0]} position={[0, -0.3, 0]}>
        <torusGeometry args={[2.5, 0.06, 32, 200]} />
        <meshPhysicalMaterial
          color="#ffffff"
          emissive={winnerColor}
          emissiveIntensity={0.8}
          metalness={1}
          roughness={0}
          clearcoat={1}
          transmission={0.5}
          thickness={0.5}
          transparent
          opacity={0.7}
        />
      </mesh>

      {/* Third decorative ring */}
      <mesh rotation={[Math.PI / 1.8, 0, Math.PI / 4]} position={[0, -0.1, 0]}>
        <torusGeometry args={[2, 0.04, 16, 100]} />
        <meshPhysicalMaterial
          color={winnerColor}
          emissive={winnerColor}
          emissiveIntensity={1}
          metalness={0.95}
          roughness={0.05}
          transparent
          opacity={0.5}
        />
      </mesh>

      {/* Luxury flowing particles */}
      <points ref={particlesRef} geometry={particles}>
        <pointsMaterial
          size={0.08}
          color={accentColor}
          transparent
          opacity={0.9}
          sizeAttenuation
          blending={THREE.AdditiveBlending}
          vertexColors={false}
        />
      </points>

      {/* Elegant light rays */}
      {Array.from({ length: 6 }).map((_, i) => {
        const angle = (i / 6) * Math.PI * 2;
        const height = 8 - i * 0.5;
        return (
          <mesh
            key={i}
            position={[
              Math.cos(angle) * 1.5,
              0,
              Math.sin(angle) * 1.5
            ]}
            rotation={[0, -angle, Math.PI / 12]}
          >
            <planeGeometry args={[0.05, height]} />
            <meshBasicMaterial
              color={accentColor}
              transparent
              opacity={0.15 - i * 0.02}
              side={THREE.DoubleSide}
              blending={THREE.AdditiveBlending}
            />
          </mesh>
        );
      })}

      {/* Subtle glow sphere */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[4.5, 64, 64]} />
        <meshBasicMaterial
          color={winnerColor}
          transparent
          opacity={0.03}
          side={THREE.BackSide}
          blending={THREE.AdditiveBlending}
        />
      </mesh>

      {/* Inner glow */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[3, 32, 32]} />
        <meshBasicMaterial
          color={accentColor}
          transparent
          opacity={0.05}
          side={THREE.BackSide}
          blending={THREE.AdditiveBlending}
        />
      </mesh>

      {/* Sparkle points */}
      {Array.from({ length: 20 }).map((_, i) => {
        const phi = Math.acos(1 - 2 * (i / 20));
        const theta = Math.sqrt(20 * Math.PI) * phi;
        const radius = 3.5;
        
        return (
          <mesh
            key={`sparkle-${i}`}
            position={[
              radius * Math.sin(phi) * Math.cos(theta),
              radius * Math.sin(phi) * Math.sin(theta),
              radius * Math.cos(phi)
            ]}
          >
            <octahedronGeometry args={[0.1, 0]} />
            <meshPhysicalMaterial
              color={accentColor}
              emissive={winnerColor}
              emissiveIntensity={2}
              metalness={1}
              roughness={0}
            />
          </mesh>
        );
      })}
      </group>
    </>
  );
}