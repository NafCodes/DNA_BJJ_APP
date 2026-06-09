#!/usr/bin/env python3
"""Warn when prompts contain JWT-like secrets."""
import json
import re
import sys

JWT_PATTERN = re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")
SECRET_PATTERN = re.compile(r"(SERVICE_ROLE|sb_secret_|SUPABASE_.*KEY\s*=)", re.I)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    prompt = payload.get("prompt") or payload.get("text") or ""
    if not prompt:
        return 0

    warnings = []
    if JWT_PATTERN.search(prompt):
        warnings.append("Prompt may contain a JWT/API key — avoid pasting secrets into chat.")
    if SECRET_PATTERN.search(prompt):
        warnings.append("Prompt references secret env vars — use placeholders instead.")

    if warnings:
        print(json.dumps({"additional_context": " ".join(warnings)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
