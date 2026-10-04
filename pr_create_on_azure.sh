#!/usr/bin/env bash
# Same as Cursor `pr_create_on_azure.sh` — see scripts/pr_create_on_azure.py
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$ROOT/pr_create_on_azure.py" "$@"
