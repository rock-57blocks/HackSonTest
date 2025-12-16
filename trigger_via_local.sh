#!/usr/bin/env bash
set -euo pipefail

MESSAGE="${1:-Hello from shell via local server}"

curl -sS -X POST "http://127.0.0.1:8000/trigger" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"${MESSAGE}\"}" | jq . 2>/dev/null || true
