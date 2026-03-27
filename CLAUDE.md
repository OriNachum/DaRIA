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

## PR Workflow

Every task gets its own branch and PR. Before merging any PR:

1. **Wait for all reviewer comments** (Qodo, Copilot, human reviewers)
2. **Fix** valid issues found by reviewers — commit the fix to the same branch
3. **Pushback** on invalid or non-applicable findings — reply with reasoning
4. **Reply** to every comment thread, confirming fix or explaining pushback
5. **Resolve** all comment threads
6. **Merge** only after all threads are resolved

Never merge a PR with unaddressed review comments.
