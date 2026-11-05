#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EXE="$ROOT/.build/Build/Products/Debug/objcDebug"
if [[ ! -x "$EXE" ]]; then "$ROOT/support/build.sh"; fi
DYLD_LIBRARY_PATH="$ROOT/.build/staging/usr/lib:$ROOT/.build/Build/Products/Debug" exec "$EXE" "$@"
