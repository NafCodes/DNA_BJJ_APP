/**
 * EffectComposer configurations for different scene aesthetics.
 * All components go inside <Canvas>, as the last child before </Canvas>.
 *
 * Usage: pick the config that matches your scene type, then pass
 * scene-specific values via props rather than editing the template.
 *
 * Run before editing:
 *   resolve-library-id "@react-three/postprocessing"
 *   query-docs <id> "EffectComposer setup"
 */

import { type FC, useState, useEffect } from 'react'
import {
  EffectComposer,
  Bloom,
  ChromaticAberration,
  Vignette,
  DepthOfField,
  Noise,
  Glitch,
  SMAA,
} from '@react-three/postprocessing'
import { BlendFunction, GlitchMode } from 'postprocessing'
import { Vector2 } from 'three'

// ── Default — 90% of scenes ───────────────────────────────────────────────────
// Clean, cinematic. Subtle chromatic aberration. Soft vignette.
// Bloom only on bright emissive elements.

interface DefaultPostProcessingProps {
  bloomIntensity?: number
  vignetteDarkness?: number
}

export const DefaultPostProcessing: FC<DefaultPostProcessingProps> = ({
  bloomIntensity = 1.2,
  vignetteDarkness = 0.4,
}) => (
  <EffectComposer>
    <Bloom luminanceThreshold={0.85} intensity={bloomIntensity} mipmapBlur />
    <ChromaticAberration offset={new Vector2(0.001, 0.001)} />
    <Vignette darkness={vignetteDarkness} offset={0.3} />
  </EffectComposer>
)

// ── Cinematic / film — dramatic hero sections ─────────────────────────────────
// Heavy bloom, film grain, strong vignette. Not for dashboards or tools.

interface CinematicPostProcessingProps {
  bloomIntensity?: number
  vignetteDarkness?: number
  filmGrainOpacity?: number
}

export const CinematicPostProcessing: FC<CinematicPostProcessingProps> = ({
  bloomIntensity = 1.8,
  vignetteDarkness = 0.55,
  filmGrainOpacity = 0.06,
}) => (
  <EffectComposer>
    <Bloom luminanceThreshold={0.75} intensity={bloomIntensity} mipmapBlur levels={8} />
    <ChromaticAberration offset={new Vector2(0.0015, 0.0015)} />
    <Vignette darkness={vignetteDarkness} offset={0.25} />
    <Noise premultiply blendFunction={BlendFunction.ADD} opacity={filmGrainOpacity} />
  </EffectComposer>
)

// ── Product / clean — demos and dashboards ────────────────────────────────────
// Minimal. No chromatic aberration. SMAA for clean edges.

interface ProductPostProcessingProps {
  bloomIntensity?: number
  vignetteDarkness?: number
}

export const ProductPostProcessing: FC<ProductPostProcessingProps> = ({
  bloomIntensity = 0.8,
  vignetteDarkness = 0.25,
}) => (
  <EffectComposer>
    <Bloom luminanceThreshold={0.9} intensity={bloomIntensity} mipmapBlur />
    <Vignette darkness={vignetteDarkness} offset={0.4} />
    <SMAA />
  </EffectComposer>
)

// ── Depth of field — scenes with a clear focal subject ────────────────────────
// Only use when there is a single focal point at a known depth.
// Looks wrong on scenes without a clear focal plane.

interface DOFPostProcessingProps {
  focalLength?: number
  bloomIntensity?: number
  vignetteDarkness?: number
}

export const DOFPostProcessing: FC<DOFPostProcessingProps> = ({
  focalLength = 0.02,
  bloomIntensity = 1.0,
  vignetteDarkness = 0.4,
}) => (
  <EffectComposer>
    <DepthOfField
      focusDistance={0.01}
      focalLength={focalLength}
      bokehScale={2}
      height={480}
    />
    <Bloom luminanceThreshold={0.85} intensity={bloomIntensity} mipmapBlur />
    <ChromaticAberration offset={new Vector2(0.001, 0.001)} />
    <Vignette darkness={vignetteDarkness} offset={0.3} />
  </EffectComposer>
)

// ── Glitch / cyberpunk — intentional distortion aesthetic ─────────────────────
// DO NOT use this for professional/clean contexts.
// Only use when the scene intentionally has a glitch/hacker aesthetic.

export const GlitchPostProcessing: FC = () => (
  <EffectComposer>
    <Glitch
      delay={new Vector2(1.5, 3.5)}
      duration={new Vector2(0.05, 0.15)}
      strength={new Vector2(0.1, 0.2)}
      mode={GlitchMode.SPORADIC}
      active
      ratio={0.85}
    />
    <Bloom luminanceThreshold={0.7} intensity={1.5} mipmapBlur />
    <ChromaticAberration offset={new Vector2(0.003, 0.003)} />
    <Vignette darkness={0.5} offset={0.2} />
  </EffectComposer>
)

// ── Mobile — lightweight stack for mobile GPUs ────────────────────────────────
// Bloom only. No ChromaticAberration (expensive on mobile).
// Use AdaptivePostProcessing to auto-switch instead of using this directly.

interface MobilePostProcessingProps {
  bloomIntensity?: number
}

export const MobilePostProcessing: FC<MobilePostProcessingProps> = ({
  bloomIntensity = 0.9,
}) => (
  <EffectComposer>
    <Bloom luminanceThreshold={0.85} intensity={bloomIntensity} mipmapBlur />
  </EffectComposer>
)

// ── Adaptive — auto-selects based on device capability ───────────────────────
// Renders the full DefaultPostProcessing on desktop, MobilePostProcessing on
// mobile/low-DPR devices. Pass `isMobile` from a `useMediaQuery` hook, or
// let the component detect via devicePixelRatio (< 2 = likely mobile GPU).

interface AdaptivePostProcessingProps {
  isMobile?: boolean
  bloomIntensity?: number
  vignetteDarkness?: number
}

export const AdaptivePostProcessing: FC<AdaptivePostProcessingProps> = ({
  isMobile,
  bloomIntensity = 1.2,
  vignetteDarkness = 0.4,
}) => {
  const [mobileDetected, setMobileDetected] = useState(false)

  useEffect(() => {
    if (isMobile !== undefined) {
      setMobileDetected(isMobile)
    } else {
      // Heuristic: mobile GPUs tend to be at 2x+ DPR on small screens
      const isMobileViewport = window.innerWidth < 768
      setMobileDetected(isMobileViewport)
    }
  }, [isMobile])

  if (mobileDetected) {
    return <MobilePostProcessing bloomIntensity={bloomIntensity} />
  }

  return (
    <DefaultPostProcessing
      bloomIntensity={bloomIntensity}
      vignetteDarkness={vignetteDarkness}
    />
  )
}

// ── Rules ─────────────────────────────────────────────────────────────────────
//
// 1. EffectComposer must be the LAST child inside <Canvas>
// 2. Max 3 effects without explicit reason — effects compound perf cost
// 3. ChromaticAberration offset must be new Vector2(x, y) — NOT [x, y]
// 4. ChromaticAberration offset values must stay ≤ 0.002
// 5. Bloom luminanceThreshold ≥ 0.75 or everything blooms white
// 6. Do NOT combine GlitchPostProcessing with any non-glitch aesthetic
// 7. Noise opacity 0.04–0.08 — anything higher looks broken
// 8. SMAA is an anti-aliasing pass — use when scene looks jagged, not always
