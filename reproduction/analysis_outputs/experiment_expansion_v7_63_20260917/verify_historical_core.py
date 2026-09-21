from pathlib import Path
from unittest.mock import patch
import csv,json,math,sys
WORK=Path(__file__).resolve().parent;ROOT=WORK.parents[1]
sys.path.insert(0,str(WORK/'implementation_v7_63'))
from atomic_task.experiments import run_experiments
from atomic_task.generation import read_jsonl
HIST=ROOT/'dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907'
out=WORK/'historical_replay';out.mkdir(exist_ok=False)
records=read_jsonl(HIST/'tasks.jsonl')
cfg=json.loads((HIST/'analysis/experiment_configuration.json').read_text(encoding='utf-8'))
with patch('atomic_task.experiments.run_extended_experiments',side_effect=lambda records,output,method,methods,paths,**kwargs:paths):
    paths=run_experiments(records,out/'core',structure_seed=cfg['structure_seed'],generation_seed=cfg['generation_seed'],duration_jitter=cfg['duration_jitter'])
report={}
for key in ['table1','table2','table3','table4','table1_detailed','table2_detailed','table3_detailed','table4_detailed']:
    old=list(csv.DictReader((HIST/'tables'/paths[key].name).open(encoding='utf-8-sig')))
    new=list(csv.DictReader(paths[key].open(encoding='utf-8-sig')))
    diffs=[]
    assert len(old)==len(new)
    for index,(a,b) in enumerate(zip(old,new)):
        for col,value in a.items():
            equal=value==b.get(col)
            if not equal:
                try:equal=math.isclose(float(value),float(b[col]),rel_tol=1e-12,abs_tol=1e-12)
                except (ValueError,KeyError):pass
            if not equal:diffs.append({'row':index,'column':col,'old':value,'new':b.get(col)})
    report[key]={'rows':len(old),'differences':diffs}
(out/'comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
assert not any(r['differences'] for r in report.values()),report
print(json.dumps({'records':len(records),'compared_tables':len(report),'historical_metric_differences':0},ensure_ascii=False))
