"""Check archived bytes; missing optional video bundle is reported separately."""
from pathlib import Path
import json,hashlib

if __name__=='__main__':
 root=Path(__file__).resolve().parent;manifest=json.loads((root/'MANIFEST_SHA256.json').read_text(encoding='utf-8'));missing_videos=[]
 for name,digest in manifest['files'].items():
  p=root/name
  if not p.exists() and p.suffix=='.mp4':missing_videos.append(name);continue
  assert p.is_file(),name
  assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,name
 print(json.dumps({'verified_files':len(manifest['files'])-len(missing_videos),'optional_videos_not_installed':len(missing_videos),'all_existing_files_match':True}))
