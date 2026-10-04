#!/usr/bin/env bash
# Same as Cursor `create_azdo_pr.sh` — see scripts/create_azdo_pr.py
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$ROOT/scripts/create_azdo_pr.py" "$@"
