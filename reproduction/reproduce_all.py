"""Offline reproduction of the fixed v7_70 evaluations in a fresh directory."""
from pathlib import Path
import subprocess,sys,json
W=Path(__file__).resolve().parent
out=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else W/'results/new_run'
out.mkdir(parents=True,exist_ok=False)
for script,name in [('reproduce.py','fair'),('external_discrete.py','public'),('exhaustive_mechanism.py','mechanism')]:
 with (out/(name+'.log')).open('w',encoding='utf-8') as log:
  subprocess.run([sys.executable,'-X','utf8',str(W/script),str(out/name)],cwd=W,stdout=log,stderr=subprocess.STDOUT,check=True)
 print('COMPLETED',name,flush=True)
def read(p):return json.loads(p.read_text(encoding='utf-8'))
assert read(out/'public/summary.json')==read(W/'results/external_discrete_run01/summary.json')
assert read(out/'mechanism/summary.json')==read(W/'results/exhaustive_run01/summary.json')
for name in ['comparison_details.jsonl','external_CodeLlama-13b_details.jsonl','external_mistral-7b_details.jsonl']:
 a=[json.loads(x) for x in (out/'fair'/name).read_text(encoding='utf-8').splitlines()]
 b=[json.loads(x) for x in (W/'results/fair_comparison'/name).read_text(encoding='utf-8').splitlines()]
 assert a==b,name
print('All frozen evaluation results reproduced exactly; timing is not compared.')
