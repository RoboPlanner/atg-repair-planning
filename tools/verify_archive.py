"""Verify the unchanged supplementary archive and all manifest-listed files."""
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[1]
ZIP_HASH = '922881a57e08e3cc1a0f28e283e2837dabfb486d1c612fc282feb4575a8f0f4a'

def verify():
    manifest = json.loads((ROOT/'reproduction/MANIFEST_SHA256.json').read_text(encoding='utf-8'))
    failures = []
    for name, expected in manifest.items():
        p = ROOT/'reproduction'/name
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != expected:
            failures.append(name)
    archive = ROOT/'docs/assets/downloads/ATG_reproduction_v7_70.zip'
    if not archive.is_file() or hashlib.sha256(archive.read_bytes()).hexdigest() != ZIP_HASH:
        failures.append('supplementary ZIP')
    if failures:
        raise SystemExit('Integrity failure: ' + ', '.join(failures))
    print(f'PASS: {len(manifest)} manifest files and supplementary ZIP match their frozen SHA-256 values.')

if __name__ == '__main__':
    verify()
