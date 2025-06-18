import { useRef, useEffect, useMemo } from 'react';
import { Mesh, Vector3, Quaternion, BufferGeometry } from 'three';
import { useFrame } from '@react-three/fiber';
import { Sphere } from '@react-three/drei';
import * as THREE from 'three';
import type { Position3D } from '../types/game3d';

interface WinningLine3DProps {
  winningPositions: Position3D[];
  color: string;
}

export function WinningLine3D({ winningPositions, color }: WinningLine3DProps) {
  const lineRef = useRef<Mesh>(null);
  const glowRef = useRef<Mesh>(null);
  const particlesRef = useRef<THREE.Points>(null);
  const animationTime = useRef(0);
  
  const CELL_SIZE = 1;
  const GAP = 0.1;
  const accentColor = color === '#facc15' ? '#fef3c7' : '#fecaca';
  
  // Delay line appearance to sync with explosion
  const ANIMATION_DELAY = 0.5; // seconds

  // Calculate line position and rotation
  const getLineTransform = () => {
    if (winningPositions.length < 2) return null;

    // Get start and end positions
    const start = winningPositions[0];
    const end = winningPositions[winningPositions.length - 1];

    // Convert to world coordinates
    const startPos = new Vector3(
      start.x * (CELL_SIZE + GAP),
      start.y * (CELL_SIZE + GAP),
      start.z * (CELL_SIZE + GAP)
    );
    const endPos = new Vector3(
      end.x * (CELL_SIZE + GAP),
      end.y * (CELL_SIZE + GAP),
      end.z * (CELL_SIZE + GAP)
    );

    // Calculate center position
    const center = new Vector3().addVectors(startPos, endPos).multiplyScalar(0.5);

    // Calculate direction and length
    const direction = new Vector3().subVectors(endPos, startPos);
    const length = direction.length() + 0.8; // Extend slightly beyond pieces

    // Calculate rotation
    direction.normalize();
    const up = new Vector3(0, 1, 0);
    const quaternion = new Quaternion();
    quaternion.setFromUnitVectors(up, direction);

    return { center, length, quaternion };
  };

  const transform = getLineTransform();

  useEffect(() => {
    animationTime.current = 0;
  }, [winningPositions]);

  useFrame((state, delta) => {
    if (!transform || !lineRef.current) return;

    animationTime.current += delta;
    const t = animationTime.current;
    
    // Apply delay before starting animations
    const delayedT = Math.max(0, t - ANIMATION_DELAY);

    // Line animation with smooth entrance
    if (lineRef.current) {
      // Scale in animation with elastic easing
      const scaleProgress = Math.min(delayedT * 1.5, 1);
      const easeOutElastic = (x: number) => {
        const c4 = (2 * Math.PI) / 3;
        return x === 0 ? 0 : x === 1 ? 1 : Math.pow(2, -10 * x) * Math.sin((x * 10 - 0.75) * c4) + 1;
      };
      lineRef.current.scale.y = easeOutElastic(scaleProgress);
      
      // Hide completely during delay
      lineRef.current.visible = t > ANIMATION_DELAY;
      
      // Gentle breathing effect
      const breath = 1 + Math.sin(t * 2) * 0.03;
      lineRef.current.scale.x = breath;
      lineRef.current.scale.z = breath;
    }

    // Glow animation
    if (glowRef.current) {
      glowRef.current.visible = t > ANIMATION_DELAY;
      if (delayedT > 0) {
        const glowPulse = 0.15 + Math.sin(delayedT * 3) * 0.05;
        glowRef.current.scale.x = 1 + glowPulse;
        glowRef.current.scale.z = 1 + glowPulse;
        (glowRef.current.material as THREE.MeshBasicMaterial).opacity = 0.3 + Math.sin(delayedT * 2) * 0.1;
      }
    }

    // Particle flow along line
    if (particlesRef.current && particlesRef.current.geometry.attributes.position) {
      particlesRef.current.visible = t > ANIMATION_DELAY;
      if (delayedT > 0) {
        const positions = particlesRef.current.geometry.attributes.position;
        const progress = (delayedT * 0.3) % 1;
      
      for (let i = 0; i < 20; i++) {
        const particleT = ((i / 20) + progress) % 1;
        const pos = new Vector3().lerpVectors(
          new Vector3(
            winningPositions[0].x * (CELL_SIZE + GAP),
            winningPositions[0].y * (CELL_SIZE + GAP),
            winningPositions[0].z * (CELL_SIZE + GAP)
          ),
          new Vector3(
            winningPositions[winningPositions.length - 1].x * (CELL_SIZE + GAP),
            winningPositions[winningPositions.length - 1].y * (CELL_SIZE + GAP),
            winningPositions[winningPositions.length - 1].z * (CELL_SIZE + GAP)
          ),
          particleT
        );
        
        const offset = Math.sin(particleT * Math.PI) * 0.3;
        positions.array[i * 3] = pos.x + (Math.random() - 0.5) * offset;
        positions.array[i * 3 + 1] = pos.y + (Math.random() - 0.5) * offset;
        positions.array[i * 3 + 2] = pos.z + (Math.random() - 0.5) * offset;
      }
        
        positions.needsUpdate = true;
      }
    }
  });

  if (!transform) return null;

  // Create particle geometry for flowing effect
  const particleGeometry = useMemo(() => {
    const geometry = new BufferGeometry();
    const positions = new Float32Array(20 * 3);
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    return geometry;
  }, []);

  return (
    <group>
      {/* Glow cylinder behind main line */}
      <mesh
        ref={glowRef}
        position={transform.center}
        quaternion={transform.quaternion}
      >
        <cylinderGeometry args={[0.2, 0.2, transform.length, 32]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.3}
          blending={THREE.AdditiveBlending}
        />
      </mesh>

      {/* Main line with premium material */}
      <mesh
        ref={lineRef}
        position={transform.center}
        quaternion={transform.quaternion}
      >
        <cylinderGeometry args={[0.06, 0.06, transform.length, 32]} />
        <meshPhysicalMaterial
          color={accentColor}
          emissive={color}
          emissiveIntensity={1.5}
          metalness={0.95}
          roughness={0.05}
          clearcoat={1}
          clearcoatRoughness={0}
          transmission={0.2}
          thickness={0.5}
        />
      </mesh>

      {/* Premium end spheres */}
      {winningPositions.length > 0 && (
        <>
          {/* Start sphere */}
          <group position={[
            winningPositions[0].x * (CELL_SIZE + GAP),
            winningPositions[0].y * (CELL_SIZE + GAP),
            winningPositions[0].z * (CELL_SIZE + GAP)
          ]}>
            <Sphere args={[0.15, 32, 32]}>
              <meshPhysicalMaterial
                color={accentColor}
                emissive={color}
                emissiveIntensity={2}
                metalness={1}
                roughness={0}
                clearcoat={1}
              />
            </Sphere>
            <Sphere args={[0.25, 32, 32]}>
              <meshBasicMaterial
                color={color}
                transparent
                opacity={0.3}
                blending={THREE.AdditiveBlending}
              />
            </Sphere>
          </group>

          {/* End sphere */}
          <group position={[
            winningPositions[winningPositions.length - 1].x * (CELL_SIZE + GAP),
            winningPositions[winningPositions.length - 1].y * (CELL_SIZE + GAP),
            winningPositions[winningPositions.length - 1].z * (CELL_SIZE + GAP)
          ]}>
            <Sphere args={[0.15, 32, 32]}>
              <meshPhysicalMaterial
                color={accentColor}
                emissive={color}
                emissiveIntensity={2}
                metalness={1}
                roughness={0}
                clearcoat={1}
              />
            </Sphere>
            <Sphere args={[0.25, 32, 32]}>
              <meshBasicMaterial
                color={color}
                transparent
                opacity={0.3}
                blending={THREE.AdditiveBlending}
              />
            </Sphere>
          </group>
        </>
      )}

      {/* Flowing particles along the line */}
      <points ref={particlesRef} geometry={particleGeometry}>
        <pointsMaterial
          size={0.1}
          color={accentColor}
          transparent
          opacity={0.8}
          sizeAttenuation
          blending={THREE.AdditiveBlending}
        />
      </points>

      {/* Highlight each winning position */}
      {winningPositions.map((pos, i) => (
        <group
          key={`win-pos-${i}`}
          position={[
            pos.x * (CELL_SIZE + GAP),
            pos.y * (CELL_SIZE + GAP),
            pos.z * (CELL_SIZE + GAP)
          ]}
        >
          <mesh>
            <ringGeometry args={[0.4, 0.45, 32]} />
            <meshBasicMaterial
              color={color}
              transparent
              opacity={0.3}
              side={THREE.DoubleSide}
              blending={THREE.AdditiveBlending}
            />
          </mesh>
        </group>
      ))}
    </group>
  );
}