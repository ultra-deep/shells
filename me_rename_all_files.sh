#!/usr/bin/env bash

pattern="$1"

if [[ -z "$pattern" ]]; then
  echo "Usage: $0 PATTERN"
  exit 1
fi

for file in *; do
  [[ -f "$file" ]] || continue

  name="${file%.*}"
  ext="${file##*.}"

  newname=""

  for ((i=0; i<${#name}; i++)); do
    p="${pattern:i:1}"
    c="${name:i:1}"

    if [[ "$p" == "$c" || "$p" == "@" ]]; then
      newname+="$c"
    fi
  done

  if [[ -n "$newname" ]]; then
    mv -- "$file" "$newname.$ext"
    echo "$file -> $newname.$ext"
  fi
done

