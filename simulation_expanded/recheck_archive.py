"""Read-only re-evaluation of saved trajectories; does not replace frozen reports."""
from pathlib import Path
import json
from verify_expanded import verify_trial

if __name__=='__main__':
 root=Path(__file__).resolve().parent/'evaluation_frozen_v1'
 archived=json.loads((root/'independent_verification.json').read_text(encoding='utf-8'))
 records=[verify_trial(root/r['trial']) for r in archived['records']]
 for expected,actual in zip(archived['records'],records):
  for k in ['execution_success','integrity_valid','outcome_agreement','physical_failure_reasons','integrity_issues']:
   assert expected[k]==actual[k],(actual['trial'],k)
 print(json.dumps({'rechecked':len(records),'successes':sum(r['execution_success'] for r in records),'all_match_archive':True}))
