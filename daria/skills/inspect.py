"""Inspect skill — examine code, commits, and PRs.

Provides git, gh, and filesystem tools for DaRIA to understand
what's happening in codebases on the mesh.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

MAX_FILE_SIZE = 100_000
SUBPROCESS_TIMEOUT = 60.0


async def _run(cmd: list[str], cwd: str | None = None) -> tuple[int, str, str]:
    """Run a subprocess and return (returncode, stdout, stderr)."""
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )
    except (FileNotFoundError, OSError) as exc:
        return 127, "", str(exc)
    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=SUBPROCESS_TIMEOUT,
        )
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except ProcessLookupError:
            pass
        return 124, "", f"Command timed out after {SUBPROCESS_TIMEOUT}s"
    return proc.returncode, stdout.decode(errors="replace"), stderr.decode(errors="replace")


async def read_file(path: str, max_size: int = MAX_FILE_SIZE) -> str:
    """Read a file and return its content as JSON."""
    try:
        p = Path(path)
        if not p.is_file():
            return json.dumps({"ok": False, "error": f"Not a file: {path}"})
        if p.stat().st_size > max_size:
            return json.dumps({"ok": False, "error": f"File too large: {p.stat().st_size} bytes"})
        content = p.read_text(encoding="utf-8", errors="replace")
        return json.dumps({"ok": True, "path": path, "content": content})
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)})


async def git_log(repo_path: str, count: int = 20) -> str:
    """Get recent git log as JSON."""
    rc, out, err = await _run(
        ["git", "log", f"--max-count={count}", "--format=%H|%an|%ai|%s"],
        cwd=repo_path,
    )
    if rc != 0:
        return json.dumps({"ok": False, "error": err.strip() or "git log failed"})

    commits = []
    for line in out.strip().split("\n"):
        if not line:
            continue
        parts = line.split("|", 3)
        if len(parts) == 4:
            commits.append({
                "hash": parts[0],
                "author": parts[1],
                "date": parts[2],
                "message": parts[3],
            })
    return json.dumps({"ok": True, "commits": commits})


async def git_diff(repo_path: str, ref: str = "HEAD") -> str:
    """Get git diff as JSON."""
    rc, out, err = await _run(["git", "diff", ref], cwd=repo_path)
    if rc != 0:
        return json.dumps({"ok": False, "error": err.strip() or "git diff failed"})
    return json.dumps({"ok": True, "diff": out[:MAX_FILE_SIZE]})


async def grep_files(pattern: str, path: str, glob: str = "*") -> str:
    """Search files for a pattern using grep."""
    rc, out, err = await _run(
        ["grep", "-rn", "--include", glob, "--", pattern, path],
    )
    if rc not in (0, 1):
        return json.dumps({"ok": False, "error": err.strip() or "grep failed"})

    matches = []
    for line in out.strip().split("\n"):
        if not line:
            continue
        matches.append(line)
    return json.dumps({"ok": True, "matches": matches[:200]})


async def list_prs(repo_path: str, state: str = "open") -> str:
    """List PRs using gh CLI."""
    rc, out, err = await _run(
        ["gh", "pr", "list", "--state", state, "--json", "number,title,author,url"],
        cwd=repo_path,
    )
    if rc != 0:
        return json.dumps({"ok": False, "error": err.strip() or "gh pr list failed"})
    try:
        prs = json.loads(out)
        return json.dumps({"ok": True, "prs": prs})
    except json.JSONDecodeError:
        return json.dumps({"ok": False, "error": "Failed to parse gh output"})
