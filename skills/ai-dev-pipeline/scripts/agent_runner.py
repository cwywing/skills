"""Invoke Cursor Agent CLI (agent -p --force ...)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

# Windows CreateProcess command-line limit is 8191. Stay under with headroom
# for cmd.exe + agent.cmd path + args.
WIN_CMDLINE_LIMIT = 8191
WIN_CMDLINE_SAFE = 7200


@dataclass
class AgentResult:
    returncode: int
    stdout: str
    stderr: str
    started_at: str
    finished_at: str
    command: List[str] = field(default_factory=list)
    parsed: Optional[Dict[str, Any]] = None
    prompt_file: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def which_agent(bin_name: str = "agent") -> Optional[str]:
    return shutil.which(bin_name)


def ensure_agent_available(bin_name: str = "agent") -> str:
    path = which_agent(bin_name)
    if not path:
        raise RuntimeError(
            f"Cursor CLI `{bin_name}` not found on PATH. "
            "Install from https://cursor.com/docs and run `agent login`, "
            "or set CURSOR_API_KEY."
        )
    return path


def estimate_cmdline_len(parts: Sequence[str]) -> int:
    # Rough Windows cmdline length (spaces between args).
    return sum(len(p) + 1 for p in parts)


def build_command(
    prompt: str,
    *,
    bin_name: str = "agent",
    extra_args: Optional[Sequence[str]] = None,
) -> List[str]:
    resolved = ensure_agent_available(bin_name)
    args = list(extra_args or ["-p", "--force", "--output-format", "json"])
    # Windows: .cmd/.bat cannot be executed directly with shell=False
    if os.name == "nt" and resolved.lower().endswith((".cmd", ".bat")):
        return ["cmd.exe", "/c", resolved, *args, prompt]
    return [resolved, *args, prompt]


def _pointer_prompt(prompt_path: Path, original_len: int) -> str:
    path = str(prompt_path.resolve())
    return (
        f"Open and read this UTF-8 file, then follow ALL instructions in it exactly. "
        f"Do not skip sections. Path:\n{path}\n"
        f"(Full prompt is only in that file; {original_len} chars.)"
    )


def prepare_prompt_for_cli(
    prompt: str,
    *,
    bin_name: str = "agent",
    extra_args: Optional[Sequence[str]] = None,
    prompt_file_dir: Optional[Path] = None,
) -> tuple[str, Optional[Path]]:
    """
    On Windows, if argv would exceed CreateProcess limit, spill prompt to a
    temp file and return a short pointer prompt the agent can Read.
    """
    cmd = build_command(prompt, bin_name=bin_name, extra_args=extra_args)
    needs_file = os.name == "nt" and (
        estimate_cmdline_len(cmd) > WIN_CMDLINE_SAFE or len(prompt) > 5500
    )
    if not needs_file:
        return prompt, None

    directory = prompt_file_dir
    if directory is None:
        directory = Path(tempfile.gettempdir()) / "ai-dev-pipeline-prompts"
    directory.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix="agent-prompt-", suffix=".md", dir=str(directory))
    path = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(prompt)
    except Exception:
        try:
            os.close(fd)
        except OSError:
            pass
        raise

    short = _pointer_prompt(path, len(prompt))
    # Recheck; pointer should always be short.
    cmd2 = build_command(short, bin_name=bin_name, extra_args=extra_args)
    if estimate_cmdline_len(cmd2) > WIN_CMDLINE_LIMIT - 200:
        # Extreme paths: still truncate pointer (should never happen)
        short = short[:2000]
    return short, path


def run_agent(
    prompt: str,
    *,
    cwd: str | Path,
    bin_name: str = "agent",
    extra_args: Optional[Sequence[str]] = None,
    timeout_sec: Optional[int] = 1800,
    env: Optional[Dict[str, str]] = None,
    log_path: Optional[Path] = None,
) -> AgentResult:
    """Run headless agent. Writes prompt + stdout/stderr to log_path when set."""
    prompt_dir = log_path.parent if log_path else None
    effective_prompt, prompt_file = prepare_prompt_for_cli(
        prompt,
        bin_name=bin_name,
        extra_args=extra_args,
        prompt_file_dir=prompt_dir,
    )
    cmd = build_command(effective_prompt, bin_name=bin_name, extra_args=extra_args)
    started = datetime.now(timezone.utc).isoformat()
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)

    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        spill_note = (
            f"# prompt_file: {prompt_file}\n" if prompt_file else "# prompt_file: (inline)\n"
        )
        log_path.write_text(
            f"# command: {' '.join(cmd[:6])} ...\n# started: {started}\n{spill_note}\n"
            f"## PROMPT\n{prompt}\n\n"
            + (
                f"## PROMPT_ARGV (spilled; short pointer)\n{effective_prompt}\n\n"
                if prompt_file
                else ""
            ),
            encoding="utf-8",
        )

    try:
        completed = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_sec,
            env=merged_env,
            shell=False,
        )
        finished = datetime.now(timezone.utc).isoformat()
        result = AgentResult(
            returncode=completed.returncode,
            stdout=completed.stdout or "",
            stderr=completed.stderr or "",
            started_at=started,
            finished_at=finished,
            command=cmd,
            prompt_file=str(prompt_file) if prompt_file else None,
        )
    except subprocess.TimeoutExpired as exc:
        finished = datetime.now(timezone.utc).isoformat()
        result = AgentResult(
            returncode=124,
            stdout=(exc.stdout or "") if isinstance(exc.stdout, str) else "",
            stderr=((exc.stderr or "") if isinstance(exc.stderr, str) else "")
            + f"\nTIMEOUT after {timeout_sec}s",
            started_at=started,
            finished_at=finished,
            command=cmd,
            prompt_file=str(prompt_file) if prompt_file else None,
        )

    if result.stdout.strip().startswith("{") or result.stdout.strip().startswith("["):
        try:
            result.parsed = json.loads(result.stdout)
        except json.JSONDecodeError:
            result.parsed = None

    if log_path:
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(f"## STDOUT\n{result.stdout}\n\n")
            fh.write(f"## STDERR\n{result.stderr}\n\n")
            fh.write(
                f"## META\nreturncode={result.returncode}\n"
                f"finished={result.finished_at}\n"
                f"prompt_spilled={bool(prompt_file)}\n"
            )

    return result


def auth_hint() -> str:
    if os.environ.get("CURSOR_API_KEY"):
        return "CURSOR_API_KEY is set."
    return "CURSOR_API_KEY not set; ensure `agent login` was completed."


if __name__ == "__main__":
    try:
        path = ensure_agent_available()
        print(f"OK: {path}")
        print(auth_hint())
    except RuntimeError as err:
        print(err, file=sys.stderr)
        sys.exit(1)
