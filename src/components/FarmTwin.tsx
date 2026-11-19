import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { useState } from "react";

type Props = { reducedMotion: boolean };

function Terrain({ onSelect, selected }: { onSelect: (plot: string) => void; selected: string }) {
  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.15, 0]} receiveShadow>
        <planeGeometry args={[15, 11, 48, 36]} />
        <meshStandardMaterial color="#294834" roughness={0.96} />
      </mesh>
      {[
        [-3.6, -2.2],
        [0, -2.2],
        [3.6, -2.2],
        [-3.6, 1.6],
        [0, 1.6],
        [3.6, 1.6],
      ].map(([x, z], index) => {
        const id = `Plot ${String(index + 1).padStart(2, "0")}`;
        const active = selected === id;
        return (
          <mesh
            key={id}
            position={[x, 0.02, z]}
            onClick={(event) => {
              event.stopPropagation();
              onSelect(id);
            }}
            onPointerOver={(event) => {
              event.stopPropagation();
              document.body.style.cursor = "pointer";
            }}
            onPointerOut={() => {
              document.body.style.cursor = "auto";
            }}
          >
            <boxGeometry args={[3.2, 0.12, 3.25]} />
            <meshStandardMaterial
              color={active ? "#a1d47b" : index % 2 ? "#52764a" : "#446940"}
              roughness={0.9}
              transparent
              opacity={active ? 0.92 : 0.72}
            />
          </mesh>
        );
      })}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.05, 0]} receiveShadow>
        <ringGeometry args={[0.14, 0.24, 24]} />
        <meshStandardMaterial color="#d5b66b" />
      </mesh>
    </group>
  );
}

export default function FarmTwin({ reducedMotion }: Props) {
  const [selected, setSelected] = useState("Plot 01");
  return (
    <div className="twin-stage" aria-label="Illustrative interactive farm scene">
      <Canvas
        dpr={[1, 1.5]}
        camera={{ position: [10, 10, 12], fov: 36 }}
        shadows
        gl={{ antialias: false, powerPreference: "low-power" }}
      >
        <color attach="background" args={["#17251c"]} />
        <fog attach="fog" args={["#17251c", 17, 30]} />
        <ambientLight intensity={1.2} />
        <directionalLight position={[6, 10, 4]} intensity={2} castShadow={!reducedMotion} />
        <Terrain selected={selected} onSelect={setSelected} />
        <OrbitControls
          enableDamping={!reducedMotion}
          dampingFactor={0.08}
          minDistance={9}
          maxDistance={21}
          maxPolarAngle={Math.PI / 2.15}
        />
      </Canvas>
      <div className="twin-caption">
        <span className="scene-dot" />
        <span>Illustrative scene · not satellite imagery</span>
      </div>
      <div className="plot-selection" aria-live="polite">
        <span className="tiny-label">SELECTED PLOT</span>
        <strong>{selected}</strong>
        <span>Connect field boundaries to load plot data</span>
      </div>
    </div>
  );
}
