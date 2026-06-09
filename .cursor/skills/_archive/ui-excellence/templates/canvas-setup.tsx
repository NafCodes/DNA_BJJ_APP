'use client'

import { type FC, useRef, Suspense } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import {
  Environment,
  Float,
  OrbitControls,
  Sparkles,
  MeshTransmissionMaterial,
} from '@react-three/drei'
import {
  EffectComposer,
  Bloom,
  ChromaticAberration,
  Vignette,
} from '@react-three/postprocessing'
import { ACESFilmicToneMapping, Vector2 } from 'three'
import type * as THREE from 'three'

// ── Types ─────────────────────────────────────────────────────────────────────

export interface SceneProps {
  className?: string
  environmentPreset?: 'city' | 'night' | 'warehouse' | 'sunset' | 'dawn' | 'forest'
  bloomIntensity?: number
  orbitEnabled?: boolean
}

interface SceneContentsProps {
  environmentPreset: NonNullable<SceneProps['environmentPreset']>
  bloomIntensity: number
  orbitEnabled: boolean
}

// ── Hero object ───────────────────────────────────────────────────────────────

function HeroMesh() {
  const meshRef = useRef<THREE.Mesh>(null)

  useFrame((_state, delta) => {
    if (!meshRef.current) return
    meshRef.current.rotation.x += delta * 0.1
    meshRef.current.rotation.y += delta * 0.18
  })

  return (
    <Float speed={1.5} rotationIntensity={0.3} floatIntensity={0.5}>
      <mesh ref={meshRef} castShadow>
        <icosahedronGeometry args={[1.2, 1]} />
        <MeshTransmissionMaterial
          backside
          thickness={1.5}
          roughness={0.05}
          transmission={0.95}
          ior={1.5}
          chromaticAberration={0.03}
          anisotropy={0.3}
          envMapIntensity={2}
        />
      </mesh>
    </Float>
  )
}

// ── Scene interior ────────────────────────────────────────────────────────────

const SceneContents: FC<SceneContentsProps> = ({
  environmentPreset,
  bloomIntensity,
  orbitEnabled,
}) => {
  return (
    <>
      <Environment preset={environmentPreset} />

      <Sparkles
        count={200}
        size={1.5}
        speed={0.3}
        opacity={0.6}
        color="#a78bfa"
        scale={[10, 10, 10]}
      />

      <HeroMesh />

      {orbitEnabled && (
        <OrbitControls
          makeDefault
          enableDamping
          dampingFactor={0.05}
          enableZoom={false}
          enablePan={false}
          maxPolarAngle={Math.PI * 0.6}
        />
      )}

      <EffectComposer>
        <Bloom luminanceThreshold={0.85} intensity={bloomIntensity} mipmapBlur />
        <ChromaticAberration offset={new Vector2(0.001, 0.001)} />
        <Vignette darkness={0.4} offset={0.3} />
      </EffectComposer>
    </>
  )
}

// ── Canvas root ───────────────────────────────────────────────────────────────

export function Scene({
  className = 'w-full h-full',
  environmentPreset = 'city',
  bloomIntensity = 1.2,
  orbitEnabled = true,
}: SceneProps) {
  return (
    <Canvas
      dpr={[1, 2]}
      gl={{
        antialias: true,
        toneMapping: ACESFilmicToneMapping,
        toneMappingExposure: 1.1,
      }}
      camera={{ position: [0, 0, 6], fov: 45, near: 0.1, far: 100 }}
      className={className}
    >
      <Suspense fallback={null}>
        <SceneContents
          environmentPreset={environmentPreset}
          bloomIntensity={bloomIntensity}
          orbitEnabled={orbitEnabled}
        />
      </Suspense>
    </Canvas>
  )
}

// ── Dynamic import for Next.js pages ─────────────────────────────────────────
//
// Copy this block into app/page.tsx (or whichever page hosts the Canvas).
// Do NOT import Scene directly — it will crash on server render.

/*
import dynamic from 'next/dynamic'
import type { SceneProps } from '@/components/Scene'

const Scene = dynamic<SceneProps>(
  () => import('@/components/Scene').then((m) => ({ default: m.Scene })),
  { ssr: false }
)

export default function Page() {
  return (
    <div className="w-full h-screen bg-black">
      <Scene environmentPreset="city" bloomIntensity={1.2} orbitEnabled />
    </div>
  )
}
*/
