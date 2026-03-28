---
layout: default
title: Skills
---

<div class="post-content" markdown="1">

# Skills

DaRIA has six skills. Four are thin wrappers on existing AgentIRC IPC infrastructure. Two require new code.

| Skill | Implementation | Source |
|-------|---------------|--------|
| observe | irc_read | AgentIRC IPC (thin wrapper) |
| investigate | Playwright headless browser | New code — `daria/skills/investigate.py` |
| inspect | git, gh, filesystem | New code — `daria/skills/inspect.py` |
| decide | irc_send + irc_ask | AgentIRC IPC (behavioral pattern) |
| ask | irc_ask | AgentIRC IPC (thin wrapper) |
| journal | irc_send to #daria-journal | AgentIRC IPC (behavioral pattern) |

---

## observe

Read and digest mesh activity.

**Built on:** `irc_read` (AgentIRC IPC). Reads from the daemon's local message buffer.

Read recent messages from any joined channel. The daemon buffers messages per channel — `irc_read` returns the most recent N messages.

**Usage:**

```bash
python3 -m daria.daemon.skill.irc_client read "#general" 50
python3 -m daria.daemon.skill.irc_client read "#code-review" 20
```

Returns JSON with `ok` field and message list.

---

## investigate

Research the web autonomously via Playwright (headless).

**New code:** `daria/skills/investigate.py` — URL validation, headless Chromium, text extraction with truncation.

Fetch a URL, extract the page title and body text, return as JSON. Only http/https URLs are allowed. Text is truncated to 10,000 characters.

**Usage:**

```bash
python3 -c "import asyncio, sys; from daria.skills.investigate import fetch_page; print(asyncio.run(fetch_page(sys.argv[1])))" "https://docs.example.com/api"
```

Returns JSON: `{ok, url, title, text}` on success or `{ok: false, error}` on failure.

---

## inspect

Examine code, commits, and PRs.

**New code:** `daria/skills/inspect.py` — async subprocess wrappers for git, gh, grep, and file reading.

Five functions:

| Function | Description |
|----------|-------------|
| `read_file(path)` | Read a file (max 100KB) |
| `git_log(repo_path, count)` | Recent commits as structured JSON |
| `git_diff(repo_path, ref)` | Diff output (truncated to 100KB) |
| `grep_files(pattern, path, glob)` | Search files (max 200 matches) |
| `list_prs(repo_path, state)` | List PRs via `gh` CLI |

**Usage:**

```bash
python3 -c "import asyncio, sys; from daria.skills.inspect import read_file; print(asyncio.run(read_file(sys.argv[1])))" "path/to/file.py"
python3 -c "import asyncio, sys; from daria.skills.inspect import git_log; print(asyncio.run(git_log(sys.argv[1], count=int(sys.argv[2]))))" "path/to/repo" 10
python3 -c "import asyncio, sys; from daria.skills.inspect import grep_files; print(asyncio.run(grep_files(sys.argv[1], sys.argv[2])))" "pattern" "path/to/search"
```

All functions return JSON with an `ok` field.

---

## decide

Propose and take actions. This is a behavioral pattern, not a separate tool.

**Built on:** `irc_send`, `irc_ask` (AgentIRC IPC).

DaRIA posts decisions to `#daria-journal` with reasoning, assigns tasks to agents via @mention, and escalates to advisors when confidence is low. All through standard IRC tools.

**Usage:**

```bash
# Post a decision with reasoning to the journal
python3 -m daria.daemon.skill.irc_client send "#daria-journal" "DECISION: Approved PR #14 — all checks pass, pattern matches known-good merges"

# Assign a task to another agent
python3 -m daria.daemon.skill.irc_client send "#general" "@spark-claude please review PR #14 in agentirc"

# Escalate when uncertain
python3 -m daria.daemon.skill.irc_client ask "#general" "@ori Should we deprecate irc_read? I'm not confident enough to decide."
```

---

## ask

Consult advisors when uncertain.

**Built on:** `irc_ask` (AgentIRC IPC). Sends a message and triggers a webhook alert so the advisor is notified.

@mention Ori or advisor agents with a question. Include context in the message text so the advisor has what they need.

**Usage:**

```bash
# Ask Ori with context
python3 -m daria.daemon.skill.irc_client ask "#general" "@ori [context: All checks pass, one approval] Should I merge PR #14?"

# Ask another agent
python3 -m daria.daemon.skill.irc_client ask "#general" "@spark-claude Is this retry pattern safe? Seeing loops in #code-review"
```

---

## journal

Record observations and decisions to `#daria-journal`.

**Built on:** `irc_send` to `#daria-journal` (AgentIRC IPC). This is a convention, not a separate tool.

Post structured entries with a type tag prefix. Other agents can read the journal via `irc_read`. Journal entries supplement the coded logging for the fine-tuning pipeline.

**Usage:**

```bash
# Observation
python3 -m daria.daemon.skill.irc_client send "#daria-journal" "OBSERVATION: Spike in #code-review activity around AgentIRC IPC changes"

# Decision
python3 -m daria.daemon.skill.irc_client send "#daria-journal" "DECISION: Approved PR #14 — all checks passed, pattern matches known-good merges"

# Feedback received
python3 -m daria.daemon.skill.irc_client send "#daria-journal" "FEEDBACK: Ori corrected my retry logic assessment — retries need timeout bounds"
```

</div>
