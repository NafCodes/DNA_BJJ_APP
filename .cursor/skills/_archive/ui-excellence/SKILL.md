---
name: ui-excellence
description: >-
  Cursor hero UI pass: cinematic R3F scenes, post-processing, premium materials,
  and Framer Motion transitions on the golden path. Run after lovable-import
  validates. Trigger on: upgrade UI, 3D scene, animations, make it outstanding,
  polish the demo, smooth transitions.
---

# UI Excellence

**Cursor's differentiator.** Lovable gives an MVP; this skill makes judges remember the UI.

**Prerequisite:** [lovable-import](../lovable-import/SKILL.md) complete — `validate.py` passed, `npm run build` clean.

**Scope:** Golden-path screens and Canvas components only. ≤5 files per chunk.

---

## Step 1 — Analyze

```bash
python .cursor/skills/ui-excellence/scripts/analyze.py .
```

Read JSON. Work `upgrade_order` first. Install `missing_packages`:

```bash
npm install @react-three/postprocessing framer-motion
```

---

## Step 2 — Canvas upgrade (each file in `canvas_audit`)

```bash
python .cursor/skills/ui-excellence/scripts/patch_canvas.py <path-to-canvas-file> --write
```

Verify after each patch:

- `dpr={[1, 2]}` on `<Canvas>`
- `ACESFilmicToneMapping` on gl
- `<Environment preset="..." />`
- `<EffectComposer>` with Bloom + Vignette (max 3 effects)
- Parent page uses `dynamic(() => import('./Scene'), { ssr: false })`

Materials — run audit, upgrade manually:

```bash
python .cursor/skills/ui-excellence/scripts/audit_materials.py .
```

Replace `meshBasicMaterial` → `MeshTransmissionMaterial` or `meshPhysicalMaterial` where it matters. See [reference.md](reference.md).

Templates: [templates/](templates/)

---

## Step 3 — Framer Motion (2D layer)

Golden path only — page enter/exit, panel slides, list stagger.

```tsx
import { motion, AnimatePresence } from 'framer-motion'
```

- Wrap route content in `<AnimatePresence mode="wait">`
- Stagger lists that appear on the demo path
- Do **not** animate forms, tables, or loading spinners

See [reference.md § Motion](reference.md#motion)

---

## Step 4 — Build gate

```bash
npm run build
```

Fix all errors. Quick manual check: bloom visible, transitions smooth, no console errors on demo route.

---

## Hard rules

- No `setState` inside `useFrame` — refs only
- Cap `dpr` at `[1, 2]`
- Dispose geometries/materials on unmount
- Max 3 post-processing effects unless justified
- No Theatre.js or physics unless user explicitly asks
- Do not touch auth, schema, or API routes — use [production-stack](../production-stack/SKILL.md)
