#!/usr/bin/env python3
"""Print the complete current runtime diff against the selected objc4 submodule."""
import difflib
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
original, working = root / 'upstream/objc4/runtime', root / 'runtime'
files = {p.relative_to(original) for p in original.rglob('*') if p.is_file()}
files |= {p.relative_to(working) for p in working.rglob('*') if p.is_file() and p.name != '.DS_Store'}
for relative in sorted(files):
    a, b = original / relative, working / relative
    before = a.read_text().splitlines(True) if a.is_file() else []
    after = b.read_text().splitlines(True) if b.is_file() else []
    name = 'runtime/' + str(relative)
    sys.stdout.writelines(difflib.unified_diff(before, after,
        fromfile='a/' + name if a.is_file() else '/dev/null',
        tofile='b/' + name if b.is_file() else '/dev/null'))
