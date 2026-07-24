"""Pipeline round memory: summarize after each task and inject into later prompts."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import yaml

# Only match real failure signals — NEVER template labels like `authz: n/a`
# or checklist headings that appear on every Verify PASS.
GAP_PATTERNS = [
    (
        re.compile(
            r"(?i)(?:authz\s*:\s*(?:fail|missing|gap)|criterion:.*(?:403|特权|AuthZ).*(?:fail|缺)"
            r"|非特权.*(?:未|fail|缺)|特权写.*(?:未|fail|缺)|missing.*(?:403|authz))"
        ),
        "authz",
    ),
    (
        re.compile(
            r"(?i)(?:defaults?\s*:\s*(?:fail|missing)|mock.*(?:default|开).*(?:fail|危险|缺)"
            r"|危险默认|MOCK_.*(?:true|1).*prod)"
        ),
        "mock_default",
    ),
    (
        re.compile(
            r"(?i)(?:skip.?sign.*(?:fail|开|on|true)|回调.*(?:未验签|skip).*(?:fail|缺)"
            r"|signature.*(?:skip|bypassed).*(?:fail|prod))"
        ),
        "skip_sign",
    ),
    (
        re.compile(
            r"(?i)(?:missing.*(?:read|list|show)|读闭环.*(?:fail|缺|gap)|无\s*(?:list|show)\s*(?:路由|端点)"
            r"|criterion:.*(?:list|show).*(?:fail|缺))"
        ),
        "missing_read",
    ),
    (
        re.compile(
            r"(?i)(?:pii.*(?:leak|泄漏|fail)|未鉴权.*写|anonymous.*write.*(?:fail|开)"
            r"|写操作.*未认证)"
        ),
        "authn_write",
    ),
]
# Plain or JSON-escaped stdout; does not match template `PASS|FAIL`.
VERIFY_FAIL_RE = re.compile(r"VERIFY_RESULT:\s*FAIL\b", re.I)
NA_LINE_RE = re.compile(r"(?i)^\s*(?:authz|defaults?|mechanism|prd_coverage)\s*:\s*n/a\b")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def memory_dir_from_config(config: Dict[str, Any], project_root: Path) -> Path:
    mem = config.get("memory") or {}
    rel = mem.get("dir") or ".pipeline/memory"
    path = Path(rel)
    if not path.is_absolute():
        path = project_root / path
    return path


def ensure_memory_dirs(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)


def _stage_notes(task: Dict[str, Any], stage_id: str) -> str:
    meta = (task.get("stages") or {}).get(stage_id) or {}
    return str(meta.get("notes") or "")


def _scrub_na_lines(text: str) -> str:
    """Drop verify template lines like `authz: n/a` that false-trigger gaps."""
    return "\n".join(
        line for line in (text or "").splitlines() if not NA_LINE_RE.match(line)
    )


def extract_gaps_from_text(text: str) -> List[Dict[str, str]]:
    gaps: List[Dict[str, str]] = []
    seen = set()
    scrubbed = _scrub_na_lines(text)
    if VERIFY_FAIL_RE.search(scrubbed):
        gaps.append({"gap_id": "verify_fail", "note": "VERIFY_RESULT: FAIL"})
        seen.add("verify_fail")
    for pat, tag in GAP_PATTERNS:
        if pat.search(scrubbed) and tag not in seen:
            seen.add(tag)
            gaps.append({"gap_id": tag, "note": f"detected:{tag}"})
    return gaps


def rule_summarize(
    task: Dict[str, Any],
    *,
    impl_ok: bool,
    delivery_ok: bool,
    failed_stage: str = "",
) -> Dict[str, Any]:
    tid = str(task.get("id", ""))
    verify_notes = _stage_notes(task, "verify")
    # Only mine gaps from verify/dev notes when the task actually failed.
    # PASS notes still contain checklist words (authz/mock) that polluted adapt.
    gaps: List[Dict[str, str]] = []
    if not impl_ok:
        blob = f"{verify_notes}\n{_stage_notes(task, 'dev')}"
        gaps = extract_gaps_from_text(blob)
        if failed_stage and not any(
            g["gap_id"] == f"failed_{failed_stage}" for g in gaps
        ):
            gaps.append(
                {"gap_id": f"failed_{failed_stage}", "note": f"stage {failed_stage} failed"}
            )

    advice: List[Dict[str, str]] = []
    for g in gaps:
        gid = g["gap_id"]
        if gid == "authz":
            advice.append(
                {
                    "target_hint": "admin settle withdraw payout",
                    "suggest_acceptance": "非特权用户调用特权写接口 → 403（机制：Feature 测试）",
                }
            )
        elif gid in {"mock_default", "skip_sign"}:
            advice.append(
                {
                    "target_hint": "auth sf payment mock callback",
                    "suggest_acceptance": "Mock/skip-sign 默认关闭；仅显式 env 且非 production 可开",
                }
            )
        elif gid == "missing_read":
            advice.append(
                {
                    "target_hint": "orders withdraws list show",
                    "suggest_acceptance": "同资源含 list/show 读闭环验收",
                }
            )
        elif gid == "authn_write":
            advice.append(
                {
                    "target_hint": "boost cancel withdraw orders",
                    "suggest_acceptance": "写操作需认证；响应不泄漏他人 PII",
                }
            )

    one_liner = (
        f"{tid}: {'OK' if impl_ok else 'FAIL'}"
        + (f" @{failed_stage}" if failed_stage else "")
        + (f" gaps={[g['gap_id'] for g in gaps]}" if gaps else "")
    )
    return {
        "task_id": tid,
        "finished_at": utc_now(),
        "impl_ok": impl_ok,
        "delivery_ok": delivery_ok,
        "failed_stage": failed_stage or "",
        "done_summary": str(task.get("description") or "")[:200],
        "verify_excerpt": verify_notes[-800:] if verify_notes else "(none)",
        "gaps": gaps,
        "advice": advice,
        "one_liner": one_liner,
    }


def render_memory_md(data: Dict[str, Any]) -> str:
    gaps_lines = "\n".join(
        f"- gap_id: {g.get('gap_id')}\n  note: {g.get('note')}" for g in (data.get("gaps") or [])
    ) or "- (none)"
    advice_lines = "\n".join(
        f"- target_hint: {a.get('target_hint')}\n  suggest_acceptance: {a.get('suggest_acceptance')}"
        for a in (data.get("advice") or [])
    ) or "- (none)"
    return (
        f"# Memory: {data.get('task_id')}\n"
        f"- finished_at: {data.get('finished_at')}\n"
        f"- impl_ok: {data.get('impl_ok')} / delivery_ok: {data.get('delivery_ok')}\n"
        f"- failed_stage: {data.get('failed_stage') or '(none)'}\n\n"
        f"## Done\n- {data.get('done_summary')}\n\n"
        f"## Verify\n```\n{data.get('verify_excerpt')}\n```\n\n"
        f"## Gaps\n{gaps_lines}\n\n"
        f"## Advice for later tasks\n{advice_lines}\n"
    )


def write_task_memory(root: Path, data: Dict[str, Any]) -> Path:
    ensure_memory_dirs(root)
    path = root / f"{data['task_id']}.md"
    path.write_text(render_memory_md(data), encoding="utf-8")
    # sidecar yaml for adapt matching
    ypath = root / f"{data['task_id']}.yaml"
    with ypath.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, allow_unicode=True, sort_keys=False)
    return path


def update_index(root: Path, data: Dict[str, Any], *, recent_n: int = 10) -> None:
    ensure_memory_dirs(root)
    index = root / "index.md"
    lines: List[str] = []
    if index.exists():
        lines = index.read_text(encoding="utf-8", errors="replace").splitlines()

    # Keep header
    header = ["# Pipeline memory index", "", "## Recent", ""]
    recent: List[str] = []
    for line in lines:
        if line.startswith("- ") and ":" in line:
            recent.append(line)
    recent.insert(0, f"- {data.get('one_liner')}")
    recent = recent[:recent_n]

    open_gaps: List[str] = []
    for g in data.get("gaps") or []:
        open_gaps.append(f"- [{data.get('task_id')}] {g.get('gap_id')}: {g.get('note')}")

    # Preserve previous open gaps (simple append unique)
    in_open = False
    for line in lines:
        if line.strip() == "## Open gaps":
            in_open = True
            continue
        if in_open and line.startswith("## "):
            break
        if in_open and line.startswith("- "):
            if line not in open_gaps:
                open_gaps.append(line)

    body = (
        header
        + recent
        + ["", "## Open gaps", ""]
        + (open_gaps or ["- (none)"])
        + [""]
    )
    index.write_text("\n".join(body), encoding="utf-8")


def load_memory_yaml(root: Path, task_id: str) -> Optional[Dict[str, Any]]:
    path = root / f"{task_id}.yaml"
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if isinstance(data, dict) else None


def list_recent_memory(root: Path, n: int = 5) -> List[Dict[str, Any]]:
    if not root.exists():
        return []
    files = sorted(root.glob("*.yaml"), key=lambda p: p.stat().st_mtime, reverse=True)
    out: List[Dict[str, Any]] = []
    for path in files[:n]:
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if isinstance(data, dict):
            out.append(data)
    return out


def load_prior_learnings(
    root: Path,
    task: Dict[str, Any],
    *,
    recent_n: int = 5,
    max_chars: int = 1200,
) -> str:
    recent = list_recent_memory(root, recent_n)
    if not recent:
        return "(none)"

    hay = (
        f"{task.get('id', '')} {task.get('description', '')} "
        f"{task.get('category', '')}"
    ).lower()
    # Keep one-liners short; do not list other pending task IDs as work to do.
    parts: List[str] = [
        "### Recent rounds (context only — do NOT implement those task ids)",
    ]
    for m in recent[: min(5, recent_n)]:
        line = str(m.get("one_liner") or m.get("task_id") or "")[:160]
        parts.append(f"- {line}")

    parts.append("\n### Relevant gaps / advice (harden THIS task only if it applies)")
    hit = 0
    for m in recent:
        for g in m.get("gaps") or []:
            gid = str(g.get("gap_id", ""))
            if gid.startswith("failed_"):
                continue  # stage failure is noise for other tasks
            # Require keyword overlap with current task — no blanket authz spam
            related = any(tok in hay for tok in gid.split("_") if len(tok) > 3)
            if gid in {"authz", "mock_default", "skip_sign", "authn_write"}:
                hint_tokens = {
                    "authz": ("admin", "settle", "withdraw", "payout", "filament"),
                    "mock_default": ("auth", "mock", "sf", "payment", "login"),
                    "skip_sign": ("sf", "callback", "sign"),
                    "authn_write": ("boost", "cancel", "withdraw", "order"),
                }.get(gid, ())
                related = related or any(t in hay for t in hint_tokens)
            if not related:
                continue
            parts.append(f"- [{m.get('task_id')}] gap `{gid}`: {g.get('note')}")
            hit += 1
        for a in m.get("advice") or []:
            hint = str(a.get("target_hint") or "").lower()
            tokens = [t for t in hint.split() if len(t) > 3]
            if tokens and not any(t in hay for t in tokens):
                continue
            parts.append(
                f"- advice → consider acceptance: {a.get('suggest_acceptance')} "
                f"(hint: {a.get('target_hint')})"
            )
            hit += 1
            if hit >= 6:
                break
        if hit >= 6:
            break
    if hit == 0:
        parts.append("- (no strongly related gaps)")

    text = "\n".join(parts)
    if len(text) > max_chars:
        text = text[: max_chars - 20] + "\n…(truncated)"
    return text


def agent_refine_memory(
    data: Dict[str, Any],
    *,
    cwd: Path,
    agent_cfg: Dict[str, Any],
    run_agent_fn,
    log_path: Path,
) -> Dict[str, Any]:
    """Optional: ask agent to refine gaps/advice from verify excerpt."""
    prompt = (
        "You refine pipeline memory for a coding pipeline. "
        "Given the task result below, reply with ONLY YAML (no markdown fences) containing:\n"
        "gaps: [{gap_id, note}]\n"
        "advice: [{target_hint, suggest_acceptance}]\n"
        "one_liner: short string\n"
        "Use gap_id from: authz, mock_default, skip_sign, missing_read, authn_write, verify_fail, other.\n"
        "If nothing wrong, gaps: [] and advice: [].\n\n"
        f"task_id: {data.get('task_id')}\n"
        f"impl_ok: {data.get('impl_ok')}\n"
        f"failed_stage: {data.get('failed_stage')}\n"
        f"verify_excerpt:\n{data.get('verify_excerpt')}\n"
    )
    result = run_agent_fn(
        prompt,
        cwd=cwd,
        bin_name=agent_cfg.get("bin") or "agent",
        extra_args=list(
            agent_cfg.get("args")
            or ["-p", "--force", "--output-format", "text", "--model", "cursor-grok-4.5-high"]
        ),
        timeout_sec=min(int(agent_cfg.get("timeout_sec") or 600), 600),
        log_path=log_path,
    )
    raw = (result.stdout or "").strip()
    # strip fences if any
    raw = re.sub(r"^```ya?ml\s*", "", raw)
    raw = re.sub(r"```\s*$", "", raw)
    try:
        parsed = yaml.safe_load(raw)
    except Exception:
        return data
    if not isinstance(parsed, dict):
        return data
    if isinstance(parsed.get("gaps"), list):
        data["gaps"] = parsed["gaps"]
    if isinstance(parsed.get("advice"), list):
        data["advice"] = parsed["advice"]
    if parsed.get("one_liner"):
        data["one_liner"] = str(parsed["one_liner"])
    data["refined_by_agent"] = True
    return data


def after_task_memory(
    *,
    config: Dict[str, Any],
    project_root: Path,
    pipeline_root: Path,
    task: Dict[str, Any],
    impl_ok: bool,
    delivery_ok: bool,
    failed_stage: str = "",
    run_agent_fn=None,
) -> Dict[str, Any]:
    mem_cfg = config.get("memory") or {}
    if mem_cfg.get("enabled", True) is False:
        return {"enabled": False}

    root = memory_dir_from_config(config, project_root)
    data = rule_summarize(
        task, impl_ok=impl_ok, delivery_ok=delivery_ok, failed_stage=failed_stage
    )

    use_agent = bool(mem_cfg.get("use_agent", False))
    only_on_fail = mem_cfg.get("use_agent_only_on_fail", True)
    if use_agent and run_agent_fn and (not only_on_fail or not impl_ok):
        log_path = pipeline_root / "logs" / "memory" / f"{task.get('id')}-refine.md"
        agent_cfg = config.get("agent") or {}
        try:
            data = agent_refine_memory(
                data,
                cwd=project_root,
                agent_cfg=agent_cfg,
                run_agent_fn=run_agent_fn,
                log_path=log_path,
            )
        except Exception as exc:
            data["refine_error"] = str(exc)

    write_task_memory(root, data)
    update_index(root, data, recent_n=int(mem_cfg.get("recent_n") or 10))
    return data
