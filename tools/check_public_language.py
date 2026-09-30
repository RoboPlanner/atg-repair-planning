"""Check English presentation files, while explicitly retaining frozen originals.

This inspects current tracked/unignored UTF-8 text, including Unicode escapes.
It does not rewrite Git history or claim to OCR images or inspect binary media.
"""
from pathlib import Path
import html
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ARCHIVES = ('reproduction/', 'simulation/', 'simulation_expanded/')
HAN = re.compile('[' + ''.join(chr(a) + '-' + chr(b) for a, b in
                 [(0x3400, 0x4dbf), (0x4e00, 0x9fff), (0x20000, 0x2fa1f)]) + ']')


def check():
    names = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=ROOT).decode('utf-8').split('\0')
    issues, preserved = [], []
    checked = 0
    for name in sorted(set(names) - {''}):
        path = ROOT / name
        if not path.is_file():
            continue
        try:
            text = path.read_text('utf-8-sig')
        except (UnicodeDecodeError, ValueError):
            continue
        if '\0' in text:
            continue
        decoded = html.unescape(re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m[1], 16)), text))
        if HAN.search(decoded) or HAN.search(name):
            if name.startswith(ARCHIVES):
                preserved.append(name)
            else:
                issues.append(name)
        if not name.startswith(ARCHIVES):
            checked += 1
    report = {'checked_English_text_files': checked, 'issues': issues,
              'original_archive_files_retaining_source_language': len(preserved),
              'scope': 'Current text surfaces and labelled English copies; frozen originals deliberately retained.'}
    print(json.dumps(report, indent=2))
    if issues:
        raise SystemExit(1)


if __name__ == '__main__':
    check()
