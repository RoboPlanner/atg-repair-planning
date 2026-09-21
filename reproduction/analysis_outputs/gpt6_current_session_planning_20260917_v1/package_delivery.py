"""Create a new, checksum-verified archive without replacing any artifact."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parent
manifest_path = root / 'artifact_manifest.json'
archive_path = root.parent / 'GPT6_current_session_24_tasks_20260917_v1.zip'
if manifest_path.exists() or archive_path.exists():
    raise FileExistsError('Delivery already exists; choose a new version.')
pre = json.loads((root/'pre_generation_freeze.json').read_text(encoding='utf-8-sig'))
source = root.parents[1] / 'dual_arm_task_experiments' / 'src' / 'atomic_task'
unchanged = {name:hashlib.sha256((source/name).read_bytes()).hexdigest()==digest
             for name,digest in pre['code_files'].items()}
assert all(unchanged.values()), 'Original evaluator changed since freeze'
files = [p for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
manifest = {'created_utc':datetime.now(timezone.utc).isoformat(),
            'original_evaluator_unchanged_since_freeze':unchanged,
            'files':[{'path':p.relative_to(root).as_posix(), 'bytes':p.stat().st_size,
                      'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with zipfile.ZipFile(archive_path,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    for p in files+[manifest_path]:
        archive.write(p,arcname=root.name+'/'+p.relative_to(root).as_posix())
with zipfile.ZipFile(archive_path) as archive:
    assert archive.testzip() is None
    for entry in manifest['files']:
        data = archive.read(root.name+'/'+entry['path'])
        assert hashlib.sha256(data).hexdigest()==entry['sha256']
print(json.dumps({'files':len(files)+1,'archive_bytes':archive_path.stat().st_size,
                  'archive_sha256':hashlib.sha256(archive_path.read_bytes()).hexdigest(),
                  'zip_crc_and_all_file_hashes_verified':True},indent=2))
