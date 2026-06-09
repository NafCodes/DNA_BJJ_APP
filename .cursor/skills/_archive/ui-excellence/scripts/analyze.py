#!/usr/bin/env python3
"""
analyze.py — Scans a React/Next.js project (Lovable export) and produces a
structured JSON report for the ui-upgrade skill.

Output shape:
{
  component_inventory: { pages, layouts, canvas_components, ui_primitives,
                         feature_components, unknown },
  canvas_audit:   { <rel-path>: { has_dpr_cap, has_aces_toning, has_environment,
                                  has_postprocessing, has_float_animation,
                                  has_orbit_controls, material_types,
                                  performance_violations } },
  animation_audit: { <rel-path>: { has_framer_motion, has_page_transition,
                                   has_scroll_animation, static_lists } },
  missing_packages: [],
  vite_leaks: [{ file, line, match }],
  upgrade_order: []
}

Usage: python3 analyze.py <project-root>
"""

import sys
import os
import re
import json
from pathlib import Path


# ── Desired packages ──────────────────────────────────────────────────────────

DESIRED_PACKAGES = [
    "@react-three/fiber",
    "@react-three/drei",
    "@react-three/postprocessing",
    "framer-motion",
    "three",
    "zustand",
]

# ── Patterns ──────────────────────────────────────────────────────────────────

CANVAS_PAT          = re.compile(r'<Canvas\b')
DPR_PAT             = re.compile(r'\bdpr\s*=')
ACES_PAT            = re.compile(r'ACESFilmicToneMapping')
ENVIRONMENT_PAT     = re.compile(r'<Environment\b')
POSTPROCESSING_PAT  = re.compile(r'EffectComposer|@react-three/postprocessing')
FLOAT_PAT           = re.compile(r'<Float\b')
ORBIT_PAT           = re.compile(r'<OrbitControls\b')
USE_FRAME_PAT       = re.compile(r'useFrame\s*\(')
DYNAMIC_IMPORT_PAT  = re.compile(r"dynamic\s*\(\s*\(\s*\)\s*=>", re.DOTALL)
DISPOSE_PAT         = re.compile(r'\.dispose\(\)')
VITE_ENV_PAT        = re.compile(r'import\.meta\.env\.VITE_\w+')
USE_EFFECT_PAT      = re.compile(r'\buseEffect\s*\(')
SUPABASE_FETCH_PAT  = re.compile(r'supabase\.|fetch\(|axios\.')

MATERIAL_NAMES = [
    "meshStandardMaterial",
    "meshBasicMaterial",
    "meshLambertMaterial",
    "meshPhongMaterial",
    "meshPhysicalMaterial",
    "MeshTransmissionMaterial",
    "MeshReflectorMaterial",
]

FRAMER_IMPORT_PAT       = re.compile(r"from\s+['\"]framer-motion['\"]")
MOTION_COMPONENT_PAT    = re.compile(r'<motion\.')
ANIMATE_PRESENCE_PAT    = re.compile(r'<AnimatePresence\b|AnimatePresence')
USE_SCROLL_PAT          = re.compile(r'\buseScroll\b|\buseInView\b|\buseTransform\b')
STATIC_LIST_PAT         = re.compile(r'\.(map|filter)\s*\([^)]*\)\s*\.map\s*\(|<(?:ul|ol)\b')


# ── Helpers ───────────────────────────────────────────────────────────────────

def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def is_excluded(path: Path) -> bool:
    excluded = {"node_modules", ".git", "dist", "build", ".next", "coverage", ".claude", ".cursor"}
    return any(part in excluded for part in path.parts)


def tsx_files(root: Path):
    for ext in ("*.tsx", "*.ts", "*.jsx", "*.js"):
        for f in root.rglob(ext):
            if not is_excluded(f):
                yield f


def check_packages(root: Path) -> list[str]:
    pkg_path = root / "package.json"
    if not pkg_path.exists():
        return DESIRED_PACKAGES[:]
    try:
        pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
    except Exception:
        return DESIRED_PACKAGES[:]
    all_deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    return [p for p in DESIRED_PACKAGES if p not in all_deps]


# ── useFrame body extractor ───────────────────────────────────────────────────

def extract_useframe_bodies(content: str) -> list[str]:
    """
    Find every useFrame(... => { ... }) call and return the body strings.
    Uses brace counting so it correctly handles nested braces and multiline
    callbacks — avoids false positives from regex-only approach.
    """
    bodies = []
    search_from = 0
    # Match: useFrame( then optional whitespace, then a callback opening brace
    # Handles: useFrame((_state, delta) => {  or  useFrame(() => {
    pat = re.compile(r'useFrame\s*\([^{]*\{', re.DOTALL)
    while search_from < len(content):
        m = pat.search(content, search_from)
        if not m:
            break
        body_start = m.end()
        depth = 1
        j = body_start
        while j < len(content) and depth > 0:
            c = content[j]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
            j += 1
        bodies.append(content[body_start : j - 1])
        search_from = j
    return bodies


def has_setstate_in_useframe(content: str) -> bool:
    """Only flags setState if it appears inside a useFrame callback body."""
    for body in extract_useframe_bodies(content):
        if re.search(r'\bset[A-Z]\w*\s*\(', body):
            return True
    return False


# ── Line-number helpers ───────────────────────────────────────────────────────

def find_line(content: str, pat: re.Pattern) -> int | None:
    for i, line in enumerate(content.splitlines(), 1):
        if pat.search(line):
            return i
    return None


def find_all_vite_leaks(content: str, rel: str) -> list[dict]:
    leaks = []
    for i, line in enumerate(content.splitlines(), 1):
        for m in VITE_ENV_PAT.finditer(line):
            leaks.append({"file": rel, "line": i, "match": m.group()})
    return leaks


# ── Component classification ──────────────────────────────────────────────────

def classify(fpath: Path, root: Path, content: str) -> str:
    rel_parts = fpath.relative_to(root).parts

    if CANVAS_PAT.search(content):
        return "canvas_component"

    # layout.tsx or layout.jsx anywhere in the tree
    if fpath.stem == "layout":
        return "layout"

    # Under app/ or pages/ directory → page
    if rel_parts and rel_parts[0] in ("app", "pages"):
        # Skip sub-files that are not route files (e.g. _components)
        if fpath.suffix in (".tsx", ".jsx") and not fpath.stem.startswith("_"):
            return "page"

    # Under components/ui/
    if "ui" in rel_parts and "components" in rel_parts:
        return "ui_primitive"

    # Feature component: has useEffect AND data fetching
    if USE_EFFECT_PAT.search(content) and SUPABASE_FETCH_PAT.search(content):
        return "feature_component"

    if "<" in content and re.search(r'export\s+(default\s+)?(function|const|class)', content):
        return "unknown"

    return "unknown"


# ── Canvas audit ──────────────────────────────────────────────────────────────

def audit_canvas(content: str) -> dict:
    material_types = [m for m in MATERIAL_NAMES
                      if re.search(rf'<{re.escape(m)}\b|(?<!\w){re.escape(m[0].upper() + m[1:])}\b', content)]

    violations = []
    if USE_FRAME_PAT.search(content) and has_setstate_in_useframe(content):
        line = find_line(content, re.compile(r'\bset[A-Z]\w*\s*\('))
        violations.append({
            "issue": "setState called inside useFrame — use refs instead",
            "line": line,
        })
    if USE_FRAME_PAT.search(content) and not DISPOSE_PAT.search(content):
        violations.append({
            "issue": "useFrame present but no .dispose() cleanup — memory leak on unmount",
            "line": None,
        })
    if not DYNAMIC_IMPORT_PAT.search(content):
        violations.append({
            "issue": "Canvas component not wrapped in next/dynamic with ssr:false — will crash on SSR",
            "line": None,
        })

    return {
        "has_dpr_cap":        bool(DPR_PAT.search(content)),
        "has_aces_toning":    bool(ACES_PAT.search(content)),
        "has_environment":    bool(ENVIRONMENT_PAT.search(content)),
        "has_postprocessing": bool(POSTPROCESSING_PAT.search(content)),
        "has_float_animation": bool(FLOAT_PAT.search(content)),
        "has_orbit_controls": bool(ORBIT_PAT.search(content)),
        "material_types":     material_types,
        "performance_violations": violations,
    }


# ── Animation audit ───────────────────────────────────────────────────────────

def audit_animation(content: str) -> dict:
    static_lists = []
    for m in STATIC_LIST_PAT.finditer(content):
        ctx = content[max(0, m.start() - 40) : m.end() + 40].replace("\n", " ")
        static_lists.append(ctx.strip())

    return {
        "has_framer_motion":   bool(FRAMER_IMPORT_PAT.search(content)),
        "has_page_transition": bool(ANIMATE_PRESENCE_PAT.search(content) or MOTION_COMPONENT_PAT.search(content)),
        "has_scroll_animation": bool(USE_SCROLL_PAT.search(content)),
        "static_lists":        static_lists[:5],
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def analyze(root_str: str) -> dict:
    root = Path(root_str).resolve()
    if not root.exists():
        return {"error": f"Path not found: {root_str}"}

    inventory: dict[str, list[str]] = {
        "pages": [], "layouts": [], "canvas_components": [],
        "ui_primitives": [], "feature_components": [], "unknown": [],
    }
    canvas_audit: dict[str, dict] = {}
    animation_audit: dict[str, dict] = {}
    vite_leaks: list[dict] = []

    files = list(tsx_files(root))

    for fpath in files:
        content = read_file(fpath)
        rel = fpath.relative_to(root).as_posix()

        kind = classify(fpath, root, content)
        key_map = {
            "page": "pages",
            "layout": "layouts",
            "canvas_component": "canvas_components",
            "ui_primitive": "ui_primitives",
            "feature_component": "feature_components",
            "unknown": "unknown",
        }
        inventory[key_map[kind]].append(rel)

        if kind == "canvas_component":
            canvas_audit[rel] = audit_canvas(content)

        if kind in ("page", "feature_component", "layout"):
            anim = audit_animation(content)
            if not anim["has_framer_motion"] or anim["static_lists"]:
                animation_audit[rel] = anim

        leaks = find_all_vite_leaks(content, rel)
        vite_leaks.extend(leaks)

    missing_packages = check_packages(root)

    # ── Build upgrade_order ────────────────────────────────────────────────────
    seen: set[str] = set()
    upgrade_order: list[str] = []

    def add(f: str):
        if f not in seen:
            seen.add(f)
            upgrade_order.append(f)

    # 1) VITE leaks first
    for leak in vite_leaks:
        add(leak["file"])

    # 2) Performance violations
    for rel, audit in canvas_audit.items():
        if audit["performance_violations"]:
            add(rel)

    # 3) All canvas components (even without violations)
    for rel in inventory["canvas_components"]:
        add(rel)

    # 4) Pages (for page transitions)
    for rel in inventory["pages"]:
        add(rel)

    # 5) Feature components (stagger / scroll reveals)
    for rel in inventory["feature_components"]:
        add(rel)

    # 6) UI primitives last
    for rel in inventory["ui_primitives"]:
        add(rel)

    report = {
        "component_inventory": inventory,
        "canvas_audit": canvas_audit,
        "animation_audit": animation_audit,
        "missing_packages": missing_packages,
        "vite_leaks": vite_leaks,
        "upgrade_order": upgrade_order,
        "summary": {
            "total_tsx_files": len(files),
            "canvas_components": len(inventory["canvas_components"]),
            "pages": len(inventory["pages"]),
            "feature_components": len(inventory["feature_components"]),
            "missing_packages": missing_packages,
            "vite_leak_count": len(vite_leaks),
            "files_needing_animation": len(animation_audit),
            "canvas_with_violations": sum(
                1 for a in canvas_audit.values() if a["performance_violations"]
            ),
        },
    }

    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze.py <project-root>", file=sys.stderr)
        sys.exit(1)
    analyze(sys.argv[1])
