"""Task storage under .pipeline/tasks/{pending,active,done,failed}."""

from __future__ import annotations

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml

SAFE_ID = re.compile(r"^[A-Za-z0-9_-]+$")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def dump_yaml(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, allow_unicode=True, sort_keys=False)


class TaskStore:
    def __init__(self, tasks_dir: str | Path):
        self.root = Path(tasks_dir)
        self.pending = self.root / "pending"
        self.active = self.root / "active"
        self.done = self.root / "done"
        self.failed = self.root / "failed"

    def ensure_dirs(self) -> None:
        for d in (self.pending, self.active, self.done, self.failed):
            d.mkdir(parents=True, exist_ok=True)

    def _bucket_paths(self) -> List[Path]:
        return [self.pending, self.active, self.done, self.failed]

    def find_task_file(self, task_id: str) -> Optional[Path]:
        for bucket in self._bucket_paths():
            for ext in (".yaml", ".yml", ".json"):
                candidate = bucket / f"{task_id}{ext}"
                if candidate.exists():
                    return candidate
        return None

    def list_pending(self) -> List[Path]:
        self.ensure_dirs()
        files = list(self.pending.glob("*.yaml")) + list(self.pending.glob("*.yml"))
        files += list(self.pending.glob("*.json"))

        def sort_key(path: Path):
            try:
                data = self.load_task(path)
                order = data.get("order")
                if isinstance(order, (int, float)):
                    return (0, float(order), path.name)
            except Exception:
                pass
            return (1, 0.0, path.name)

        return sorted(files, key=sort_key)

    def load_task(self, path: Path) -> Dict[str, Any]:
        data = load_yaml(path)
        if not isinstance(data, dict):
            raise ValueError(f"Task file must be a mapping: {path}")
        return data

    def validate_task(self, task: Dict[str, Any]) -> None:
        tid = str(task.get("id", "")).strip()
        if not tid or not SAFE_ID.match(tid):
            raise ValueError(f"Invalid task id: {tid!r}")
        if not str(task.get("description", "")).strip():
            raise ValueError(f"Task {tid}: description required")
        acc = task.get("acceptance")
        if not isinstance(acc, list) or not acc:
            raise ValueError(f"Task {tid}: acceptance must be a non-empty list")

    def write_task(self, task: Dict[str, Any], bucket: str = "pending") -> Path:
        self.validate_task(task)
        self.ensure_dirs()
        buckets = {
            "pending": self.pending,
            "active": self.active,
            "done": self.done,
            "failed": self.failed,
        }
        if bucket not in buckets:
            raise ValueError(f"Unknown bucket: {bucket}")
        # Remove duplicates in other buckets
        existing = self.find_task_file(task["id"])
        path = buckets[bucket] / f"{task['id']}.yaml"
        if existing and existing.resolve() != path.resolve():
            existing.unlink()
        dump_yaml(path, task)
        return path

    def move(self, task_id: str, to_bucket: str) -> Path:
        src = self.find_task_file(task_id)
        if not src:
            raise FileNotFoundError(f"Task not found: {task_id}")
        task = self.load_task(src)
        return self.write_task(task, bucket=to_bucket)

    def ensure_stage_map(
        self, task: Dict[str, Any], stage_ids: Iterable[str]
    ) -> Dict[str, Any]:
        stages = task.setdefault("stages", {})
        for sid in stage_ids:
            stages.setdefault(sid, {"status": "pending", "attempts": 0})
        return task

    def set_stage_status(
        self,
        task: Dict[str, Any],
        stage_id: str,
        status: str,
        *,
        notes: str = "",
        inc_attempt: bool = False,
    ) -> Dict[str, Any]:
        stages = task.setdefault("stages", {})
        entry = stages.setdefault(stage_id, {"status": "pending", "attempts": 0})
        if inc_attempt:
            entry["attempts"] = int(entry.get("attempts") or 0) + 1
        entry["status"] = status
        if status == "done":
            entry["completed_at"] = utc_now()
        if notes:
            entry["notes"] = notes
        stages[stage_id] = entry
        task["stages"] = stages
        return task

    def import_tasks_document(self, data: Any, *, source: str = "") -> List[Path]:
        """Import list or single task from YAML/JSON document."""
        tasks: List[Dict[str, Any]]
        if isinstance(data, dict) and "tasks" in data:
            tasks = data["tasks"]
        elif isinstance(data, dict) and "id" in data:
            tasks = [data]
        elif isinstance(data, list):
            tasks = data
        else:
            raise ValueError("Expected task mapping, list, or {tasks: [...]}")

        written: List[Path] = []
        for item in tasks:
            if not isinstance(item, dict):
                raise ValueError("Each task must be a mapping")
            if source and not item.get("source"):
                item["source"] = source
            written.append(self.write_task(item, bucket="pending"))
        return written

    def clear_active_to_pending(self) -> None:
        self.ensure_dirs()
        for path in list(self.active.glob("*.*")):
            shutil.move(str(path), str(self.pending / path.name))
