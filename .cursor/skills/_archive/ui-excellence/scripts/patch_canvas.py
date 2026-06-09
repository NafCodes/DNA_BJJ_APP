#!/usr/bin/env python3
"""
patch_canvas.py — JSX-aware patcher for R3F Canvas components.

Uses a state machine to correctly handle multiline Canvas opening tags
(common in Lovable output). Injects missing props and EffectComposer block
only where they belong.

Dry-run by default (prints diff to stderr, patched source to stdout).
Pass --write to write in-place.

Usage:
  python3 patch_canvas.py <path-to-tsx>           # dry-run
  python3 patch_canvas.py <path-to-tsx> --write   # write in-place
"""

import sys
import re
import difflib
from pathlib import Path
from typing import NamedTuple


# ── What to inject ────────────────────────────────────────────────────────────

CANVAS_PROPS_TO_ADD = [
    ('dpr',    'dpr={[1, 2]}'),
    ('gl=',    'gl={{ antialias: true, toneMapping: ACESFilmicToneMapping, toneMappingExposure: 1.1 }}'),
    ('camera=', 'camera={{ position: [0, 0, 6], fov: 45, near: 0.1, far: 100 }}'),
]

EFFECT_COMPOSER_BLOCK = """\
      <Environment preset="city" />
      <EffectComposer>
        <Bloom luminanceThreshold={0.85} intensity={1.2} mipmapBlur />
        <ChromaticAberration offset={new Vector2(0.001, 0.001)} />
        <Vignette darkness={0.4} offset={0.3} />
      </EffectComposer>"""

# Named imports we need per package
DREI_NEEDS     = {"Environment", "Float", "Sparkles"}
POST_NEEDS     = {"EffectComposer", "Bloom", "ChromaticAberration", "Vignette"}
THREE_NEEDS    = {"ACESFilmicToneMapping", "Vector2"}


# ── Import merger ─────────────────────────────────────────────────────────────

class ImportBlock(NamedTuple):
    line_indices: list[int]    # 0-based indices in the lines list
    names: set[str]            # currently imported names


def parse_named_imports(lines: list[str], package: str) -> ImportBlock | None:
    """
    Find `import { ... } from '<package>'` (possibly multiline) and return
    the ImportBlock. Returns None if no such import exists.
    """
    pkg_pat = re.compile(
        r"""import\s*\{([^}]*)\}\s*from\s*['"]""" + re.escape(package) + r"""['"]""",
        re.DOTALL,
    )
    source = "\n".join(lines)
    m = pkg_pat.search(source)
    if not m:
        return None

    names_str = m.group(1)
    names = {n.strip().split(" as ")[0].strip() for n in names_str.split(",") if n.strip()}

    # Find which line indices span this match
    start_pos = m.start()
    end_pos = m.end()
    char = 0
    start_line = end_line = None
    for i, line in enumerate(lines):
        line_end = char + len(line) + 1  # +1 for \n
        if start_line is None and char <= start_pos < line_end:
            start_line = i
        if end_line is None and char <= end_pos <= line_end:
            end_line = i
            break
        char = line_end

    if start_line is None or end_line is None:
        return None

    return ImportBlock(line_indices=list(range(start_line, end_line + 1)), names=names)


def merge_imports(lines: list[str], package: str, needed: set[str]) -> tuple[list[str], list[str]]:
    """
    Add `needed` names to the existing import from `package`, or create a new
    import statement after the last existing import line.
    Returns (updated_lines, change_descriptions).
    """
    changes = []
    block = parse_named_imports(lines, package)

    if block:
        existing = block.names
        to_add = needed - existing
        if not to_add:
            return lines, []
        merged = sorted(existing | to_add)
        new_import = f"import {{ {', '.join(merged)} }} from '{package}';"
        new_lines = lines[:]
        # Replace the span with a single line
        new_lines[block.line_indices[0]] = new_import
        for idx in reversed(block.line_indices[1:]):
            new_lines.pop(idx)
        changes.append(f"Merged into existing {package} import: added {sorted(to_add)}")
        return new_lines, changes
    else:
        # Find last import line and insert after it
        last_import = 0
        for i, line in enumerate(lines):
            if re.match(r'\s*import\b', line):
                last_import = i
        new_import = f"import {{ {', '.join(sorted(needed))} }} from '{package}';"
        new_lines = lines[: last_import + 1] + [new_import] + lines[last_import + 1 :]
        changes.append(f"Added import: {new_import}")
        return new_lines, changes


# ── String-in-JSX-attribute guard ─────────────────────────────────────────────

def is_inside_string(line: str, pos: int) -> bool:
    """
    Crude check: count unescaped quotes before `pos`.
    If the count of `"` chars before `pos` is odd, we're inside a string.
    Handles the common case; not a full JSX parser.
    """
    before = line[:pos]
    # Remove escaped quotes
    before = before.replace('\\"', "").replace("\\'", "")
    return before.count('"') % 2 == 1


# ── Canvas state machine ───────────────────────────────────────────────────────

def patch(source: str) -> tuple[str, list[str]]:
    """
    Patch the Canvas component in `source`.
    Returns (patched_source, list_of_human_readable_changes).
    """
    lines = source.splitlines()
    changes: list[str] = []

    # ── Step 1: Fix imports ───────────────────────────────────────────────────

    # Determine what's already imported across the whole file
    full = "\n".join(lines)
    already_drei     = set()
    already_post     = set()
    already_three    = set()

    block_drei  = parse_named_imports(lines, "@react-three/drei")
    block_post  = parse_named_imports(lines, "@react-three/postprocessing")
    block_three = parse_named_imports(lines, "three")

    if block_drei:  already_drei  = block_drei.names
    if block_post:  already_post  = block_post.names
    if block_three: already_three = block_three.names

    drei_needed  = DREI_NEEDS  - already_drei
    post_needed  = POST_NEEDS  - already_post
    three_needed = THREE_NEEDS - already_three

    if drei_needed:
        lines, c = merge_imports(lines, "@react-three/drei", DREI_NEEDS)
        changes.extend(c)
    if post_needed:
        lines, c = merge_imports(lines, "@react-three/postprocessing", POST_NEEDS)
        changes.extend(c)
    if three_needed:
        lines, c = merge_imports(lines, "three", THREE_NEEDS)
        changes.extend(c)

    # ── Step 2: State-machine Canvas patch ───────────────────────────────────

    BEFORE_CANVAS     = "BEFORE_CANVAS"
    INSIDE_CANVAS_TAG = "INSIDE_CANVAS_TAG"
    INSIDE_CANVAS_BODY = "INSIDE_CANVAS_BODY"
    AFTER_CANVAS      = "AFTER_CANVAS"

    state = BEFORE_CANVAS
    out: list[str] = []
    canvas_tag_lines: list[str] = []   # accumulates the opening tag lines
    props_in_tag = ""                  # concat of canvas_tag_lines for prop checking
    effect_composer_injected = False

    # Re-read full source after import edits
    full = "\n".join(lines)
    effect_already_present = bool(re.search(r'<EffectComposer\b', full))
    environment_already_present = bool(re.search(r'<Environment\b', full))

    for line in lines:
        stripped = line.strip()

        if state == BEFORE_CANVAS:
            if re.search(r'<Canvas\b', line):
                state = INSIDE_CANVAS_TAG
                canvas_tag_lines = [line]
                props_in_tag = line
            else:
                out.append(line)

        elif state == INSIDE_CANVAS_TAG:
            canvas_tag_lines.append(line)
            props_in_tag += "\n" + line

            # Find a `>` that's NOT inside a string attribute value
            gt_idx = line.find(">")
            if gt_idx != -1 and not is_inside_string(line, gt_idx):
                # The opening tag is now complete.
                # Determine what props to add.
                props_to_inject: list[str] = []
                for (check_str, prop_line) in CANVAS_PROPS_TO_ADD:
                    if check_str not in props_in_tag:
                        props_to_inject.append(prop_line)
                        changes.append(f"Canvas: injected prop — {prop_line.strip()}")

                if props_to_inject:
                    # Insert props before the closing > of the tag.
                    # Find the last tag line and insert before its >
                    last_tag_line = canvas_tag_lines[-1]
                    gt_pos = last_tag_line.rfind(">")
                    # Detect indentation from the <Canvas line
                    indent = len(canvas_tag_lines[0]) - len(canvas_tag_lines[0].lstrip())
                    prop_indent = " " * (indent + 2)
                    injected = (
                        last_tag_line[:gt_pos]
                        + "\n"
                        + "\n".join(f"{prop_indent}{p}" for p in props_to_inject)
                        + "\n"
                        + prop_indent[:-2]  # restore original indent for >
                        + last_tag_line[gt_pos:]
                    )
                    canvas_tag_lines[-1] = injected

                # Self-closing canvas (<Canvas ... />) is unusual but handle it
                if "/>" in line[: gt_idx + 1]:
                    out.extend(canvas_tag_lines)
                    state = AFTER_CANVAS
                else:
                    out.extend(canvas_tag_lines)
                    state = INSIDE_CANVAS_BODY

        elif state == INSIDE_CANVAS_BODY:
            # Check for closing tag
            if re.match(r'\s*</Canvas\s*>', stripped):
                # Inject EffectComposer block before </Canvas> if not already present
                if not effect_already_present and not effect_composer_injected:
                    indent = len(line) - len(line.lstrip())
                    block_indent = " " * indent
                    # Build the block with correct indentation
                    block_lines = EFFECT_COMPOSER_BLOCK.splitlines()
                    # EFFECT_COMPOSER_BLOCK uses 6-space indent; adjust to actual
                    reference_indent = 6
                    adjusted = []
                    for bl in block_lines:
                        stripped_bl = bl.lstrip()
                        original_extra = len(bl) - len(stripped_bl)
                        extra = original_extra - reference_indent
                        adjusted.append(block_indent + " " * max(0, extra) + stripped_bl)
                    out.extend(adjusted)
                    effect_composer_injected = True
                    changes.append("Canvas: injected <Environment> + <EffectComposer> block before </Canvas>")
                out.append(line)
                state = AFTER_CANVAS
            else:
                out.append(line)

        else:  # AFTER_CANVAS
            out.append(line)

    return "\n".join(out), changes


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python3 patch_canvas.py <tsx-file> [--write]", file=sys.stderr)
        sys.exit(1)

    write_mode = "--write" in args
    file_args = [a for a in args if not a.startswith("--")]
    if not file_args:
        print("Error: no file specified", file=sys.stderr)
        sys.exit(1)

    fpath = Path(file_args[0])
    if not fpath.exists():
        print(f"File not found: {fpath}", file=sys.stderr)
        sys.exit(1)

    original = fpath.read_text(encoding="utf-8")
    patched, changes = patch(original)

    if not changes:
        print(f"[patch_canvas] No changes needed for {fpath}", file=sys.stderr)
        if not write_mode:
            print(original, end="")
        sys.exit(0)

    # Print human-readable summary
    print(f"\n[patch_canvas] {fpath}", file=sys.stderr)
    print(f"Changes ({len(changes)}):", file=sys.stderr)
    for c in changes:
        print(f"  + {c}", file=sys.stderr)

    if write_mode:
        fpath.write_text(patched, encoding="utf-8")
        print(f"\n[patch_canvas] Written in-place: {fpath}", file=sys.stderr)
        # Print unified diff to stderr for review
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            patched.splitlines(keepends=True),
            fromfile=str(fpath),
            tofile=str(fpath) + " (patched)",
            n=3,
        )
        sys.stderr.writelines(diff)
    else:
        print("[patch_canvas] Dry-run. Pass --write to apply.", file=sys.stderr)
        print(patched, end="")

    # Remind about dynamic import
    print(
        f"\n[patch_canvas] Remember to wrap the import in the parent page:\n"
        f"  import dynamic from 'next/dynamic'\n"
        f"  const Scene = dynamic(() => import('@/components/{fpath.stem}'), {{ ssr: false }})",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
