"""Generic loop runner: import a plan once, then loop all pending tasks.

Usage:
  # First run: import plan + loop
  python .pipeline/run_loop.py --plan .pipeline/plans/<tasks>.yaml

  # Resume (do NOT re-import; keeps stage state, saves agent quota)
  python .pipeline/run_loop.py --no-import
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".pipeline" / "scripts"))

from parse_plan import parse_plan  # noqa: E402
from task_store import TaskStore  # noqa: E402
from run_pipeline import run_pipeline  # noqa: E402

CONFIG = ROOT / ".pipeline" / "config.yaml"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Loop all pending pipeline tasks")
    parser.add_argument("--plan", help="Plan YAML/JSON/MD to import (first run)")
    parser.add_argument(
        "--no-import",
        action="store_true",
        help="Resume mode: do not re-import plan; keep existing task stage state",
    )
    args = parser.parse_args(argv)

    store = TaskStore(ROOT / ".pipeline" / "tasks")
    store.ensure_dirs()

    if args.no_import:
        print("resume mode: skipping import")
    elif args.plan:
        plan = Path(args.plan)
        if not plan.is_absolute():
            plan = (ROOT / plan).resolve()
        done_ids = {p.stem for p in store.done.glob("*.yaml")}
        info = parse_plan(plan, store=store, use_agent=False)
        for path in list(store.list_pending()):
            if path.stem in done_ids:
                store.move(path.stem, "done")
        print("import:", info)
    else:
        print("No --plan and no --no-import; assuming resume (no import)")

    print("pending:", [p.name for p in store.list_pending()])
    return run_pipeline(
        project_root=ROOT,
        config_path=CONFIG,
        plan=None,
        once=False,
        dry_run=False,
    )


if __name__ == "__main__":
    raise SystemExit(main())
