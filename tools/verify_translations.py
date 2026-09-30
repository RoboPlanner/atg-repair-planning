"""Verify English reading copies against unchanged frozen source files.

Dataset checks compare every record and field. These translations are not
replacement benchmark inputs; run experiments from the original archives.
"""
from pathlib import Path
from urllib.parse import unquote
import csv
import hashlib
import io
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / 'translations/en'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_data(path, kind):
    text = path.read_text('utf-8-sig')
    if kind.startswith('CSV'):
        return list(csv.reader(io.StringIO(text)))
    if kind.startswith('JSONL'):
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    return json.loads(text)


def compare(original, translated, substitutions, path='', seen=None):
    if seen is None:
        seen = set()
    assert type(original) is type(translated), ('Type changed', path)
    if isinstance(original, dict):
        assert list(original) == list(translated), ('Keys changed', path)
        for key in original:
            part = key.replace('~', '~0').replace('/', '~1')
            compare(original[key], translated[key], substitutions, path + '/' + part, seen)
    elif isinstance(original, list):
        assert len(original) == len(translated), ('Length changed', path)
        for i, (a, b) in enumerate(zip(original, translated)):
            compare(a, b, substitutions, path + '/' + str(i), seen)
    elif path in substitutions:
        record = substitutions[path]
        assert isinstance(original, str), ('Non-string translation', path)
        assert sha(original.encode()) == record['source_text_sha256'], ('Source text changed', path)
        assert translated == record['english_text'], ('Translation changed', path)
        seen.add(path)
    else:
        assert original == translated, ('Unlisted value change', path)
    return seen


def verify():
    manifest = json.loads((EN / 'TRANSLATION_MANIFEST.json').read_text('utf-8'))
    count = 0
    for item in manifest['files']:
        original = ROOT / unquote(item['source_uri'])
        translated = EN / item['translation_path']
        assert sha(original.read_bytes()) == item['source_sha256'], ('Original hash', item['source_uri'])
        assert sha(translated.read_bytes()) == item['translation_sha256'], ('Translation hash', item['translation_path'])
        if 'string_substitutions' in item:
            subs = {s['path']: s for s in item['string_substitutions']}
            assert len(subs) == len(item['string_substitutions']), 'Duplicate substitution path'
            seen = compare(read_data(original, item['kind']), read_data(translated, item['kind']), subs)
            assert seen == set(subs), 'Unused substitution'
            count += len(seen)
        if item.get('checks', {}).get('node_and_schedule_table_rows_byte_identical'):
            rows = lambda p: [line for line in p.read_text('utf-8-sig').splitlines() if re.match(r'\| t\d+ \|', line)]
            assert rows(original) == rows(translated), 'Plan or schedule row changed'
        if item.get('checks', {}).get('numeric_table_cells_preserved'):
            pattern = re.compile(r'(?<![A-Za-z_])\d+(?:\.\d+)?')
            cells = lambda p: [pattern.findall(line) for line in p.read_text('utf-8-sig').splitlines() if line.startswith('|') and pattern.search(line)]
            assert cells(original) == cells(translated), 'Numeric report table changed'
    release = json.loads((ROOT / 'translations/release.json').read_text('utf-8'))
    archive = ROOT / release['archive']
    assert sha(archive.read_bytes()) == release['sha256'], 'English ZIP hash mismatch'
    expected = {p.relative_to(EN).as_posix(): p for p in EN.rglob('*') if p.is_file()}
    with zipfile.ZipFile(archive) as z:
        assert set(z.namelist()) == {'ATG_English_reading_copies_v1/' + name for name in expected}, 'ZIP file list mismatch'
        for name, path in expected.items():
            assert z.read('ATG_English_reading_copies_v1/' + name) == path.read_bytes(), ('ZIP bytes differ', name)
    print(f'PASS: {len(manifest["files"])} English copies; {count} documented string substitutions; '
          'source hashes, dataset structure, non-string values, report tables, plan rows and ZIP verified.')


if __name__ == '__main__':
    verify()
