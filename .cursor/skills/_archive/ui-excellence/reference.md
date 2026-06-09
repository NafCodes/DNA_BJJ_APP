# UI Excellence Reference

## Canvas checklist

| Check | Target |
|-------|--------|
| SSR | `dynamic(..., { ssr: false })` wrapper |
| DPR | `dpr={[1, 2]}` |
| Tone mapping | `gl={{ toneMapping: ACESFilmicToneMapping }}` |
| Lighting | `<Environment preset="city" />` not bare ambient |
| Post-processing | Bloom + Vignette (+ optional ChromaticAberration) |
| Idle life | `<Float>` on hero mesh |
| Controls | `OrbitControls` with `enableDamping` |

## Materials

| Lovable default | Upgrade |
|-----------------|---------|
| `meshBasicMaterial` | `MeshTransmissionMaterial` (glass) or `meshPhysicalMaterial` |
| Flat color box | `MeshTransmissionMaterial` + Environment |
| Many identical meshes | `InstancedMesh` + ref mutation in `useFrame` |

## Motion

Page transition pattern:

```tsx
'use client'
import { motion } from 'framer-motion'

export function PageShell({ children }: { children: React.ReactNode }) {
  return (
    <motion.main
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.main>
  )
}
```

List stagger: wrap items in `motion.div` with `transition={{ delay: index * 0.05 }}`.

## Performance

- Cap particles (Sparkles count ≤ 200 on demo device)
- One Canvas per golden-path view — no nested Canvases
- Profile DevTools Performance if frame rate drops below 30fps
