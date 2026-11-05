#!/usr/bin/env python3
"""Materialize pinned submodules + ordered patches without modifying upstream."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / '.build'
STATE = BUILD / 'prepared.json'


def git(*args, cwd=ROOT):
    return subprocess.check_output(['git', '-C', str(cwd), *args], text=True).strip()


def hashes(base, managed):
    result = {}
    for name in managed:
        path = base / name
        files = sorted(path.rglob('*')) if path.is_dir() else [path]
        for file in files:
            if file.is_file() and file.name != '.DS_Store':
                result[str(file.relative_to(base))] = hashlib.sha256(file.read_bytes()).hexdigest()
    return result


def prepare(if_needed):
    layout = json.loads((ROOT / 'support/source-layout.json').read_text())
    managed = layout + ['dependency']
    series = [line.strip() for line in (ROOT / 'patches/series').read_text().splitlines()
              if line.strip() and not line.lstrip().startswith('#')]
    patches = [ROOT / 'patches' / name for name in series]
    for path in patches:
        if path.parent != ROOT / 'patches' or not path.is_file():
            raise RuntimeError(f'Invalid patch entry: {path}')
    modules = git('config', '-f', '.gitmodules', '--get-regexp', r'^submodule\..*\.path$')
    inputs = {}
    for line in modules.splitlines():
        name = line.split(None, 1)[1]
        path = ROOT / name
        if not (path / '.git').exists():
            raise RuntimeError('Submodules missing. Run: python3 support/bootstrap.py')
        if git('status', '--porcelain', cwd=path):
            raise RuntimeError(f'Upstream has local edits: {name}. Save them before preparing.')
        inputs[name] = git('rev-parse', 'HEAD', cwd=path)
    for name in ['dependency-map.json', 'support/source-layout.json', 'support/prepare.py',
                 'patches/series', *['patches/' + entry for entry in series]]:
        inputs[name] = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    previous = json.loads(STATE.read_text()) if STATE.is_file() else None
    # Normal builds preserve runtime experiments when upstream/patches did not change.
    if if_needed and previous and previous['inputs'] == inputs:
        print('Prepared sources are current.')
        return
    changed = []
    current = {}
    if previous:
        current = hashes(ROOT, previous['managed'])
        changed = sorted(name for name in current.keys() | previous['outputs'].keys()
                         if current.get(name) != previous['outputs'].get(name))
    elif any((ROOT / name).exists() for name in managed):
        raise RuntimeError('Generated sources exist without a manifest. Save or move them before preparing.')

    with tempfile.TemporaryDirectory(prefix='prepare-', dir=BUILD) as temp:
        stage = Path(temp)
        for name in layout:
            src, dst = ROOT / 'upstream/objc4' / name, stage / name
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        for dst, src in json.loads((ROOT / 'dependency-map.json').read_text()).items():
            target = stage / 'dependency' / dst
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / 'upstream' / src, target)
        for patch in patches:
            print(f'Checking and applying {patch.name}', flush=True)
            for option in ('--check', None):
                command = ['git', '-C', str(stage), 'apply', '--no-index', '--whitespace=nowarn']
                if option:
                    command.append(option)
                subprocess.run([*command, str(patch)], check=True)
        outputs = hashes(stage, managed)
        # Adopt an experiment only when the new patches reproduce every edited byte.
        unrecorded = [name for name in changed if current.get(name) != outputs.get(name)]
        if unrecorded:
            raise RuntimeError('Generated sources have local edits; save them as a patch first:\n' +
                               '\n'.join(unrecorded[:20]))
        backup = stage / 'previous'
        backup.mkdir()
        installed, saved = [], []
        try:
            for name in managed:
                target = ROOT / name
                if target.exists() or target.is_symlink():
                    os.replace(target, backup / name)
                    saved.append(name)
                os.replace(stage / name, target)
                installed.append(name)
            record = stage / 'prepared.json'
            record.write_text(json.dumps({'inputs': inputs, 'outputs': outputs, 'managed': managed}, indent=2) + '\n')
            os.replace(record, STATE)
        except BaseException:
            for name in reversed(installed):
                target = ROOT / name
                if target.is_dir() and not target.is_symlink():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            for name in saved:
                os.replace(backup / name, ROOT / name)
            raise
    print('Prepared sources from submodules + patches. Upstream checkouts unchanged.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--if-needed', action='store_true', help='Reuse current generated sources, including local experiments')
    args = parser.parse_args()
    BUILD.mkdir(exist_ok=True)
    with (BUILD / 'prepare.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            prepare(args.if_needed)
        except (RuntimeError, subprocess.CalledProcessError, OSError) as error:
            raise SystemExit(str(error))
