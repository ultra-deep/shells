#!/bin/bash
# Wrapper for gitrelease_charisma_create_message.py
# Usage examples:
#   ./gitrelease_charisma_create_message
#   ./gitrelease_charisma_create_message p sr dd
#   ./gitrelease_charisma_create_message pr --copy

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/gitrelease_charisma_create_message.py"

if [[ ! -f "$PYTHON_SCRIPT" ]]; then
  echo "Python script not found: $PYTHON_SCRIPT" >&2
  exit 1
fi

exec python3 "$PYTHON_SCRIPT" "$@"
