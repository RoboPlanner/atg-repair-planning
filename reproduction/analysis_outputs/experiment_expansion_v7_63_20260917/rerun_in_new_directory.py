"""Repeat experiments into a new sibling directory, never replace archived outputs."""
from pathlib import Path
import argparse,shutil,subprocess,sys

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name',required=True,help='New sibling directory name, e.g. reproduction_run01')
    args=parser.parse_args()
    if not args.name or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in args.name):
        parser.error('Use letters, digits, underscores and hyphens only')
    source=Path(__file__).resolve().parent;target=source.parent/args.name
    if target.exists():parser.error('Target already exists; choose a new name')
    target.mkdir()
    for name in ['inputs','implementation_v7_63']:
        shutil.copytree(source/name,target/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    for name in ['run_supplement.py','milp_baseline.py','test_new_contract_and_milp.py','experiment_protocol_frozen.json','verify_historical_core.py']:
        shutil.copy2(source/name,target/name)
    result=subprocess.run([sys.executable,'-X','utf8',str(target/'run_supplement.py')],cwd=target)
    print('New run directory:',target)
    raise SystemExit(result.returncode)
if __name__=='__main__':main()
