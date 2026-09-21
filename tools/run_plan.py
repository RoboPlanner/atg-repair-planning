"""Run the formal planning interface on JSON input; never overwrite an output."""
from pathlib import Path
import argparse, json, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'reproduction/implementation_v7_70'))
from atomic_task.pipeline import run_verified_atg

def states(data, key):
    values = data[key]
    if not isinstance(values, list) or any(not isinstance(v, str) or not v for v in values):
        raise ValueError(f'{key} must be an explicit array of nonempty strings')
    return set(values)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output and args.output.exists():
        parser.error('output already exists; choose a new path')
    try:
        data = json.loads(args.input.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            raise ValueError('input must be a JSON object')
        result = run_verified_atg(data['graph'], initial_states=states(data, 'initial_states'), goal_states=states(data, 'goal_states')).to_dict()
    except (KeyError, TypeError, ValueError) as exc:
        result = {'accepted': False, 'graph': None, 'audit': None, 'schedule': None, 'failure_reasons': [f'input validation failed: {exc}']}
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(text+'\n')
        print(('ACCEPTED' if result['accepted'] else 'REJECTED') + ': ' + str(args.output))
    else:
        print(text)
    return 0 if result['accepted'] else 2

if __name__ == '__main__':
    raise SystemExit(main())
