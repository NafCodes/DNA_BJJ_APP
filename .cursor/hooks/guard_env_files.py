#!/usr/bin/env python3
"""Warn when env files are edited."""
import json
import re
import sys
from pathlib import Path

SECRET_PATTERNS = [
    (re.compile(r"NEXT_PUBLIC_.*(SERVICE_ROLE|SECRET|PASSWORD|TOKEN|PRIVATE)", re.I),
     "NEXT_PUBLIC_ must never prefix secrets — use server-only env vars."),
    (re.compile(r"^SUPABASE_SERVICE_ROLE", re.M),
     "Service role key is server-only — never import in client code."),
]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    file_path = payload.get("file_path") or payload.get("path") or ""
    content = payload.get("content") or payload.get("new_string") or ""

    name = Path(file_path).name.lower()
    if not any(name.startswith(p) for p in (".env", ".env.")):
        return 0

    warnings = ["Never commit .env files — verify .gitignore includes .env*"]
    for pattern, msg in SECRET_PATTERNS:
        if content and pattern.search(content):
            warnings.append(msg)

    print(json.dumps({
        "additional_context": " ".join(warnings),
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
