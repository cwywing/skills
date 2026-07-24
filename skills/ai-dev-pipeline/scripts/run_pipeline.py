"""Main orchestration loop for Cursor Agent CLI pipeline."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from agent_runner import auth_hint, ensure_agent_available, run_agent  # noqa: E402
from adapt_pending import run_adapt  # noqa: E402
from memory_store import after_task_memory, load_prior_learnings, memory_dir_from_config  # noqa: E402
from parse_plan import parse_plan, render_template  # noqa: E402
from task_store import TaskStore, load_yaml, utc_now  # noqa: E402

# Match in plain text OR JSON-escaped agent stdout (`\\nVERIFY_RESULT: FAIL`).
# Does NOT match template `VERIFY_RESULT: PASS|FAIL`.
VERIFY_FAIL_RE = re.compile(r"VERIFY_RESULT:\s*FAIL\b")
STAGE_NOTE_MAX_PER = 400
STAGE_NOTES_MAX_TOTAL = 1500


def load_config(path: Path) -> Dict[str, Any]:
    data = load_yaml(path)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid config: {path}")
    return data


def acceptance_list(task: Dict[str, Any]) -> str:
    lines = task.get("acceptance") or []
    return "\n".join(f"- {item}" for item in lines)


def stage_notes(task: Dict[str, Any], *, max_total: int = STAGE_NOTES_MAX_TOTAL) -> str:
    """Compact prior-stage notes for prompts (avoid Windows cmdline blow-up on retry)."""
    stages = task.get("stages") or {}
    parts: List[str] = []
    for sid, meta in stages.items():
        if not isinstance(meta, dict):
            continue
        note = str(meta.get("notes") or "").strip()
        status = meta.get("status")
        if not note:
            continue
        if len(note) > STAGE_NOTE_MAX_PER:
            note = note[: STAGE_NOTE_MAX_PER - 20] + "…(truncated)"
        parts.append(f"[{sid}] ({status}) {note}")
    text = "\n".join(parts) if parts else "(none)"
    if len(text) > max_total:
        text = text[: max_total - 20] + "\n…(truncated)"
    return text


def resolve_prompt_path(pipeline_root: Path, stage: Dict[str, Any]) -> Path:
    rel = stage.get("prompt") or f"prompts/{stage['id']}.md"
    path = Path(rel)
    if not path.is_absolute():
        path = pipeline_root / path
    return path


def build_stage_prompt(
    template_path: Path,
    task: Dict[str, Any],
    *,
    verify_command: List[str],
    other_pending_ids: Optional[List[str]] = None,
    prior_learnings: str = "(none)",
) -> str:
    template = template_path.read_text(encoding="utf-8")
    others = ", ".join(other_pending_ids) if other_pending_ids else "(none)"
    return render_template(
        template,
        {
            "task_id": str(task.get("id", "")),
            "task_description": str(task.get("description", "")),
            "acceptance_list": acceptance_list(task),
            "stage_notes": stage_notes(task),
            "verify_command": " ".join(verify_command) if verify_command else "(none)",
            "plan_path": str(task.get("source") or ""),
            "plan_content": "",
            "tasks_pending_dir": "",
            "other_pending_ids": others,
            "prior_learnings": prior_learnings or "(none)",
        },
    )


def run_shell_command(cmd: List[str], cwd: Path, log_path: Path) -> int:
    import os
    import shutil

    log_path.parent.mkdir(parents=True, exist_ok=True)
    resolved = list(cmd)
    if resolved:
        first = resolved[0]
        bin_path = shutil.which(first)
        if bin_path:
            resolved[0] = bin_path
        # Windows: .cmd/.bat need cmd.exe /c; also "cmd" itself and shell-builtins
        # (if/echo/...) are not executables — route through cmd.exe /c.
        # Note: when first=="cmd", resolved is already ["cmd.exe(full)", "/c", ...args]
        # after shutil.which above, so do NOT add another /c.
        if os.name == "nt":
            if first.lower() == "cmd":
                pass  # resolved[0] already resolved to cmd.exe, [1] is "/c"
            elif resolved[0].lower().endswith((".cmd", ".bat")):
                resolved = ["cmd.exe", "/c", *resolved]


    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(f"\n$ {' '.join(str(x) for x in resolved)}\n")
    completed = subprocess.run(
        resolved,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
    )
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(completed.stdout or "")
        fh.write(completed.stderr or "")
        fh.write(f"\nexit={completed.returncode}\n")
    return completed.returncode


def _cleanup_windows_junk(cwd: Path) -> None:
    """Remove reserved-name junk files (e.g. NUL) that break git add on Windows."""
    import os

    if os.name != "nt":
        return
    for name in ("NUL", "NUL.map", "CON", "PRN", "AUX"):
        target = cwd / name
        try:
            # Prefer extended path for reserved device names
            os.remove(f"\\\\?\\{target}")
        except OSError:
            try:
                if target.exists():
                    target.unlink()
            except OSError:
                pass


def ensure_branch(cwd: Path, branch: str) -> None:
    subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=cwd, check=True, capture_output=True)
    cur = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if cur == branch:
        return
    exists = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
        cwd=cwd,
    )
    if exists.returncode == 0:
        subprocess.run(["git", "checkout", branch], cwd=cwd, check=True)
    else:
        subprocess.run(["git", "checkout", "-b", branch], cwd=cwd, check=True)


def deliver(
    *,
    mode: str,
    cwd: Path,
    task_id: str,
    summary: str,
    branch_prefix: str,
    commit_message_tpl: str,
    logs_dir: Path,
) -> Dict[str, Any]:
    if mode == "none":
        return {"mode": "none", "ok": True}

    branch = f"{branch_prefix}{task_id}".replace(" ", "-")
    msg = commit_message_tpl.format(task_id=task_id, summary=summary, stage="done")
    log = logs_dir / "delivery" / f"{task_id}.log"
    try:
        _cleanup_windows_junk(cwd)
        ensure_branch(cwd, branch)
        add = subprocess.run(
            ["git", "add", "-A"],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        if add.returncode != 0:
            # Retry once after junk cleanup (Windows NUL etc.)
            _cleanup_windows_junk(cwd)
            subprocess.run(["git", "add", "-A"], cwd=cwd, check=True)
        # Commit only if there are staged changes
        staged = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=cwd,
        )
        if staged.returncode != 0:
            subprocess.run(["git", "commit", "-m", msg], cwd=cwd, check=True)
        else:
            with log.open("a", encoding="utf-8") as fh:
                fh.write("No staged changes to commit.\n")

        if mode == "pr":
            body = f"Pipeline task `{task_id}`\n\n{summary}\n"
            pr = subprocess.run(
                [
                    "gh",
                    "pr",
                    "create",
                    "--title",
                    msg,
                    "--body",
                    body,
                ],
                cwd=cwd,
                capture_output=True,
                text=True,
            )
            log.parent.mkdir(parents=True, exist_ok=True)
            with log.open("a", encoding="utf-8") as fh:
                fh.write(pr.stdout)
                fh.write(pr.stderr)
            return {
                "mode": "pr",
                "ok": pr.returncode == 0,
                "branch": branch,
                "output": (pr.stdout or pr.stderr).strip(),
            }

        return {"mode": "commit", "ok": True, "branch": branch, "message": msg}
    except Exception as exc:  # noqa: BLE001 — surface delivery errors to caller
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8") as fh:
            fh.write(f"delivery error: {exc}\n")
        return {"mode": mode, "ok": False, "error": str(exc)}


def enabled_stages(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    stages = config.get("stages") or []
    return [s for s in stages if isinstance(s, dict) and s.get("enabled", True)]


def should_run_plan_stage(config: Dict[str, Any], store: TaskStore) -> bool:
    stages = {s["id"]: s for s in enabled_stages(config)}
    plan = stages.get("plan")
    if not plan:
        return False
    return len(store.list_pending()) == 0 and len(list(store.active.glob("*.*"))) == 0


def apply_stage_status(
    store: TaskStore,
    task: Dict[str, Any],
    stage_id: str,
    status: str,
    *,
    notes: str = "",
    attempts: Optional[int] = None,
) -> Dict[str, Any]:
    task = store.set_stage_status(task, stage_id, status, notes=notes, inc_attempt=False)
    if attempts is not None:
        task["stages"][stage_id]["attempts"] = attempts
    return task


def execute_stage(
    *,
    store: TaskStore,
    stage: Dict[str, Any],
    task: Dict[str, Any],
    config: Dict[str, Any],
    pipeline_root: Path,
    cwd: Path,
    logs_dir: Path,
) -> Dict[str, Any]:
    stage_id = stage["id"]
    if stage_id == "plan":
        # Plan at task level is usually already done when task exists
        task = apply_stage_status(store, task, stage_id, "skipped", notes="task already materialized")
        return {"ok": True, "task": task}

    agent_cfg = config.get("agent") or {}
    max_retry = int((config.get("retry") or {}).get("max_per_stage") or 2)
    verify_command = list(task.get("verify_command") or stage.get("run") or [])
    prompt_path = resolve_prompt_path(pipeline_root, stage)
    if not prompt_path.exists():
        return {"ok": False, "task": task, "error": f"Missing prompt: {prompt_path}"}

    attempts = int((task.get("stages") or {}).get(stage_id, {}).get("attempts") or 0)
    last_error = ""

    while attempts < max_retry:
        attempts += 1
        log_path = logs_dir / str(task["id"]) / f"{stage_id}-attempt{attempts}.md"
        other_ids = [
            p.stem for p in store.list_pending() if p.stem != str(task["id"])
        ]
        mem_cfg = config.get("memory") or {}
        prior = "(none)"
        if mem_cfg.get("enabled", True) is not False:
            prior = load_prior_learnings(
                memory_dir_from_config(config, cwd),
                task,
                recent_n=int(mem_cfg.get("recent_n") or 5),
                max_chars=int(mem_cfg.get("max_inject_chars") or 1200),
            )
        prompt = build_stage_prompt(
            prompt_path,
            task,
            verify_command=verify_command,
            other_pending_ids=other_ids,
            prior_learnings=prior,
        )
        result = run_agent(
            prompt,
            cwd=cwd,
            bin_name=agent_cfg.get("bin") or "agent",
            extra_args=list(
                agent_cfg.get("args") or ["-p", "--force", "--output-format", "json"]
            ),
            timeout_sec=agent_cfg.get("timeout_sec") or 1800,
            log_path=log_path,
        )

        # Clean Windows reserved-name junk that agent may have written (NUL, CON, ...)
        _cleanup_windows_junk(cwd)

        cmd_ok = True
        if verify_command and stage_id in {"verify", "deploy"}:
            cmd_rc = run_shell_command(
                verify_command,
                cwd,
                logs_dir / str(task["id"]) / f"{stage_id}-cmd.log",
            )
            cmd_ok = cmd_rc == 0

        verify_fail = stage_id == "verify" and bool(
            VERIFY_FAIL_RE.search(result.stdout or "")
        )
        # Harness: Windows cmdline / empty verify with nonzero rc
        cmdline_boom = "command line is too long" in (
            (result.stderr or "") + (result.stdout or "")
        ).lower()
        ok = result.ok and cmd_ok and not verify_fail and not cmdline_boom
        note = (result.stdout or result.stderr or "")[-2000:]
        if cmdline_boom:
            note = (
                "[harness] Windows command line too long — prompt should spill to file. "
                + note
            )[-2000:]
        task = apply_stage_status(
            store,
            task,
            stage_id,
            "done" if ok else "failed",
            notes=note,
            attempts=attempts,
        )
        if ok:
            return {"ok": True, "task": task, "attempts": attempts}
        last_error = result.stderr or result.stdout or "stage failed"

    return {"ok": False, "task": task, "error": last_error, "attempts": attempts}


def process_task(
    *,
    store: TaskStore,
    task_path: Path,
    config: Dict[str, Any],
    pipeline_root: Path,
    project_root: Path,
) -> Dict[str, Any]:
    task = store.load_task(task_path)
    store.validate_task(task)
    stage_ids = [s["id"] for s in enabled_stages(config)]
    task = store.ensure_stage_map(task, stage_ids)
    store.write_task(task, bucket="active")

    logs_dir = Path(config.get("logs_dir") or ".pipeline/logs")
    if not logs_dir.is_absolute():
        logs_dir = project_root / logs_dir

    for stage in enabled_stages(config):
        sid = stage["id"]
        status = (task.get("stages") or {}).get(sid, {}).get("status")
        if status in {"done", "skipped"}:
            continue
        result = execute_stage(
            store=store,
            stage=stage,
            task=task,
            config=config,
            pipeline_root=pipeline_root,
            cwd=project_root,
            logs_dir=logs_dir,
        )
        task = result["task"]
        store.write_task(task, bucket="active")
        if not result.get("ok"):
            store.write_task(task, bucket="failed")
            _post_task_learn(
                config=config,
                project_root=project_root,
                pipeline_root=pipeline_root,
                store=store,
                task=task,
                impl_ok=False,
                delivery_ok=False,
                failed_stage=sid,
            )
            return {
                "ok": False,
                "task_id": task["id"],
                "failed_stage": sid,
                "error": result.get("error"),
            }

    # impl_ok = all stages passed; delivery may still fail separately
    impl_ok = True
    delivery_cfg = config.get("delivery") or {}
    delivery = deliver(
        mode=str(delivery_cfg.get("mode") or "commit"),
        cwd=project_root,
        task_id=str(task["id"]),
        summary=str(task.get("description") or "")[:120],
        branch_prefix=str(delivery_cfg.get("branch_prefix") or "pipeline/"),
        commit_message_tpl=str(
            delivery_cfg.get("commit_message") or "pipeline({task_id}): {summary}"
        ),
        logs_dir=logs_dir,
    )
    task["delivery"] = delivery
    task["completed_at"] = utc_now()
    delivery_ok = bool(delivery.get("ok", True))
    # impl passed → done bucket even if delivery failed; report delivery failure separately
    store.write_task(task, bucket="done" if impl_ok else "failed")
    learn = _post_task_learn(
        config=config,
        project_root=project_root,
        pipeline_root=pipeline_root,
        store=store,
        task=task,
        impl_ok=impl_ok,
        delivery_ok=delivery_ok,
        failed_stage="",
    )
    return {
        "ok": impl_ok,
        "impl_ok": impl_ok,
        "delivery_ok": delivery_ok,
        "task_id": task["id"],
        "delivery": delivery,
        "memory": {"one_liner": (learn or {}).get("one_liner"), "gaps": (learn or {}).get("gaps")},
        "adapt": learn.get("adapt") if isinstance(learn, dict) else None,
    }


def _post_task_learn(
    *,
    config: Dict[str, Any],
    project_root: Path,
    pipeline_root: Path,
    store: TaskStore,
    task: Dict[str, Any],
    impl_ok: bool,
    delivery_ok: bool,
    failed_stage: str,
) -> Dict[str, Any]:
    memory = after_task_memory(
        config=config,
        project_root=project_root,
        pipeline_root=pipeline_root,
        task=task,
        impl_ok=impl_ok,
        delivery_ok=delivery_ok,
        failed_stage=failed_stage,
        run_agent_fn=run_agent,
    )
    adapt_result = {"mode": "off"}
    if memory.get("enabled") is not False:
        try:
            adapt_result = run_adapt(
                config=config,
                project_root=project_root,
                store=store,
                memory=memory,
            )
            print(
                f"memory: {memory.get('one_liner')} | adapt: mode={adapt_result.get('mode')} "
                f"proposals={len(adapt_result.get('proposals') or [])} "
                f"applied={adapt_result.get('applied_ids') or []}"
            )
        except Exception as exc:
            adapt_result = {"mode": "error", "error": str(exc)}
            print(f"adapt error: {exc}", file=sys.stderr)
    memory["adapt"] = adapt_result
    return memory


def run_pipeline(
    *,
    project_root: Path,
    config_path: Path,
    plan: Optional[Path] = None,
    once: bool = False,
    dry_run: bool = False,
) -> int:
    project_root = project_root.resolve()
    config = load_config(config_path)
    pipeline_root = (project_root / ".pipeline").resolve()

    tasks_dir = Path(config.get("tasks_dir") or ".pipeline/tasks")
    if not tasks_dir.is_absolute():
        tasks_dir = project_root / tasks_dir
    store = TaskStore(tasks_dir)
    store.ensure_dirs()
    store.clear_active_to_pending()

    agent_cfg = config.get("agent") or {}
    if not dry_run:
        try:
            ensure_agent_available(agent_cfg.get("bin") or "agent")
        except RuntimeError as err:
            print(err, file=sys.stderr)
            print(auth_hint(), file=sys.stderr)
            return 1

    # Import / plan
    if plan:
        plan = plan.resolve()
        prompt = pipeline_root / "prompts" / "plan.md"
        logs_dir = Path(config.get("logs_dir") or ".pipeline/logs")
        if not logs_dir.is_absolute():
            logs_dir = project_root / logs_dir
        info = parse_plan(
            plan,
            store=store,
            prompt_template=prompt if prompt.exists() else None,
            cwd=project_root,
            agent_bin=agent_cfg.get("bin") or "agent",
            agent_args=list(
                agent_cfg.get("args") or ["-p", "--force", "--output-format", "json"]
            ),
            timeout_sec=int(agent_cfg.get("timeout_sec") or 1800),
            log_path=logs_dir / "plan" / f"{plan.stem}.md",
            use_agent=not dry_run,
        )
        print(yaml.safe_dump({"plan": info}, allow_unicode=True, sort_keys=False))
    elif should_run_plan_stage(config, store):
        plans_dir = Path(config.get("plans_dir") or ".pipeline/plans")
        if not plans_dir.is_absolute():
            plans_dir = project_root / plans_dir
        plans = sorted(plans_dir.glob("*.md")) + sorted(plans_dir.glob("*.yaml"))
        plans += sorted(plans_dir.glob("*.yml"))
        if not plans:
            print("No pending tasks and no plans found.", file=sys.stderr)
            return 2
        return run_pipeline(
            project_root=project_root,
            config_path=config_path,
            plan=plans[0],
            once=once,
            dry_run=dry_run,
        )

    if dry_run:
        pending = [p.name for p in store.list_pending()]
        print(json.dumps({"dry_run": True, "pending": pending}, ensure_ascii=False, indent=2))
        return 0

    stop_on_fail = bool(config.get("stop_on_task_failure"))
    processed = 0
    failures = 0

    while True:
        pending = store.list_pending()
        if not pending:
            break
        task_path = pending[0]
        print(f"==> processing {task_path.name} @ {datetime.now(timezone.utc).isoformat()}")
        result = process_task(
            store=store,
            task_path=task_path,
            config=config,
            pipeline_root=pipeline_root,
            project_root=project_root,
        )
        processed += 1
        print(yaml.safe_dump({"result": result}, allow_unicode=True, sort_keys=False))
        if not result.get("ok"):
            failures += 1
            if stop_on_fail:
                break
        if once:
            break

    print(f"Done. processed={processed} failures={failures}")
    return 1 if failures else 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run AI dev pipeline via Cursor Agent CLI")
    parser.add_argument("--project", default=".", help="Target project root")
    parser.add_argument(
        "--config",
        default=".pipeline/config.yaml",
        help="Pipeline config path (relative to project unless absolute)",
    )
    parser.add_argument("--plan", help="Markdown/YAML/JSON plan to ingest first")
    parser.add_argument("--once", action="store_true", help="Process only one task")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse/import only; do not call agent or deliver",
    )
    parser.add_argument(
        "--no-import",
        action="store_true",
        help="Do not re-import plan; resume existing pending tasks (keeps stage state)",
    )
    args = parser.parse_args(argv)

    project = Path(args.project).resolve()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = project / config_path
    if not config_path.exists():
        print(f"Missing config: {config_path}. Run install.py first.", file=sys.stderr)
        return 2

    plan = Path(args.plan) if args.plan else None
    if plan and not plan.is_absolute():
        plan = (Path.cwd() / plan).resolve()
    if args.no_import and plan:
        print("--no-import ignores --plan; resume mode keeps existing tasks.", file=sys.stderr)
        plan = None

    return run_pipeline(
        project_root=project,
        config_path=config_path,
        plan=plan,
        once=args.once,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    raise SystemExit(main())
