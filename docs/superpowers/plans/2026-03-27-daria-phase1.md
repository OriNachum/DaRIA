# DaRIA Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build DaRIA as a working AgentIRC agent with skills for observation, investigation, code inspection, and decision-making, plus coded logging hooks for the future fine-tuning pipeline.

**Architecture:** Standard AgentIRC OpenCode agent (thin agent, fat skills). Daemon files copied from AgentIRC's OpenCode backend via the assimilai pattern. New code: JSONL logger, Playwright investigate skill, git/gh inspect skill. Jekyll site matching Assimilai's styling.

**Tech Stack:** Python 3.12+, uv, hatchling, asyncio, Playwright, pytest + pytest-asyncio, Jekyll 4.3

---

## File Map

### New files (DaRIA-specific)

| File | Responsibility |
|------|---------------|
| `daria/__init__.py` | Package version |
| `daria/daemon/logger.py` | JSONL coded logging (triggers, tool calls, model outputs) |
| `daria/skills/investigate.py` | Playwright web browsing tool |
| `daria/skills/inspect.py` | git + gh + filesystem tool |
| `skills/daria/SKILL.md` | Tool definitions installed into agent env |
| `config/agents.example.yaml` | Example agents.yaml entry |
| `tests/conftest.py` | Shared fixtures |
| `tests/test_logger.py` | Logger tests |
| `tests/test_investigate.py` | Investigate skill tests |
| `tests/test_inspect.py` | Inspect skill tests |
| `pyproject.toml` | Project config |
| `CLAUDE.md` | Dev instructions |
| `CHANGELOG.md` | Release notes |

### Copied from AgentIRC OpenCode backend (assimilai pattern)

Source: `/home/spark/git/agentirc/agentirc/clients/opencode/`

| File | Status |
|------|--------|
| `daria/daemon/agent_runner.py` | As-is (update imports only) |
| `daria/daemon/irc_transport.py` | As-is (update imports only) |
| `daria/daemon/message_buffer.py` | As-is (update imports only) |
| `daria/daemon/socket_server.py` | As-is (update imports only) |
| `daria/daemon/ipc.py` | As-is (update imports only) |
| `daria/daemon/webhook.py` | As-is (update imports only) |
| `daria/daemon/config.py` | Adapted (DaRIA defaults) |
| `daria/daemon/daemon.py` | Adapted (logging hooks) |
| `daria/daemon/supervisor.py` | Adapted (DaRIA eval prompts) |
| `daria/daemon/skill/irc_client.py` | As-is (update imports only) |

### Jekyll site files

| File | Responsibility |
|------|---------------|
| `index.md` | Homepage |
| `_config.yml` | Site config |
| `Gemfile` | Ruby dependencies |
| `_layouts/default.html` | Page template (from Assimilai) |
| `assets/css/style.css` | Theme (from Assimilai, DaRIA colors) |

### Documentation

| File | Responsibility |
|------|---------------|
| `docs/overview.md` | What DaRIA is, ecosystem fit |
| `docs/skills.md` | Skill reference |
| `docs/logging.md` | JSONL log format and schema |
| `docs/pipeline.md` | Phase 2 fine-tuning spec |

---

## Task 1: Project Scaffolding

**Files:**

- Create: `pyproject.toml`
- Create: `daria/__init__.py`
- Create: `CLAUDE.md`
- Create: `CHANGELOG.md`

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "daria"
version = "0.1.0"
description = "Data Refinery Intelligent Agent — the awareness pillar of Organic Development"
readme = "README.md"
requires-python = ">=3.12"
license = "MIT"
authors = [{ name = "Ori Nachum" }]
dependencies = [
    "pyyaml>=6.0",
]

[project.optional-dependencies]
investigate = ["playwright>=1.40"]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.25",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
```

- [ ] **Step 2: Create daria/__init__.py**

```python
__version__ = "0.1.0"
```

- [ ] **Step 3: Create CLAUDE.md**

```markdown
# DaRIA Development Guide

## Quick Reference

- **Run tests:** `uv run pytest -v`
- **Install dev deps:** `uv sync --extra dev`
- **Install Playwright:** `uv sync --extra investigate && uv run playwright install chromium`

## Architecture

DaRIA is an AgentIRC agent (OpenCode backend). The daemon files in `daria/daemon/`
are copied from AgentIRC's OpenCode backend via the assimilai pattern — DaRIA owns
these files and can modify them independently.

New code unique to DaRIA:
- `daria/daemon/logger.py` — JSONL coded logging
- `daria/skills/investigate.py` — Playwright web browsing
- `daria/skills/inspect.py` — git/gh/filesystem inspection

## Conventions

- Python 3.12+, async/await throughout
- Type hints on all public functions
- Tests use real instances, no mocks (following AgentIRC convention)
- Commits follow conventional style: feat/fix/docs/refactor
```

- [ ] **Step 4: Create CHANGELOG.md**

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added

- Project scaffolding
```

- [ ] **Step 5: Create empty package directories**

```bash
mkdir -p daria/daemon/skill daria/skills tests skills/daria config docs
touch daria/daemon/__init__.py daria/daemon/skill/__init__.py daria/skills/__init__.py tests/__init__.py
```

- [ ] **Step 6: Initialize uv and verify**

Run: `uv sync --extra dev`
Expected: Lock file created, dependencies installed.

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml daria/ tests/ CLAUDE.md CHANGELOG.md
git commit -m "feat: project scaffolding with pyproject.toml, package structure, dev guide"
```

---

## Task 2: Copy Daemon Files (Assimilai Pattern)

**Files:**

- Create: `daria/daemon/agent_runner.py` (copy)
- Create: `daria/daemon/irc_transport.py` (copy)
- Create: `daria/daemon/message_buffer.py` (copy)
- Create: `daria/daemon/socket_server.py` (copy)
- Create: `daria/daemon/ipc.py` (copy)
- Create: `daria/daemon/webhook.py` (copy)
- Create: `daria/daemon/config.py` (copy)
- Create: `daria/daemon/daemon.py` (copy)
- Create: `daria/daemon/supervisor.py` (copy)
- Create: `daria/daemon/skill/irc_client.py` (copy)

- [ ] **Step 1: Copy all daemon files from AgentIRC OpenCode backend**

```bash
cp /home/spark/git/agentirc/agentirc/clients/opencode/agent_runner.py daria/daemon/
cp /home/spark/git/agentirc/agentirc/clients/opencode/irc_transport.py daria/daemon/
cp /home/spark/git/agentirc/agentirc/clients/opencode/message_buffer.py daria/daemon/
cp /home/spark/git/agentirc/agentirc/clients/opencode/socket_server.py daria/daemon/
cp /home/spark/git/agentirc/agentirc/clients/opencode/ipc.py daria/daemon/
cp /home/spark/git/agentirc/agentirc/clients/opencode/webhook.py daria/daemon/
cp /home/spark/git/agentirc/agentirc/clients/opencode/config.py daria/daemon/
cp /home/spark/git/agentirc/agentirc/clients/opencode/daemon.py daria/daemon/
cp /home/spark/git/agentirc/agentirc/clients/opencode/supervisor.py daria/daemon/
cp /home/spark/git/agentirc/agentirc/clients/opencode/skill/irc_client.py daria/daemon/skill/
```

- [ ] **Step 2: Update all imports from `agentirc.clients.opencode` to `daria.daemon`**

In every copied file, replace:

```python
# Old
from agentirc.clients.opencode.config import ...
from agentirc.clients.opencode.ipc import ...
# etc.

# New
from daria.daemon.config import ...
from daria.daemon.ipc import ...
# etc.
```

Apply to all files. The import prefix `agentirc.clients.opencode` becomes `daria.daemon` everywhere.

Also update any `agentirc.clients.opencode.skill` references to `daria.daemon.skill`.

- [ ] **Step 3: Update config.py defaults for DaRIA**

In `daria/daemon/config.py`, change the AgentConfig default:

```python
@dataclass
class AgentConfig:
    nick: str = ""
    agent: str = "opencode"
    directory: str = "."
    channels: list[str] = field(default_factory=lambda: ["#general", "#daria-journal"])
    model: str = "nvidia/nemotron-3-nano"
```

- [ ] **Step 4: Verify imports resolve**

Run: `uv run python -c "from daria.daemon.ipc import make_response; print('ok')"`
Expected: `ok`

- [ ] **Step 5: Commit**

```bash
git add daria/daemon/
git commit -m "feat: copy AgentIRC OpenCode daemon files (assimilai pattern)

Source: agentirc/clients/opencode/
Imports updated from agentirc.clients.opencode → daria.daemon
Config defaults adapted for DaRIA (Nemotron Nano, #daria-journal)"
```

---

## Task 3: JSONL Logger (TDD)

**Files:**

- Create: `tests/test_logger.py`
- Create: `daria/daemon/logger.py`

- [ ] **Step 1: Write failing tests for logger**

```python
"""Tests for DaRIA coded logging."""
from __future__ import annotations

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from daria.daemon.logger import DaRIALogger, LogEntry


class TestLogEntry:
    def test_trigger_entry(self) -> None:
        entry = LogEntry.trigger(
            source="mention",
            sender="ori",
            channel="#general",
            text="should we use Redis?",
        )
        assert entry.kind == "trigger"
        assert entry.data["source"] == "mention"
        assert entry.data["sender"] == "ori"
        assert isinstance(entry.timestamp, str)

    def test_tool_call_entry(self) -> None:
        entry = LogEntry.tool_call(
            skill="investigate",
            args={"url": "https://example.com"},
            result={"ok": True, "summary": "Example page"},
        )
        assert entry.kind == "tool_call"
        assert entry.data["skill"] == "investigate"

    def test_response_entry(self) -> None:
        entry = LogEntry.response(
            text="I recommend SQLite",
            destinations=["#general", "#daria-journal"],
        )
        assert entry.kind == "response"
        assert entry.data["destinations"] == ["#general", "#daria-journal"]

    def test_to_json_is_valid_jsonl(self) -> None:
        entry = LogEntry.trigger(source="patrol", sender="daria", channel=None, text="")
        line = entry.to_json()
        parsed = json.loads(line)
        assert parsed["kind"] == "trigger"
        assert "timestamp" in parsed


class TestDaRIALogger:
    def test_log_creates_daily_file(self, tmp_path: Path) -> None:
        logger = DaRIALogger(log_dir=tmp_path)
        entry = LogEntry.trigger(source="test", sender="test", channel=None, text="hello")
        logger.log(entry)

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = tmp_path / f"daria-{today}.jsonl"
        assert log_file.exists()

        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 1
        parsed = json.loads(lines[0])
        assert parsed["kind"] == "trigger"

    def test_log_appends_multiple_entries(self, tmp_path: Path) -> None:
        logger = DaRIALogger(log_dir=tmp_path)
        logger.log(LogEntry.trigger(source="a", sender="x", channel=None, text=""))
        logger.log(LogEntry.response(text="reply", destinations=["#general"]))

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = tmp_path / f"daria-{today}.jsonl"
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 2

    def test_log_dir_created_if_missing(self, tmp_path: Path) -> None:
        log_dir = tmp_path / "subdir" / "logs"
        logger = DaRIALogger(log_dir=log_dir)
        logger.log(LogEntry.trigger(source="test", sender="test", channel=None, text=""))
        assert log_dir.exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_logger.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'daria.daemon.logger'`

- [ ] **Step 3: Implement logger.py**

```python
"""JSONL coded logging for DaRIA.

Append-only daily log files that capture triggers, tool calls, and model
outputs.  These logs are the primary input for the phase 2 fine-tuning
pipeline — treat the schema as a contract once established.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class LogEntry:
    kind: str
    data: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @classmethod
    def trigger(
        cls,
        source: str,
        sender: str,
        channel: str | None,
        text: str,
    ) -> LogEntry:
        return cls(
            kind="trigger",
            data={"source": source, "sender": sender, "channel": channel, "text": text},
        )

    @classmethod
    def tool_call(
        cls,
        skill: str,
        args: dict[str, Any],
        result: dict[str, Any],
    ) -> LogEntry:
        return cls(
            kind="tool_call",
            data={"skill": skill, "args": args, "result": result},
        )

    @classmethod
    def response(
        cls,
        text: str,
        destinations: list[str],
    ) -> LogEntry:
        return cls(
            kind="response",
            data={"text": text, "destinations": destinations},
        )

    def to_json(self) -> str:
        return json.dumps(
            {"kind": self.kind, "data": self.data, "timestamp": self.timestamp},
            ensure_ascii=False,
        )


class DaRIALogger:
    """Append-only JSONL logger, one file per UTC day."""

    def __init__(self, log_dir: str | Path) -> None:
        self._log_dir = Path(log_dir)

    def _log_path(self) -> Path:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self._log_dir / f"daria-{today}.jsonl"

    def log(self, entry: LogEntry) -> None:
        self._log_dir.mkdir(parents=True, exist_ok=True)
        with open(self._log_path(), "a", encoding="utf-8") as f:
            f.write(entry.to_json() + "\n")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_logger.py -v`
Expected: All 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add daria/daemon/logger.py tests/test_logger.py
git commit -m "feat: JSONL coded logging for triggers, tool calls, and responses"
```

---

## Task 4: Wire Logging Hooks into Daemon

**Files:**

- Modify: `daria/daemon/daemon.py` (add logging hooks to three methods)

- [ ] **Step 1: Add logger import and initialization to daemon**

At the top of `daria/daemon/daemon.py`, add:

```python
from daria.daemon.logger import DaRIALogger, LogEntry
```

In `__init__()`, add:

```python
self._logger: DaRIALogger | None = None
```

In `start()`, after MessageBuffer initialization, add:

```python
log_dir = Path(self.agent.directory) / "logs"
self._logger = DaRIALogger(log_dir=log_dir)
```

- [ ] **Step 2: Add trigger logging to `_on_mention()`**

In `_on_mention()`, after the existing logic that formats the prompt, add before `send_prompt`:

```python
if self._logger:
    self._logger.log(LogEntry.trigger(
        source="mention",
        sender=sender,
        channel=target if target.startswith("#") else None,
        text=text,
    ))
```

- [ ] **Step 3: Add tool call logging to `_handle_ipc()`**

In `_handle_ipc()`, after computing the response from the handler, add before returning:

```python
if self._logger and msg_type not in ("compact", "clear", "shutdown"):
    self._logger.log(LogEntry.tool_call(
        skill=msg_type,
        args={k: v for k, v in msg.items() if k not in ("type", "id")},
        result={"ok": response.get("ok", False)},
    ))
```

- [ ] **Step 4: Add response logging to `_on_agent_message()`**

In `_on_agent_message()`, after extracting text and sending to IRC, add:

```python
if self._logger:
    destinations = [relay_target] if relay_target else []
    full_text = "\n".join(
        block.get("text", "")
        for block in msg.get("content", [])
        if block.get("type") == "text"
    )
    self._logger.log(LogEntry.response(text=full_text, destinations=destinations))
```

- [ ] **Step 5: Verify daemon still imports cleanly**

Run: `uv run python -c "from daria.daemon.daemon import OpenCodeDaemon; print('ok')"`

Note: This may fail if the daemon imports AgentIRC-specific modules not available in DaRIA's environment. If so, the import error will indicate which dependencies need to be added to `pyproject.toml` or which imports need conditional handling. Fix any import issues before proceeding.

Expected: `ok` (or fix import issues first)

- [ ] **Step 6: Commit**

```bash
git add daria/daemon/daemon.py
git commit -m "feat: wire coded logging hooks into daemon (_on_mention, _handle_ipc, _on_agent_message)"
```

---

## Task 5: Adapt Supervisor for DaRIA

**Files:**

- Modify: `daria/daemon/supervisor.py`

- [ ] **Step 1: Update the evaluation prompt in supervisor**

In `daria/daemon/supervisor.py`, find the `_build_eval_prompt()` method (or the string that contains the supervisor's evaluation instructions). Replace the generic agent evaluation with DaRIA-specific guidance:

```python
EVAL_PROMPT = """You are supervising DaRIA, an autonomous decision-making agent.

Review the last {window_size} turns. Evaluate whether DaRIA is:
- Observing mesh activity regularly (patrol)
- Journaling decisions to #daria-journal with reasoning
- Asking advisors when confidence is low instead of guessing
- Investigating unfamiliar topics before making decisions
- Following up on past decisions

Verdict (pick one):
OK — DaRIA is operating well, no intervention needed.
CORRECTION <message> — redirect DaRIA (e.g., "You haven't patrolled channels recently, check #general and #code-review for activity")
THINK_DEEPER <message> — prompt reflection (e.g., "Your last decision was made quickly — reconsider whether you had enough information")
ESCALATION <message> — DaRIA is stuck or making repeated poor decisions, escalate to Ori
"""
```

- [ ] **Step 2: Verify supervisor imports cleanly**

Run: `uv run python -c "from daria.daemon.supervisor import OpenCodeSupervisor; print('ok')"`
Expected: `ok` (or fix import issues)

- [ ] **Step 3: Commit**

```bash
git add daria/daemon/supervisor.py
git commit -m "feat: adapt supervisor with DaRIA-specific evaluation prompts"
```

---

## Task 6: Investigate Skill — Playwright (TDD)

**Files:**

- Create: `tests/test_investigate.py`
- Create: `daria/skills/investigate.py`

- [ ] **Step 1: Write failing tests**

```python
"""Tests for the investigate skill (Playwright web browsing)."""
from __future__ import annotations

import json

import pytest

from daria.skills.investigate import fetch_page, format_result


class TestFormatResult:
    def test_formats_success(self) -> None:
        result = format_result(
            url="https://example.com",
            title="Example",
            text="Hello world",
            ok=True,
        )
        parsed = json.loads(result)
        assert parsed["ok"] is True
        assert parsed["url"] == "https://example.com"
        assert parsed["title"] == "Example"
        assert "Hello world" in parsed["text"]

    def test_formats_error(self) -> None:
        result = format_result(
            url="https://bad.example",
            title="",
            text="",
            ok=False,
            error="Connection refused",
        )
        parsed = json.loads(result)
        assert parsed["ok"] is False
        assert "Connection refused" in parsed["error"]

    def test_truncates_long_text(self) -> None:
        long_text = "x" * 20000
        result = format_result(url="https://example.com", title="T", text=long_text, ok=True)
        parsed = json.loads(result)
        assert len(parsed["text"]) <= 10000


class TestFetchPage:
    @pytest.mark.asyncio
    async def test_rejects_non_http_url(self) -> None:
        result = await fetch_page("file:///etc/passwd")
        parsed = json.loads(result)
        assert parsed["ok"] is False
        assert "http" in parsed["error"].lower()

    @pytest.mark.asyncio
    async def test_rejects_empty_url(self) -> None:
        result = await fetch_page("")
        parsed = json.loads(result)
        assert parsed["ok"] is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_investigate.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'daria.skills.investigate'`

- [ ] **Step 3: Implement investigate.py**

```python
"""Investigate skill — browse the web via Playwright.

Provides headless web browsing for autonomous research. Used by DaRIA
to look up documentation, read GitHub issues, and research topics.
"""
from __future__ import annotations

import asyncio
import json
from urllib.parse import urlparse

MAX_TEXT_LENGTH = 10000


def format_result(
    url: str,
    title: str,
    text: str,
    ok: bool,
    error: str | None = None,
) -> str:
    """Format a page fetch result as JSON."""
    truncated = text[:MAX_TEXT_LENGTH] if len(text) > MAX_TEXT_LENGTH else text
    payload: dict = {"ok": ok, "url": url}
    if ok:
        payload["title"] = title
        payload["text"] = truncated
    else:
        payload["error"] = error or "Unknown error"
    return json.dumps(payload, ensure_ascii=False)


async def fetch_page(url: str, timeout_ms: int = 15000) -> str:
    """Fetch a page with Playwright and return its text content as JSON.

    Returns JSON string with ok, url, title, text (or error).
    """
    if not url:
        return format_result(url=url, title="", text="", ok=False, error="Empty URL")

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return format_result(
            url=url, title="", text="", ok=False,
            error=f"Only http/https URLs are allowed, got: {parsed.scheme or 'none'}",
        )

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        return format_result(
            url=url, title="", text="", ok=False,
            error="Playwright not installed. Run: uv sync --extra investigate && uv run playwright install chromium",
        )

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
            title = await page.title()
            text = await page.inner_text("body")
            await browser.close()
            return format_result(url=url, title=title, text=text, ok=True)
    except Exception as exc:
        return format_result(url=url, title="", text="", ok=False, error=str(exc))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_investigate.py -v`
Expected: All 5 tests PASS. (The async tests that reject bad URLs don't need Playwright installed.)

- [ ] **Step 5: Commit**

```bash
git add daria/skills/investigate.py tests/test_investigate.py
git commit -m "feat: investigate skill — Playwright web browsing with URL validation"
```

---

## Task 7: Inspect Skill — git/gh/filesystem (TDD)

**Files:**

- Create: `tests/test_inspect.py`
- Create: `daria/skills/inspect.py`

- [ ] **Step 1: Write failing tests**

```python
"""Tests for the inspect skill (git/gh/filesystem)."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from daria.skills.inspect import (
    git_log,
    git_diff,
    read_file,
    grep_files,
    list_prs,
)


class TestReadFile:
    @pytest.mark.asyncio
    async def test_reads_existing_file(self, tmp_path: Path) -> None:
        f = tmp_path / "hello.txt"
        f.write_text("hello world")
        result = await read_file(str(f))
        parsed = json.loads(result)
        assert parsed["ok"] is True
        assert parsed["content"] == "hello world"

    @pytest.mark.asyncio
    async def test_rejects_missing_file(self) -> None:
        result = await read_file("/nonexistent/path/file.txt")
        parsed = json.loads(result)
        assert parsed["ok"] is False

    @pytest.mark.asyncio
    async def test_rejects_directory(self, tmp_path: Path) -> None:
        result = await read_file(str(tmp_path))
        parsed = json.loads(result)
        assert parsed["ok"] is False


class TestGitLog:
    @pytest.mark.asyncio
    async def test_git_log_in_repo(self) -> None:
        # Run against the daria repo itself (has at least one commit)
        result = await git_log(repo_path=".", count=5)
        parsed = json.loads(result)
        assert parsed["ok"] is True
        assert isinstance(parsed["commits"], list)
        assert len(parsed["commits"]) > 0

    @pytest.mark.asyncio
    async def test_git_log_invalid_repo(self, tmp_path: Path) -> None:
        result = await git_log(repo_path=str(tmp_path), count=5)
        parsed = json.loads(result)
        assert parsed["ok"] is False


class TestGrepFiles:
    @pytest.mark.asyncio
    async def test_grep_finds_pattern(self, tmp_path: Path) -> None:
        f = tmp_path / "code.py"
        f.write_text("def hello():\n    return 'world'\n")
        result = await grep_files(pattern="hello", path=str(tmp_path))
        parsed = json.loads(result)
        assert parsed["ok"] is True
        assert len(parsed["matches"]) > 0

    @pytest.mark.asyncio
    async def test_grep_no_matches(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.py"
        f.write_text("pass\n")
        result = await grep_files(pattern="nonexistent_xyz", path=str(tmp_path))
        parsed = json.loads(result)
        assert parsed["ok"] is True
        assert len(parsed["matches"]) == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_inspect.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'daria.skills.inspect'`

- [ ] **Step 3: Implement inspect.py**

```python
"""Inspect skill — examine code, commits, and PRs.

Provides git, gh, and filesystem tools for DaRIA to understand
what's happening in codebases on the mesh.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

MAX_FILE_SIZE = 100_000  # 100KB


async def _run(cmd: list[str], cwd: str | None = None) -> tuple[int, str, str]:
    """Run a subprocess and return (returncode, stdout, stderr)."""
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd,
    )
    stdout, stderr = await proc.communicate()
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
        ["grep", "-rn", "--include", glob, pattern, path],
    )
    # grep returns 1 for no matches (not an error)
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_inspect.py -v`
Expected: All 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add daria/skills/inspect.py tests/test_inspect.py
git commit -m "feat: inspect skill — git log, diff, file read, grep, PR listing"
```

---

## Task 8: SKILL.md and Configuration

**Files:**

- Create: `skills/daria/SKILL.md`
- Create: `config/agents.example.yaml`

- [ ] **Step 1: Create SKILL.md with all tool definitions**

```markdown
---
name: daria
description: >
  DaRIA agent skills — observe mesh activity, investigate the web,
  inspect code, make decisions, ask advisors, and journal observations.
  Use when DaRIA needs to interact with the AgentIRC mesh, browse the
  web, or examine codebases.
---

# DaRIA Skills

These skills give DaRIA its capabilities on the AgentIRC mesh.

## Setup

Set the `AGENTIRC_NICK` environment variable to your agent's nick (e.g. `spark-daria`).
The IRC tools resolve the socket path automatically:

    $XDG_RUNTIME_DIR/agentirc-<nick>.sock   (falls back to /tmp/agentirc-<nick>.sock)

## IRC Commands (observe, decide, ask, journal)

All IRC commands use `python3 -m daria.daemon.skill.irc_client`.

### read — observe channel activity

    python3 -m daria.daemon.skill.irc_client read "#general" 50

### send — post a message or decision

    python3 -m daria.daemon.skill.irc_client send "#daria-journal" "OBSERVATION: Agent spark-codex stalled on PR #12"

### ask — consult an advisor (sends + triggers webhook alert)

    python3 -m daria.daemon.skill.irc_client ask "#general" "@ori should I approve this PR?"

### join — join a channel

    python3 -m daria.daemon.skill.irc_client join "#code-review"

### part — leave a channel

    python3 -m daria.daemon.skill.irc_client part "#code-review"

### channels — list joined channels

    python3 -m daria.daemon.skill.irc_client channels

### who — list channel members or look up a nick

    python3 -m daria.daemon.skill.irc_client who "#general"

## investigate — browse the web

Use Playwright to fetch and read web pages. For researching documentation,
GitHub issues, Stack Overflow, and other resources.

    python3 -c "
    import asyncio, sys
    from daria.skills.investigate import fetch_page
    print(asyncio.run(fetch_page(sys.argv[1])))
    " "https://docs.example.com/api"

## inspect — examine code and git history

### Read a file

    python3 -c "
    import asyncio, sys
    from daria.skills.inspect import read_file
    print(asyncio.run(read_file(sys.argv[1])))
    " "path/to/file.py"

### Git log

    python3 -c "
    import asyncio, sys
    from daria.skills.inspect import git_log
    print(asyncio.run(git_log(sys.argv[1], count=int(sys.argv[2]))))
    " "/home/spark/git/agentirc" 10

### Git diff

    python3 -c "
    import asyncio, sys
    from daria.skills.inspect import git_diff
    print(asyncio.run(git_diff(sys.argv[1])))
    " "/home/spark/git/agentirc"

### Search files

    python3 -c "
    import asyncio, sys
    from daria.skills.inspect import grep_files
    print(asyncio.run(grep_files(sys.argv[1], sys.argv[2])))
    " "pattern" "/home/spark/git/agentirc"

### List PRs

    python3 -c "
    import asyncio, sys
    from daria.skills.inspect import list_prs
    print(asyncio.run(list_prs(sys.argv[1])))
    " "/home/spark/git/agentirc"

All commands print JSON to stdout. Always check the `ok` field in the response.
```

- [ ] **Step 2: Create agents.example.yaml**

```yaml
# DaRIA agent configuration for ~/.agentirc/agents.yaml
#
# Bootstrap with:
#   cd ~/git/daria && agentirc init --server spark --agent opencode --nick daria
#
# Then edit ~/.agentirc/agents.yaml to match this template.

server:
  name: spark
  host: localhost
  port: 6667

supervisor:
  model: nvidia/nemotron-3-super
  window_size: 20
  eval_interval: 5
  escalation_threshold: 3

webhooks:
  url: null  # Set to your Discord/Slack webhook URL
  irc_channel: "#alerts"
  events:
    - agent_spiraling
    - agent_error
    - agent_question
    - agent_timeout

buffer_size: 500

agents:
  - nick: spark-daria
    agent: opencode
    directory: /home/spark/git/daria
    channels:
      - "#general"
      - "#code-review"
      - "#decisions"
      - "#daria-journal"
    model: nvidia/nemotron-3-nano
```

- [ ] **Step 3: Commit**

```bash
git add skills/daria/SKILL.md config/agents.example.yaml
git commit -m "feat: SKILL.md tool definitions and example agent configuration"
```

---

## Task 9: Jekyll Site

**Files:**

- Create: `_config.yml`
- Create: `Gemfile`
- Create: `_layouts/default.html`
- Create: `assets/css/style.css`
- Modify: `index.md`

- [ ] **Step 1: Create _config.yml**

```yaml
title: DaRIA
description: "Data Refinery Intelligent Agent — the awareness pillar of Organic Development"
author: Ori Nachum
url: "https://daria.autonomous-intelligence.org"
baseurl: ""

permalink: pretty

markdown: kramdown
highlighter: rouge

kramdown:
  toc_levels: 2..3

plugins:
  - jekyll-feed
  - jekyll-sitemap
  - jekyll-seo-tag

exclude:
  - README.md
  - LICENSE
  - CLAUDE.md
  - Gemfile.lock
  - .claude/
  - .superpowers/
  - pyproject.toml
  - uv.lock
  - tests/
  - daria/
  - skills/
  - config/
```

- [ ] **Step 2: Create Gemfile**

```ruby
source "https://rubygems.org"

gem "jekyll", "~> 4.3"
gem "webrick"
gem "jekyll-feed"
gem "jekyll-sitemap"
gem "jekyll-seo-tag"
```

- [ ] **Step 3: Create _layouts/default.html**

Copy from Assimilai verbatim (`/home/spark/git/assimilai/_layouts/default.html`), updating only the nav links:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% if page.title %}{{ page.title }} | {{ site.title }}{% else %}{{ site.title }}{% endif %}</title>
  {% seo %}
  {% feed_meta %}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Fira+Code:wght@400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{{ '/assets/css/style.css' | relative_url }}">
  <script>
    (function() {
      var theme;
      try { theme = localStorage.getItem('theme'); } catch(e) {}
      if (!theme) {
        theme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      }
      if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
      }
    })();
  </script>
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": {{ site.title | jsonify }},
    "description": {{ site.description | jsonify }},
    "url": {{ site.url | append: site.baseurl | append: "/" | jsonify }},
    "author": {
      "@type": "Person",
      "name": {{ site.author | jsonify }}
    }
  }
  </script>
</head>
<body>
  <header class="site-header">
    <a class="site-title" href="{{ '/' | relative_url }}">{{ site.title }}</a>
    <nav class="site-nav">
      <a href="{{ '/' | relative_url }}">Home</a>
      <a href="{{ '/docs/overview' | relative_url }}">Docs</a>
      <button class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle dark mode" aria-pressed="false">
        <span class="icon-sun" aria-hidden="true">&#9728;</span>
        <span class="icon-moon" aria-hidden="true">&#9790;</span>
      </button>
    </nav>
  </header>

  <main>
    {{ content }}
  </main>

  <footer class="site-footer">
    &copy; {{ 'now' | date: "%Y" }} {{ site.author }}.
    Licensed under <a href="https://opensource.org/licenses/MIT">MIT</a>.
  </footer>

  <script>
    function toggleTheme() {
      var current = document.documentElement.getAttribute('data-theme');
      var next = current === 'dark' ? 'light' : 'dark';
      if (next === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
      } else {
        document.documentElement.removeAttribute('data-theme');
      }
      var btn = document.querySelector('.theme-toggle');
      if (btn) btn.setAttribute('aria-pressed', next === 'dark');
      try { localStorage.setItem('theme', next); } catch(e) {}
    }
  </script>
</body>
</html>
```

- [ ] **Step 4: Create assets/css/style.css**

Copy Assimilai's `style.css` verbatim from `/home/spark/git/assimilai/assets/css/style.css`. The accent color `#D97706` (warm orange) is shared across the Organic Development ecosystem — keep it consistent.

- [ ] **Step 5: Rewrite index.md as DaRIA homepage**

```markdown
---
layout: default
title: Home
---

<div class="hero">
  <h1>DaRIA</h1>
  <p>Data Refinery Intelligent Agent &mdash; the awareness pillar of Organic Development.</p>
</div>

<div class="star-badge">
  <iframe src="https://ghbtns.com/github-btn.html?user=OriNachum&repo=daria&type=star&count=true" frameborder="0" scrolling="0" width="150" height="20" title="GitHub Stars" loading="lazy" referrerpolicy="no-referrer"></iframe>
</div>

<div class="post-content" markdown="1">

## What is DaRIA?

DaRIA is an autonomous decision-making agent that lives on the [AgentIRC](https://agentirc.dev) mesh. It observes conversations, investigates topics, inspects code, and makes decisions — like an intern reporting to the head of a company.

DaRIA is the third pillar of [Organic Development](https://autonomous-intelligence.org):

| Pillar | Project | Role |
|--------|---------|------|
| Propagation | [Assimilai](https://assimilai.dev) | Code spreads across the mesh |
| Coordination | [AgentIRC](https://agentirc.dev) | Agents communicate and collaborate |
| Awareness | **DaRIA** | The system observes, learns, and improves |

## How It Works

DaRIA is a standard AgentIRC agent — set up with `agentirc init`, running on the mesh like any other agent. What makes it different is what it does:

- **Observe** — reads channel history, tracks decisions, notes human corrections
- **Investigate** — browses the web autonomously to research topics
- **Inspect** — examines code, commits, PRs across repositories
- **Decide** — proposes actions, assigns tasks, escalates when unsure
- **Ask** — consults advisors (human or agent) with framed questions
- **Journal** — posts structured observations to #daria-journal

## The Refinery

DaRIA refines its own judgment. During the day it acts on the mesh. At night it *dreams* — replaying the day's experiences through simulated scenarios, evaluating its own performance, and fine-tuning its model on what it learns.

The fine-tuning pipeline runs locally on NVIDIA Blackwell hardware:

- **Nemotron 3 Super** (Jetson Thor) — the dungeon master, presenting situations
- **Nemotron 3 Nano** (DGX Spark) — the dreamer, responding as if each scenario is real
- Self-evaluation scores drive reinforcement learning
- Each morning, DaRIA wakes up with better instincts

## Quick Start

```bash
cd ~/git/daria
agentirc init --server spark --agent opencode --nick daria
# Edit ~/.agentirc/agents.yaml (see config/agents.example.yaml)
agentirc start spark-daria
```

</div>
```

- [ ] **Step 6: Commit**

```bash
git add _config.yml Gemfile _layouts/ assets/ index.md
git commit -m "feat: Jekyll site with Assimilai-style theme and DaRIA homepage"
```

---

## Task 10: Documentation

**Files:**

- Create: `docs/overview.md`
- Create: `docs/skills.md`
- Create: `docs/logging.md`
- Create: `docs/pipeline.md`

- [ ] **Step 1: Create docs/overview.md**

Write a page covering: what DaRIA is, how it fits the Organic Development ecosystem, architecture (thin agent, fat skills), and the two-layer hook system. Reference the spec at `docs/superpowers/specs/2026-03-27-daria-design.md` for the full architecture diagram. Add Jekyll front matter: `layout: default`, `title: Overview`.

- [ ] **Step 2: Create docs/skills.md**

Write a skill reference page documenting all six skills (observe, investigate, inspect, decide, ask, journal) with usage examples matching the SKILL.md format. Add Jekyll front matter.

- [ ] **Step 3: Create docs/logging.md**

Document the JSONL log format and schema. Include:
- The three entry kinds: trigger, tool_call, response
- JSON structure for each kind (match the LogEntry dataclass)
- File naming: `daria-YYYY-MM-DD.jsonl`
- Location: `<working_directory>/logs/`
- Note: this schema is a contract for the phase 2 pipeline
- Add Jekyll front matter.

- [ ] **Step 4: Create docs/pipeline.md**

Extract the Phase 2 pipeline section from the design spec into a standalone document. Cover all five stages (Digest, Dream, Evaluate, Fine-Tune, Deploy), hardware allocation, the training signal format, and the organic metaphor. Mark clearly as "Phase 2 — documented for future implementation." Add Jekyll front matter.

- [ ] **Step 5: Commit**

```bash
git add docs/overview.md docs/skills.md docs/logging.md docs/pipeline.md
git commit -m "docs: overview, skills reference, logging schema, and pipeline architecture"
```

---

## Task 11: Update README

**Files:**

- Modify: `README.md`

- [ ] **Step 1: Rewrite README.md**

Replace the placeholder with a proper README covering:
- One-line description
- What DaRIA is (2-3 sentences)
- Organic Development ecosystem table (Assimilai, AgentIRC, DaRIA)
- Quick start (4 commands: init, configure, install skills, start)
- Skills list (one line each)
- Link to docs site
- License (MIT)

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: rewrite README with quick start and ecosystem context"
```

---

## Task 12: Integration Smoke Test

**Files:**

- Create: `tests/conftest.py`
- Create: `tests/test_smoke.py`

- [ ] **Step 1: Create conftest.py with shared fixtures**

```python
"""Shared test fixtures for DaRIA."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_log_dir(tmp_path: Path) -> Path:
    """Temporary directory for log files."""
    return tmp_path / "logs"
```

- [ ] **Step 2: Write smoke tests**

```python
"""Smoke tests — verify all modules import and basic wiring works."""
from __future__ import annotations

import json

import pytest


class TestImports:
    def test_import_logger(self) -> None:
        from daria.daemon.logger import DaRIALogger, LogEntry
        assert DaRIALogger is not None

    def test_import_investigate(self) -> None:
        from daria.skills.investigate import fetch_page, format_result
        assert fetch_page is not None

    def test_import_inspect(self) -> None:
        from daria.skills.inspect import read_file, git_log, grep_files
        assert read_file is not None

    def test_import_ipc(self) -> None:
        from daria.daemon.ipc import make_response, make_request
        assert make_response is not None

    def test_version(self) -> None:
        from daria import __version__
        assert __version__ == "0.1.0"


class TestLoggerIntegration:
    def test_full_cycle(self, tmp_log_dir) -> None:
        from daria.daemon.logger import DaRIALogger, LogEntry

        logger = DaRIALogger(log_dir=tmp_log_dir)

        # Log all three entry types
        logger.log(LogEntry.trigger(source="mention", sender="ori", channel="#general", text="hello"))
        logger.log(LogEntry.tool_call(skill="investigate", args={"url": "https://example.com"}, result={"ok": True}))
        logger.log(LogEntry.response(text="Done", destinations=["#general"]))

        # Verify JSONL output
        log_files = list(tmp_log_dir.glob("daria-*.jsonl"))
        assert len(log_files) == 1

        lines = log_files[0].read_text().strip().split("\n")
        assert len(lines) == 3

        kinds = [json.loads(line)["kind"] for line in lines]
        assert kinds == ["trigger", "tool_call", "response"]
```

- [ ] **Step 3: Run full test suite**

Run: `uv run pytest -v`
Expected: All tests PASS across test_logger.py, test_investigate.py, test_inspect.py, test_smoke.py.

- [ ] **Step 4: Commit**

```bash
git add tests/conftest.py tests/test_smoke.py
git commit -m "test: smoke tests verifying all imports and logger integration"
```
