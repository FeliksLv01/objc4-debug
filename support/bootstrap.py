#!/usr/bin/env python3
"""Initialize the parent repository's pinned submodules and prepare patched sources."""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
subprocess.run(['git', '-C', str(root), 'submodule', 'update', '--init', '--recursive', '--jobs', '4'], check=True)
subprocess.run([sys.executable, str(root / 'support/prepare.py')], check=True)
