"""Adapt pending tasks from memory gaps (suggest | apply)."""

from __future__ import annotations

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import yaml

from memory_store import memory_dir_from_config, utc_now
from task_store import TaskStore, dump_yaml, load_yaml

HINT_MAP = {
    "authz": ("admin", "settle", "withdraw", "payout"),
    "mock_default": ("auth", "mock", "sf", "payment", "login"),
    "skip_sign": ("sf", "callback", "route-push", "sign"),
    "missing_read": ("order", "withdraw", "address", "list", "show"),
    "authn_write": ("boost", "cancel", "withdraw", "order"),
    "verify_fail": (),  # broad — skip auto apply unless hint in advice
}

# Require at least this many token hits before proposing a patch
MIN_MATCH_SCORE = 2


def adaptations_dir(config: Dict[str, Any], project_root: Path) -> Path:
    ad = (config.get("adapt") or {}).get("dir") or ".pipeline/adaptations"
    path = Path(ad)
    if not path.is_absolute():
        path = project_root / path
    return path


def _match_score(task: Dict[str, Any], tokens: Sequence[str]) -> int:
    hay = f"{task.get('id', '')} {task.get('description', '')}".lower()
    return sum(1 for t in tokens if t and t.lower() in hay)


def _is_doc_wrapup(task: Dict[str, Any]) -> bool:
    tid = str(task.get("id") or "").lower()
    desc = str(task.get("description") or "").lower()
    return (
        "doc" in tid
        or "文档" in desc
        or "api.md" in desc
        or "readme" in desc and ("收尾" in desc or "清单" in desc)
    )


def find_pending_targets(
    store: TaskStore,
    *,
    gap_id: str,
    target_hint: str = "",
    exclude_id: str = "",
    min_score: int = MIN_MATCH_SCORE,
) -> List[Path]:
    tokens = list(HINT_MAP.get(gap_id, ()))
    tokens += [t for t in re.split(r"\s+", target_hint or "") if len(t) > 2]
    if not tokens:
        return []
    scored: List[Tuple[int, Path]] = []
    for path in store.list_pending():
        if path.stem == exclude_id:
            continue
        try:
            task = store.load_task(path)
        except Exception:
            continue
        # Never auto-patch DOC wrap-up with AuthZ/Mock noise
        if gap_id in {"authz", "mock_default", "skip_sign"} and _is_doc_wrapup(task):
            continue
        score = _match_score(task, tokens)
        if score >= min_score:
            scored.append((score, path))
    scored.sort(key=lambda x: (-x[0], x[1].name))
    return [p for _, p in scored]


def build_proposals(
    memory: Dict[str, Any],
    store: TaskStore,
    *,
    max_patches: int = 3,
) -> List[Dict[str, Any]]:
    exclude = str(memory.get("task_id") or "")
    proposals: List[Dict[str, Any]] = []
    seen_pending = set()

    # Prefer structured advice
    for advice in memory.get("advice") or []:
        hint = str(advice.get("target_hint") or "")
        acc = str(advice.get("suggest_acceptance") or "").strip()
        if not acc:
            continue
        # infer gap from advice context
        gap_id = "authz"
        low = (hint + " " + acc).lower()
        if "mock" in low or "skip" in low:
            gap_id = "mock_default"
        elif "list" in low or "show" in low or "读" in acc:
            gap_id = "missing_read"
        elif "pii" in low or "认证" in acc:
            gap_id = "authn_write"
        targets = find_pending_targets(
            store, gap_id=gap_id, target_hint=hint, exclude_id=exclude
        )
        for path in targets:
            if path.stem in seen_pending:
                continue
            seen_pending.add(path.stem)
            proposals.append(
                {
                    "pending_id": path.stem,
                    "gap_id": gap_id,
                    "add_acceptance": [acc],
                    "add_description_note": f"[adapt:{gap_id}] {acc[:80]}",
                }
            )
            if len(proposals) >= max_patches:
                return proposals

    for gap in memory.get("gaps") or []:
        if len(proposals) >= max_patches:
            break
        gid = str(gap.get("gap_id") or "")
        if gid in {"verify_fail", "failed_dev", "failed_verify"}:
            continue
        default_acc = {
            "authz": "非特权用户调用本任务特权写接口 → 403（机制：Feature 测试）",
            "mock_default": "Mock/skip-sign 默认关闭（机制：.env.example 或 production 强制关测试）",
            "skip_sign": "第三方回调默认验签；skip-sign 仅显式非 production env",
            "missing_read": "同资源提供 list/show 读闭环（或 acceptance 显式限定子集）",
            "authn_write": "写操作需认证；响应不泄漏他人 PII",
        }.get(gid)
        if not default_acc:
            continue
        targets = find_pending_targets(store, gap_id=gid, exclude_id=exclude)
        for path in targets:
            if path.stem in seen_pending:
                continue
            seen_pending.add(path.stem)
            proposals.append(
                {
                    "pending_id": path.stem,
                    "gap_id": gid,
                    "add_acceptance": [default_acc],
                    "add_description_note": f"[adapt:{gid}] from {exclude}",
                }
            )
            if len(proposals) >= max_patches:
                break
    return proposals


def write_adaptation_file(
    adapt_root: Path,
    memory: Dict[str, Any],
    proposals: List[Dict[str, Any]],
    *,
    applied: bool,
) -> Path:
    adapt_root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    tid = memory.get("task_id") or "unknown"
    path = adapt_root / f"{stamp}_{tid}.yaml"
    doc = {
        "source_task": tid,
        "created_at": utc_now(),
        "gaps": memory.get("gaps") or [],
        "proposals": proposals,
        "applied": applied,
    }
    with path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(doc, fh, allow_unicode=True, sort_keys=False)
    return path


def apply_proposals(
    store: TaskStore,
    proposals: List[Dict[str, Any]],
    *,
    allow_fields: Sequence[str],
    adapt_root: Path,
) -> List[str]:
    applied_ids: List[str] = []
    allow = set(allow_fields or ["acceptance", "description", "verify_command"])
    for prop in proposals:
        pid = prop["pending_id"]
        path = store.pending / f"{pid}.yaml"
        if not path.exists():
            path = store.pending / f"{pid}.yml"
        if not path.exists():
            continue
        # backup
        bak = adapt_root / "bak" / f"{pid}.{datetime.now(timezone.utc).strftime('%H%M%S')}.yaml"
        bak.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, bak)

        task = load_yaml(path)
        if not isinstance(task, dict):
            continue
        if "acceptance" in allow:
            acc = list(task.get("acceptance") or [])
            for item in prop.get("add_acceptance") or []:
                if item and item not in acc:
                    acc.append(item)
            task["acceptance"] = acc
        if "description" in allow and prop.get("add_description_note"):
            note = str(prop["add_description_note"])
            desc = str(task.get("description") or "")
            if note not in desc:
                task["description"] = (desc + "\n" + note).strip()
        dump_yaml(path, task)
        applied_ids.append(pid)
    return applied_ids


def run_adapt(
    *,
    config: Dict[str, Any],
    project_root: Path,
    store: TaskStore,
    memory: Dict[str, Any],
) -> Dict[str, Any]:
    adapt_cfg = config.get("adapt") or {}
    mode = str(adapt_cfg.get("mode") or "off").lower()
    if mode in {"off", "false", "0", ""}:
        return {"mode": "off", "proposals": []}
    if adapt_cfg.get("require_gap_tags", True) and not (memory.get("gaps") or memory.get("advice")):
        return {"mode": mode, "proposals": [], "skipped": "no gaps"}

    max_patches = int(adapt_cfg.get("max_pending_patches_per_round") or 3)
    proposals = build_proposals(memory, store, max_patches=max_patches)
    root = adaptations_dir(config, project_root)
    applied = False
    applied_ids: List[str] = []
    if mode == "apply" and proposals:
        allow = list(
            adapt_cfg.get("allow_fields")
            or ["acceptance", "description", "verify_command"]
        )
        applied_ids = apply_proposals(
            store, proposals, allow_fields=allow, adapt_root=root
        )
        applied = bool(applied_ids)
    path = write_adaptation_file(root, memory, proposals, applied=applied)
    return {
        "mode": mode,
        "proposals": proposals,
        "applied": applied,
        "applied_ids": applied_ids,
        "file": str(path),
    }
