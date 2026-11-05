#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EXE="$ROOT/.build/Build/Products/Debug/objcDebug"
if [[ ! -x "$EXE" ]]; then "$ROOT/support/build.sh"; fi
xcrun lldb "$EXE" \
  -o 'settings set target.disable-aslr false' \
  -o "settings set target.env-vars \"DYLD_LIBRARY_PATH=$ROOT/.build/staging/usr/lib:$ROOT/.build/Build/Products/Debug\"" \
  -o 'breakpoint set -n objc_setAssociatedObject -s libobjc.A.dylib' "$@"
