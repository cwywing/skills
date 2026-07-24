"""Parse Markdown plans and/or import structured task files."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# Allow running as script from any cwd
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from agent_runner import run_agent  # noqa: E402
from task_store import TaskStore, load_yaml  # noqa: E402


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def render_template(template: str, mapping: Dict[str, str]) -> str:
    out = template
    for key, value in mapping.items():
        out = out.replace("{{" + key + "}}", value)
    return out


def is_structured_plan(path: Path) -> bool:
    return path.suffix.lower() in {".yaml", ".yml", ".json"}


def import_structured(path: Path, store: TaskStore) -> List[Path]:
    data = load_yaml(path)
    return store.import_tasks_document(data, source=str(path))


def _extract_section(content: str, headers: List[str]) -> Optional[str]:
    lines = content.splitlines()
    start = None
    for i, line in enumerate(lines):
        if re.match(r"^#{1,3}\s+", line):
            title = re.sub(r"^#{1,3}\s+", "", line).strip().lower()
            if any(h.lower() == title or h.lower() in title for h in headers):
                start = i + 1
                break
    if start is None:
        return None
    collected: List[str] = []
    for line in lines[start:]:
        if re.match(r"^#{1,3}\s+", line):
            break
        collected.append(line)
    return "\n".join(collected)


def _list_items(block: str) -> List[str]:
    items: List[str] = []
    for line in block.splitlines():
        m = re.match(r"^\s*(?:[-*]|\d+\.)\s+(?:\[[ xX]\]\s+)?(.+)$", line)
        if m:
            text = m.group(1).strip()
            if len(text) >= 8:
                items.append(text)
    return items


def heuristic_tasks_from_markdown(plan_path: Path, content: str) -> List[Dict[str, Any]]:
    """Fallback splitter when agent is unavailable.

    Prefers list items under Suggested tasks / Tasks / 任务 sections.
    Otherwise falls back to a single task from the plan title/goal.
    """
    section = _extract_section(
        content,
        ["Suggested tasks", "Tasks", "Task list", "任务", "任务列表", "拆分任务"],
    )
    items = _list_items(section) if section else []

    if not items:
        title = plan_path.stem
        goal = None
        for line in content.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
            if re.match(r"^#{1,3}\s+Goal\b", line, re.I) or re.match(
                r"^#{1,3}\s+目标\b", line
            ):
                goal = ""
                continue
            if goal is not None:
                if re.match(r"^#{1,3}\s+", line):
                    break
                if line.strip():
                    goal = (goal + " " + line.strip()).strip()
        desc = goal or f"Implement plan: {title}"
        items = [desc]

    tasks: List[Dict[str, Any]] = []
    for idx, desc in enumerate(items, start=1):
        tid = f"PLAN_{idx:03d}"
        tasks.append(
            {
                "id": tid,
                "description": desc,
                "acceptance": [
                    f"Work for '{desc}' is implemented",
                    "Relevant verification for this item passes or is documented",
                ],
                "category": "feature",
                "complexity": "medium",
                "source": str(plan_path),
                "stages": {
                    "plan": {"status": "done"},
                    "dev": {"status": "pending"},
                    "verify": {"status": "pending"},
                },
            }
        )
    return tasks


def plan_with_agent(
    *,
    plan_path: Path,
    store: TaskStore,
    prompt_template: Path,
    cwd: Path,
    agent_bin: str,
    agent_args: List[str],
    timeout_sec: int,
    log_path: Path,
) -> Tuple[List[Path], str]:
    template = read_text(prompt_template)
    prompt = render_template(
        template,
        {
            "plan_path": str(plan_path),
            "plan_content": read_text(plan_path),
            "tasks_pending_dir": str(store.pending),
        },
    )
    result = run_agent(
        prompt,
        cwd=cwd,
        bin_name=agent_bin,
        extra_args=agent_args,
        timeout_sec=timeout_sec,
        log_path=log_path,
    )
    written = store.list_pending()
    if written:
        return written, "agent"
    # Agent may have written files with unexpected names; try heuristic fallback
    tasks = heuristic_tasks_from_markdown(plan_path, read_text(plan_path))
    paths = [store.write_task(t) for t in tasks]
    mode = "agent+heuristic-fallback" if result.ok else "heuristic-fallback"
    return paths, mode


def parse_plan(
    plan_path: Path,
    *,
    store: TaskStore,
    prompt_template: Optional[Path] = None,
    cwd: Optional[Path] = None,
    agent_bin: str = "agent",
    agent_args: Optional[List[str]] = None,
    timeout_sec: int = 1800,
    log_path: Optional[Path] = None,
    use_agent: bool = True,
) -> Dict[str, Any]:
    plan_path = plan_path.resolve()
    store.ensure_dirs()

    if is_structured_plan(plan_path):
        paths = import_structured(plan_path, store)
        return {"mode": "structured-import", "tasks": [p.name for p in paths]}

    if use_agent and prompt_template and cwd is not None:
        try:
            paths, mode = plan_with_agent(
                plan_path=plan_path,
                store=store,
                prompt_template=prompt_template,
                cwd=cwd,
                agent_bin=agent_bin,
                agent_args=list(agent_args or ["-p", "--force", "--output-format", "json"]),
                timeout_sec=timeout_sec,
                log_path=log_path or (store.root.parent / "logs" / "plan.md"),
            )
            return {"mode": mode, "tasks": [p.name for p in paths]}
        except RuntimeError:
            pass

    tasks = heuristic_tasks_from_markdown(plan_path, read_text(plan_path))
    paths = [store.write_task(t) for t in tasks]
    return {"mode": "heuristic", "tasks": [p.name for p in paths]}


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Parse plan into .pipeline tasks")
    parser.add_argument("--plan", required=True, help="Path to MD/YAML/JSON plan")
    parser.add_argument("--tasks-dir", default=".pipeline/tasks")
    parser.add_argument("--prompt", default=".pipeline/prompts/plan.md")
    parser.add_argument("--cwd", default=".")
    parser.add_argument("--no-agent", action="store_true")
    args = parser.parse_args(argv)

    store = TaskStore(args.tasks_dir)
    result = parse_plan(
        Path(args.plan),
        store=store,
        prompt_template=Path(args.prompt),
        cwd=Path(args.cwd),
        use_agent=not args.no_agent,
    )
    print(yaml.safe_dump(result, allow_unicode=True, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
