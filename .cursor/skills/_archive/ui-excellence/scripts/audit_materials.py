#!/usr/bin/env python3
"""
audit_materials.py — Deep material audit for the ui-upgrade skill.

For each material found, reports:
  - The containing component name
  - The parent <mesh> geometry type (if detectable)
  - The recommended replacement with exact reason
  - Confidence: high / medium / low
  - Two alternatives for low-confidence cases
  - The exact import statement needed

Usage: python3 audit_materials.py <project-root>
"""

import sys
import re
import json
from pathlib import Path


# ── Material detection patterns ───────────────────────────────────────────────

OLD_MATERIALS = {
    "meshBasicMaterial":    re.compile(r'<meshBasicMaterial\b|MeshBasicMaterial\b'),
    "meshStandardMaterial": re.compile(r'<meshStandardMaterial\b|MeshStandardMaterial\b'),
    "meshLambertMaterial":  re.compile(r'<meshLambertMaterial\b|MeshLambertMaterial\b'),
    "meshPhongMaterial":    re.compile(r'<meshPhongMaterial\b|MeshPhongMaterial\b'),
}

GEOMETRY_NAMES = [
    "sphereGeometry",
    "icosahedronGeometry",
    "torusGeometry",
    "torusKnotGeometry",
    "octahedronGeometry",
    "dodecahedronGeometry",
    "tetrahedronGeometry",
    "planeGeometry",
    "boxGeometry",
    "cylinderGeometry",
    "coneGeometry",
    "capsuleGeometry",
    "tubeGeometry",
    "ringGeometry",
    "circleGeometry",
]

# Geometries that are typically floors/grounds
FLOOR_GEOMETRIES = {"planeGeometry", "circleGeometry"}

# Geometries that are typically decorative hero objects
HERO_GEOMETRIES = {
    "sphereGeometry", "icosahedronGeometry", "torusGeometry",
    "torusKnotGeometry", "octahedronGeometry", "dodecahedronGeometry",
    "tetrahedronGeometry",
}

# Geometries that are UI or structural
STRUCTURAL_GEOMETRIES = {"boxGeometry", "cylinderGeometry", "capsuleGeometry"}


# ── Import snippets ───────────────────────────────────────────────────────────

IMPORT_LINES = {
    "MeshTransmissionMaterial": "import { MeshTransmissionMaterial } from '@react-three/drei'",
    "MeshReflectorMaterial":    "import { MeshReflectorMaterial } from '@react-three/drei'",
    "meshPhysicalMaterial":     "// meshPhysicalMaterial is built into R3F — no import needed",
    "meshStandardMaterial":     "// meshStandardMaterial is built into R3F — no import needed",
}

REPLACEMENT_SNIPPETS = {
    "MeshTransmissionMaterial": """\
<MeshTransmissionMaterial
  backside
  thickness={1.5}
  roughness={0.05}
  transmission={0.95}
  ior={1.5}
  chromaticAberration={0.03}
  anisotropy={0.3}
  envMapIntensity={2}
/>""",
    "MeshReflectorMaterial": """\
<MeshReflectorMaterial
  blur={[300, 100]}
  resolution={1024}
  mixBlur={1}
  mixStrength={50}
  roughness={1}
  depthScale={1.2}
  minDepthThreshold={0.4}
  maxDepthThreshold={1.4}
  color="#202035"
  metalness={0.8}
/>""",
    "meshPhysicalMaterial_metal": """\
<meshPhysicalMaterial
  color="#888888"
  metalness={0.9}
  roughness={0.1}
  envMapIntensity={2}
  clearcoat={0.3}
  clearcoatRoughness={0.1}
/>""",
    "meshPhysicalMaterial_matte": """\
<meshPhysicalMaterial
  color="#6366f1"
  metalness={0}
  roughness={0.6}
  envMapIntensity={1}
/>""",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def is_excluded(path: Path) -> bool:
    excluded = {"node_modules", ".git", "dist", "build", ".next", ".claude", ".cursor"}
    return any(part in excluded for part in path.parts)


def extract_component_name(content: str, mat_line: int) -> str:
    """
    Walk backwards from the material's line to find the nearest
    enclosing function or const component declaration.
    """
    lines = content.splitlines()
    pat = re.compile(
        r'(?:export\s+(?:default\s+)?(?:function|const)\s+([A-Z][A-Za-z0-9_]*)'
        r'|function\s+([A-Z][A-Za-z0-9_]*))',
    )
    for i in range(min(mat_line - 1, len(lines) - 1), -1, -1):
        m = pat.search(lines[i])
        if m:
            return m.group(1) or m.group(2) or "UnknownComponent"
    return "UnknownComponent"


def extract_geometry_near_material(content: str, mat_pos: int, window: int = 800) -> str | None:
    """
    Look in a window of characters around the material tag for a geometry JSX tag.
    Returns the geometry name or None.
    """
    start = max(0, mat_pos - window)
    end   = min(len(content), mat_pos + window)
    region = content[start:end]

    for geo in GEOMETRY_NAMES:
        if re.search(rf'<{re.escape(geo)}\b', region):
            return geo
    return None


def build_recommendation(
    old_mat: str,
    geo: str | None,
    content_region: str,
) -> dict:
    """
    Given the material type and (optionally) the detected geometry,
    return { confidence, primary, alternative, reason }.
    """
    # Check if material has emissive (means it's meant to glow, keep or upgrade)
    has_emissive = bool(re.search(r'\bemissive\b', content_region))

    if old_mat == "meshBasicMaterial":
        if geo in FLOOR_GEOMETRIES:
            return {
                "confidence": "high",
                "primary": "MeshReflectorMaterial",
                "primary_reason": (
                    f"meshBasicMaterial on a <{geo}> floor plane — "
                    "MeshReflectorMaterial gives a reflective stage/product surface"
                ),
                "alternative": "meshPhysicalMaterial_matte",
                "alternative_reason": "If reflection is too heavy, use matte physical for a neutral floor",
                "requires_environment": True,
            }
        if geo in HERO_GEOMETRIES:
            return {
                "confidence": "high",
                "primary": "MeshTransmissionMaterial",
                "primary_reason": (
                    f"meshBasicMaterial on a <{geo}> — "
                    "this is almost certainly a decorative hero object; "
                    "MeshTransmissionMaterial glass transforms it dramatically"
                ),
                "alternative": "meshPhysicalMaterial_metal",
                "alternative_reason": "Use polished metal instead if glass doesn't fit the brand palette",
                "requires_environment": True,
            }
        # No geometry detected
        return {
            "confidence": "low",
            "primary": "MeshTransmissionMaterial",
            "primary_reason": (
                "meshBasicMaterial has no lighting — glass is the highest-impact upgrade, "
                "but geometry context could not be determined"
            ),
            "alternative": "meshPhysicalMaterial_matte",
            "alternative_reason": "If the object is structural/UI, prefer matte physical over glass",
            "requires_environment": True,
        }

    if old_mat == "meshStandardMaterial":
        if geo in FLOOR_GEOMETRIES:
            return {
                "confidence": "high",
                "primary": "MeshReflectorMaterial",
                "primary_reason": (
                    f"meshStandardMaterial on a <{geo}> floor — "
                    "MeshReflectorMaterial adds real-time reflections that sell product quality"
                ),
                "alternative": "meshPhysicalMaterial_matte",
                "alternative_reason": "Reflector material is expensive on low-end GPUs; matte physical is the safe fallback",
                "requires_environment": True,
            }
        if geo in HERO_GEOMETRIES:
            if has_emissive:
                return {
                    "confidence": "medium",
                    "primary": "meshPhysicalMaterial_metal",
                    "primary_reason": (
                        "meshStandardMaterial with emissive on a hero shape — "
                        "upgrade to meshPhysicalMaterial and keep the emissive props; "
                        "Physical adds clearcoat and iridescence while preserving Bloom pickup"
                    ),
                    "alternative": "MeshTransmissionMaterial",
                    "alternative_reason": "Use glass instead if the glow should come through a transparent surface",
                    "requires_environment": True,
                }
            return {
                "confidence": "medium",
                "primary": "MeshTransmissionMaterial",
                "primary_reason": (
                    f"meshStandardMaterial on a <{geo}> hero object — "
                    "transmission glass is higher visual impact; verify the object isn't functional UI"
                ),
                "alternative": "meshPhysicalMaterial_metal",
                "alternative_reason": "Use polished metal if the object should feel solid rather than ethereal",
                "requires_environment": True,
            }
        return {
            "confidence": "medium",
            "primary": "meshPhysicalMaterial_matte",
            "primary_reason": (
                "meshStandardMaterial → meshPhysicalMaterial is always a safe upgrade "
                "(Physical is a superset: adds clearcoat, iridescence, transmission)"
            ),
            "alternative": "MeshTransmissionMaterial",
            "alternative_reason": "Consider glass if geometry context suggests a decorative/transparent element",
            "requires_environment": True,
        }

    if old_mat in ("meshLambertMaterial", "meshPhongMaterial"):
        return {
            "confidence": "high",
            "primary": "meshPhysicalMaterial_matte",
            "primary_reason": (
                f"{old_mat} uses an outdated shading model — "
                "meshPhysicalMaterial uses correct PBR roughness/metalness"
            ),
            "alternative": "MeshTransmissionMaterial",
            "alternative_reason": "Use glass if the mesh is a decorative hero object",
            "requires_environment": True,
        }

    return {
        "confidence": "low",
        "primary": "meshPhysicalMaterial_matte",
        "primary_reason": "Generic PBR upgrade — verify geometry context for a more specific recommendation",
        "alternative": "MeshTransmissionMaterial",
        "alternative_reason": "Consider glass for decorative/hero objects",
        "requires_environment": True,
    }


# ── Main audit ────────────────────────────────────────────────────────────────

def audit(root_str: str) -> dict:
    root = Path(root_str).resolve()
    results = []

    for fpath in root.rglob("*.tsx"):
        if is_excluded(fpath):
            continue
        content = read_file(fpath)
        if not content:
            continue
        rel = fpath.relative_to(root).as_posix()
        lines = content.splitlines()

        file_findings = []

        for old_mat, pat in OLD_MATERIALS.items():
            for m in pat.finditer(content):
                mat_pos = m.start()
                mat_line = content[:mat_pos].count("\n") + 1

                component_name = extract_component_name(content, mat_line)
                geo = extract_geometry_near_material(content, mat_pos)
                region = content[max(0, mat_pos - 400) : mat_pos + 400]
                rec = build_recommendation(old_mat, geo, region)

                primary_key = rec["primary"]
                alt_key     = rec.get("alternative")

                file_findings.append({
                    "material_found":    old_mat,
                    "component":         component_name,
                    "line":              mat_line,
                    "geometry_detected": geo,
                    "confidence":        rec["confidence"],
                    "primary_replacement": {
                        "material":   primary_key,
                        "reason":     rec["primary_reason"],
                        "import":     IMPORT_LINES.get(primary_key, ""),
                        "snippet":    REPLACEMENT_SNIPPETS.get(primary_key, ""),
                        "requires_environment": rec.get("requires_environment", True),
                    },
                    "alternative_replacement": {
                        "material": alt_key,
                        "reason":   rec.get("alternative_reason", ""),
                        "import":   IMPORT_LINES.get(alt_key or "", ""),
                        "snippet":  REPLACEMENT_SNIPPETS.get(alt_key or "", ""),
                    } if alt_key else None,
                })

        if file_findings:
            results.append({"file": rel, "findings": file_findings})

    output = {
        "total_files_with_upgradeable_materials": len(results),
        "files": results,
    }
    print(json.dumps(output, indent=2))
    return output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 audit_materials.py <project-root>", file=sys.stderr)
        sys.exit(1)
    audit(sys.argv[1])
