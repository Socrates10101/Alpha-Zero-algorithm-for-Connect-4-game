export function Lighting() {
  return (
    <>
      <ambientLight intensity={0.35} />
      
      {/* Main key light */}
      <directionalLight
        position={[10, 15, 8]}
        intensity={0.8}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        color="#ffffff"
      />
      
      {/* Fill light */}
      <directionalLight
        position={[-10, 10, -5]}
        intensity={0.4}
        color="#bfdbfe"
      />
      
      {/* Top accent light */}
      <pointLight 
        position={[0, 12, 0]} 
        intensity={0.4} 
        color="#ddd6fe" 
        distance={20}
        decay={2}
      />
      
      {/* Victory spotlight (when pieces are shown) */}
      <spotLight
        position={[1.5, 10, 1.5]}
        angle={0.5}
        penumbra={0.5}
        intensity={0.3}
        color="#fbbf24"
        target-position={[1.5, 0, 1.5]}
      />
      
      {/* Rim lighting for depth */}
      <directionalLight
        position={[0, -5, 10]}
        intensity={0.15}
        color="#60a5fa"
      />
      <directionalLight
        position={[0, -5, -10]}
        intensity={0.15}
        color="#c084fc"
      />
      
      {/* Subtle side lights for glass effect */}
      <pointLight
        position={[5, 2, 0]}
        intensity={0.1}
        color="#3b82f6"
        distance={10}
      />
      <pointLight
        position={[-5, 2, 0]}
        intensity={0.1}
        color="#8b5cf6"
        distance={10}
      />
    </>
  );
}