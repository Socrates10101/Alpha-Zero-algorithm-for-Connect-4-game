import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface ExplosionEffectProps {
  position: [number, number, number];
  color: string;
  delay?: number;
}

export function ExplosionEffect({ position, color, delay = 0 }: ExplosionEffectProps) {
  const groupRef = useRef<THREE.Group>(null);
  const particlesRef = useRef<THREE.Points>(null);
  const ringsRef = useRef<THREE.Mesh[]>([]);
  const startTime = useRef(Date.now() + delay * 1000);
  
  // Create explosion particles
  const particleGeometry = useMemo(() => {
    const count = 500;
    const positions = new Float32Array(count * 3);
    const velocities = new Float32Array(count * 3);
    const sizes = new Float32Array(count);
    const lifetimes = new Float32Array(count);
    
    for (let i = 0; i < count; i++) {
      // Random position on sphere
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const radius = 0.1;
      
      positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = radius * Math.cos(phi);
      
      // Velocity outward from center
      const speed = 5 + Math.random() * 10;
      velocities[i * 3] = positions[i * 3] * speed;
      velocities[i * 3 + 1] = positions[i * 3 + 1] * speed + Math.random() * 5;
      velocities[i * 3 + 2] = positions[i * 3 + 2] * speed;
      
      sizes[i] = Math.random() * 0.5 + 0.5;
      lifetimes[i] = Math.random() * 0.5 + 0.5;
    }
    
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('velocity', new THREE.BufferAttribute(velocities, 3));
    geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
    geometry.setAttribute('lifetime', new THREE.BufferAttribute(lifetimes, 1));
    
    return geometry;
  }, []);

  useFrame(() => {
    const elapsed = (Date.now() - startTime.current) / 1000;
    
    if (elapsed < 0) return; // Wait for delay
    
    if (!groupRef.current) return;
    
    // Fade out after 2 seconds
    const fadeOut = Math.max(0, 1 - elapsed / 2);
    groupRef.current.visible = fadeOut > 0;
    
    // Update particles
    if (particlesRef.current && particlesRef.current.geometry.attributes.position) {
      const positions = particlesRef.current.geometry.attributes.position;
      const velocities = particlesRef.current.geometry.attributes.velocity;
      const sizes = particlesRef.current.geometry.attributes.size;
      const lifetimes = particlesRef.current.geometry.attributes.lifetime;
      
      for (let i = 0; i < positions.count; i++) {
        const lifetime = lifetimes.array[i];
        const particleAge = elapsed / lifetime;
        
        if (particleAge < 1) {
          // Update position
          positions.array[i * 3] += velocities.array[i * 3] * 0.016;
          positions.array[i * 3 + 1] += velocities.array[i * 3 + 1] * 0.016;
          positions.array[i * 3 + 2] += velocities.array[i * 3 + 2] * 0.016;
          
          // Apply gravity
          velocities.array[i * 3 + 1] -= 9.8 * 0.016;
          
          // Damping
          velocities.array[i * 3] *= 0.98;
          velocities.array[i * 3 + 1] *= 0.98;
          velocities.array[i * 3 + 2] *= 0.98;
          
          // Shrink over time
          sizes.array[i] = (1 - particleAge) * (Math.random() * 0.5 + 0.5);
        } else {
          sizes.array[i] = 0;
        }
      }
      
      positions.needsUpdate = true;
      sizes.needsUpdate = true;
      
      // Update material opacity
      if (particlesRef.current.material) {
        (particlesRef.current.material as THREE.PointsMaterial).opacity = fadeOut;
      }
    }
    
    // Update shock wave rings
    ringsRef.current.forEach((ring, index) => {
      if (ring) {
        const ringProgress = Math.min(elapsed * 2, 1);
        const scale = 1 + ringProgress * (3 + index);
        ring.scale.set(scale, scale, scale);
        
        if (ring.material) {
          (ring.material as THREE.MeshBasicMaterial).opacity = (1 - ringProgress) * 0.5;
        }
      }
    });
  });

  return (
    <group ref={groupRef} position={position}>
      {/* Explosion particles */}
      <points ref={particlesRef} geometry={particleGeometry}>
        <pointsMaterial
          size={0.2}
          color={color}
          transparent
          opacity={1}
          sizeAttenuation
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </points>
      
      {/* Flash sphere */}
      <mesh scale={[0.1, 0.1, 0.1]}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshBasicMaterial
          color="#ffffff"
          transparent
          opacity={0.8}
          blending={THREE.AdditiveBlending}
        />
      </mesh>
      
      {/* Shock wave rings */}
      {[0, 1, 2].map((i) => (
        <mesh
          key={i}
          ref={(el) => { if (el) ringsRef.current[i] = el; }}
          rotation={[Math.PI / 2, 0, i * Math.PI / 6]}
        >
          <ringGeometry args={[0.9, 1, 64]} />
          <meshBasicMaterial
            color={color}
            transparent
            opacity={0.5}
            side={THREE.DoubleSide}
            blending={THREE.AdditiveBlending}
          />
        </mesh>
      ))}
      
      {/* Energy sphere */}
      <mesh>
        <sphereGeometry args={[2, 32, 32]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.1}
          side={THREE.BackSide}
          blending={THREE.AdditiveBlending}
        />
      </mesh>
    </group>
  );
}