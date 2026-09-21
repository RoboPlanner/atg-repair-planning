from __future__ import annotations

import argparse
from pathlib import Path

from .experiments import run_experiments
from .generation import generate_dataset, read_jsonl, validate_task, write_jsonl


def _generate(args: argparse.Namespace) -> None:
    records = generate_dataset(args.count, args.seed, args.duration_jitter)
    write_jsonl(records, Path(args.out))
    print(f"wrote {len(records)} task records to {args.out}")


def _validate(args: argparse.Namespace) -> None:
    try:
        records = read_jsonl(Path(args.input))
    except (KeyError, TypeError, ValueError) as exc:
        print(f"input parsing failed: {exc}")
        raise SystemExit(1) from None
    failures = []
    for record in records:
        errors = validate_task(record)
        if errors:
            failures.append((record.task_id, errors))
    if failures:
        for task_id, errors in failures:
            print(f"{task_id}: {errors}")
        raise SystemExit(1)
    print(f"validated {len(records)} task records")


def _run(args: argparse.Namespace) -> None:
    records = generate_dataset(args.count, args.seed, args.duration_jitter)
    paths = run_experiments(
        records,
        Path(args.out),
        structure_seed=args.structure_seed,
        generation_seed=args.seed,
        duration_jitter=args.duration_jitter,
    )
    print(f"wrote {len(records)} task records and planning experiment outputs")
    for name, path in paths.items():
        print(f"{name}: {path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Offline atomic task planning experiments")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="generate task records only")
    gen.add_argument("--count", type=int, default=24)
    gen.add_argument("--seed", type=int, default=7)
    gen.add_argument("--duration-jitter", type=float, default=0.2)
    gen.add_argument("--out", default="planning_outputs/tasks.jsonl")
    gen.set_defaults(func=_generate)

    val = sub.add_parser("validate", help="validate generated JSONL records")
    val.add_argument("--input", required=True)
    val.set_defaults(func=_validate)

    run = sub.add_parser("run", help="generate data and run all paper-style experiments")
    run.add_argument("--count", type=int, default=24)
    run.add_argument("--seed", type=int, default=7)
    run.add_argument("--duration-jitter", type=float, default=0.2)
    run.add_argument(
        "--structure-seed",
        type=int,
        default=0,
        help="master offset for deterministic candidate-edge perturbations",
    )
    run.add_argument("--out", default="planning_outputs")
    run.set_defaults(func=_run)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
