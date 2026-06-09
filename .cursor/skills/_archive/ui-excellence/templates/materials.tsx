/**
 * Material library for react-three-fiber scenes.
 *
 * Quick reference:
 *   Material                  | Use case                          | Needs <Environment>
 *   --------------------------|-----------------------------------|-----------
 *   GlassMaterial             | Hero orbs, liquid shapes          | YES
 *   FrostedGlassMaterial      | UI panels behind content          | YES
 *   MetalMaterial             | Sci-fi surfaces, hardware         | YES
 *   BrushedMetalMaterial      | Matte industrial surfaces         | YES
 *   GoldMaterial              | Decorative accents                | YES
 *   MatteMaterial             | Body panels, card backs           | NO
 *   PlasticMaterial           | Housing, buttons, soft surfaces   | NO
 *   EmissiveAccentMaterial    | Glow elements for Bloom pickup    | optional
 *   NeonMaterial              | LED, screen, neon sign elements   | optional
 *   TexturedMetal             | When a texture path is available  | YES
 *   ReflectiveFloor           | Product-shot floors               | YES
 */

import { type FC } from 'react'
import {
  MeshTransmissionMaterial,
  MeshReflectorMaterial,
  useTexture,
} from '@react-three/drei'

// ── Glass / crystal / transparent ────────────────────────────────────────────

interface GlassMaterialProps {
  thickness?: number
  roughness?: number
  transmission?: number
  ior?: number
  chromaticAberration?: number
  anisotropy?: number
  envMapIntensity?: number
}

export const GlassMaterial: FC<GlassMaterialProps> = ({
  thickness = 1.5,
  roughness = 0.05,
  transmission = 0.95,
  ior = 1.5,
  chromaticAberration = 0.03,
  anisotropy = 0.3,
  envMapIntensity = 2,
}) => (
  <MeshTransmissionMaterial
    backside
    thickness={thickness}
    roughness={roughness}
    transmission={transmission}
    ior={ior}
    chromaticAberration={chromaticAberration}
    anisotropy={anisotropy}
    envMapIntensity={envMapIntensity}
  />
)

interface FrostedGlassMaterialProps {
  roughness?: number
  transmission?: number
  tint?: string
}

export const FrostedGlassMaterial: FC<FrostedGlassMaterialProps> = ({
  roughness = 0.4,
  transmission = 0.85,
  tint,
}) => (
  <MeshTransmissionMaterial
    backside
    thickness={0.5}
    roughness={roughness}
    transmission={transmission}
    ior={1.45}
    chromaticAberration={0.01}
    envMapIntensity={1.5}
    color={tint}
  />
)

// ── Metallic ──────────────────────────────────────────────────────────────────

interface MetalMaterialProps {
  color?: string
  roughness?: number
  envMapIntensity?: number
}

export const MetalMaterial: FC<MetalMaterialProps> = ({
  color = '#888888',
  roughness = 0.1,
  envMapIntensity = 2,
}) => (
  <meshPhysicalMaterial
    color={color}
    metalness={0.9}
    roughness={roughness}
    envMapIntensity={envMapIntensity}
    reflectivity={1}
    clearcoat={0.2}
    clearcoatRoughness={0.05}
  />
)

interface BrushedMetalMaterialProps {
  color?: string
}

export const BrushedMetalMaterial: FC<BrushedMetalMaterialProps> = ({
  color = '#999999',
}) => (
  <meshPhysicalMaterial
    color={color}
    metalness={0.85}
    roughness={0.35}
    envMapIntensity={1.5}
  />
)

export const GoldMaterial: FC = () => (
  <meshPhysicalMaterial
    color="#c9a84c"
    metalness={1}
    roughness={0.05}
    envMapIntensity={3}
  />
)

// ── Matte / plastic ───────────────────────────────────────────────────────────

interface MatteMaterialProps {
  color?: string
  roughness?: number
}

export const MatteMaterial: FC<MatteMaterialProps> = ({
  color = '#6366f1',
  roughness = 0.6,
}) => (
  <meshPhysicalMaterial
    color={color}
    metalness={0}
    roughness={roughness}
  />
)

interface PlasticMaterialProps {
  color?: string
  clearcoat?: number
}

export const PlasticMaterial: FC<PlasticMaterialProps> = ({
  color = '#ffffff',
  clearcoat = 0.5,
}) => (
  <meshPhysicalMaterial
    color={color}
    metalness={0}
    roughness={0.3}
    clearcoat={clearcoat}
    clearcoatRoughness={0.1}
  />
)

// ── Emissive (Bloom pickup) ───────────────────────────────────────────────────

interface EmissiveAccentMaterialProps {
  color?: string
  glowIntensity?: number
  roughness?: number
}

export const EmissiveAccentMaterial: FC<EmissiveAccentMaterialProps> = ({
  color = '#6366f1',
  glowIntensity = 0.4,
  roughness = 0.4,
}) => (
  <meshPhysicalMaterial
    color={color}
    emissive={color}
    emissiveIntensity={glowIntensity}
    metalness={0.2}
    roughness={roughness}
  />
)

interface NeonMaterialProps {
  color?: string
  intensity?: number
}

export const NeonMaterial: FC<NeonMaterialProps> = ({
  color = '#00ffff',
  intensity = 2,
}) => (
  <meshStandardMaterial
    color={color}
    emissive={color}
    emissiveIntensity={intensity}
    toneMapped={false}
  />
)

// ── Textured metal ────────────────────────────────────────────────────────────
// Requires a texture file. useTexture loads it asynchronously.
// Must be used inside a <Suspense> boundary.

interface TexturedMetalProps {
  texturePath: string
  metalness?: number
  roughness?: number
}

export const TexturedMetal: FC<TexturedMetalProps> = ({
  texturePath,
  metalness = 0.8,
  roughness = 0.2,
}) => {
  const texture = useTexture(texturePath)
  return (
    <meshPhysicalMaterial
      map={texture}
      metalness={metalness}
      roughness={roughness}
      envMapIntensity={1.5}
    />
  )
}

// ── Reflective floor ──────────────────────────────────────────────────────────
// Must be placed on a <planeGeometry> rotated -π/2 on X (flat horizontal).

interface ReflectiveFloorProps {
  position?: [number, number, number]
  size?: number
  color?: string
  blur?: [number, number]
  mixStrength?: number
}

export const ReflectiveFloor: FC<ReflectiveFloorProps> = ({
  position = [0, -1.5, 0],
  size = 20,
  color = '#202035',
  blur = [300, 100],
  mixStrength = 50,
}) => (
  <mesh rotation={[-Math.PI / 2, 0, 0]} position={position}>
    <planeGeometry args={[size, size]} />
    <MeshReflectorMaterial
      blur={blur}
      resolution={1024}
      mixBlur={1}
      mixStrength={mixStrength}
      roughness={1}
      depthScale={1.2}
      minDepthThreshold={0.4}
      maxDepthThreshold={1.4}
      color={color}
      metalness={0.8}
    />
  </mesh>
)
