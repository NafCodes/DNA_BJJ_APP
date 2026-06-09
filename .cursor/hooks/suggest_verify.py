#!/usr/bin/env python3
"""Suggest verification after backend file edits."""
import json
import sys
from pathlib import Path

BACKEND_PATTERNS = ("src/routes/", "src/middleware/", "src/lib/", "src/index.js")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    # stop hook may include edited files or conversation context
    files = payload.get("files") or payload.get("edited_files") or []
    if isinstance(files, list) and files:
        touched = any(
            any(p in str(f) for p in BACKEND_PATTERNS)
            for f in files
        )
    else:
        touched = False

    if touched:
        print(json.dumps({
            "followup_message": (
                "Backend files were edited. Verify with: "
                "`npm run dev` then `curl http://localhost:3000/health`"
            ),
        }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
