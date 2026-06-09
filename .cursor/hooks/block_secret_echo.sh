#!/usr/bin/env bash
# Block shell commands that echo or print secret material.
input=$(cat)
command=$(echo "$input" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('command',''))" 2>/dev/null || echo "")

if [[ -z "$command" ]]; then
  exit 0
fi

# Block echo/print/curl of literal JWTs or secret key values
if echo "$command" | grep -qE '(echo|printf|curl.*eyJ[A-Za-z0-9_-]{10,}\.)'; then
  echo '{"permission":"deny","userMessage":"Blocked: command may expose Supabase secrets. Use env vars instead of echoing keys."}'
  exit 0
fi

exit 0
