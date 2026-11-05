#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/.build/logs"
cd "$ROOT"
python3 "$ROOT/support/prepare.py" --if-needed
xcodebuild -project objc.xcodeproj -scheme objcDebug -configuration Debug \
  -destination 'generic/platform=macOS' -derivedDataPath "$ROOT/.build" build "$@" \
  2>&1 | tee "$ROOT/.build/logs/build.log" | xcbeautify
