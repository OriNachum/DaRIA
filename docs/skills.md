---
layout: default
title: Skills
---

<div class="post-content" markdown="1">

# Skills

DaRIA has six skills. Four are thin wrappers on existing AgentIRC IPC infrastructure. Two require new code.

| Skill | Implementation | Source |
|-------|---------------|--------|
| observe | irc_read + HISTORY skill | AgentIRC IPC (thin wrapper) |
| investigate | Playwright headless browser | New code — `daria/skills/investigate.py` |
| inspect | git, gh, filesystem | New code — `daria/skills/inspect.py` |
| decide | irc_send + irc_ask | AgentIRC IPC (thin wrapper) |
| ask | irc_ask | AgentIRC IPC (thin wrapper) |
| journal | irc_send → #daria-journal | AgentIRC IPC (thin wrapper) |

---

## observe

Read and digest mesh activity.

**Built on:** `irc_read`, AgentIRC `HISTORY` server skill.

Uses the AgentIRC IPC `HISTORY` command to read recent messages from any channel, search history for topics or keywords, and track who said what. Ori's interjections are flagged as high-priority signals.

**Usage:**

```
observe channel=#general limit=50
observe channel=#code-review search="PR review"
observe channel=#decisions since=2h
```

---

## investigate

Research the web autonomously via Playwright (headless).

**New code:** `daria/skills/investigate.py` — Playwright subprocess management, URL safety validation, response summarization.

Browse URLs, search for documentation, read GitHub issues, and summarize findings back to the mesh.

**Usage:**

```
investigate url=https://docs.example.com/api
investigate query="playwright python async subprocess"
investigate url=https://github.com/owner/repo/issues/42
```

---

## inspect

Examine code, commits, and PRs.

**New code:** `daria/skills/inspect.py` — git, gh, and filesystem tool implementations.

Read files, grep codebases, check git log, review open PRs and their diffs, track Assimilai package status across repos, correlate code changes with mesh conversations.

**Usage:**

```
inspect git_log repo=~/git/agentirc limit=20
inspect diff repo=~/git/daria ref=HEAD~3
inspect file path=~/git/daria/daria/daemon/logger.py
inspect grep pattern="LogEntry" repo=~/git/daria
inspect prs repo=OriNachum/agentirc state=open
```

---

## decide

Propose and take actions.

**Built on:** `irc_send`, `irc_ask` (AgentIRC IPC).

Post decisions to `#daria-journal` with reasoning, assign tasks to agents via @mention, escalate to Ori when confidence is low.

**Usage:**

```
decide action="assign PR review" target="@spark-claude" context="PR #14 in agentirc"
decide action="approve merge" repo=agentirc pr=14 confidence=0.9
decide action="escalate" question="Should we deprecate irc_read?" target="@ori"
```

---

## ask

Consult advisors when uncertain.

**Built on:** `irc_ask` (AgentIRC IPC).

@mention Ori or advisor agents with a specific question framed with context (what was observed, what DaRIA thinks). Waits for a response before proceeding and records advice as feedback for future decisions.

**Usage:**

```
ask target="@ori" question="Should I merge this PR?" context="All checks pass, one approval"
ask target="@spark-claude" question="Is this pattern safe?" context="Seeing retry loops in #code-review"
```

---

## journal

Record observations and decisions to `#daria-journal`.

**Built on:** `irc_send` to `#daria-journal` (AgentIRC IPC).

Post structured entries tagged by type. Other agents can query the journal via `HISTORY`. Journal entries supplement the coded logging for the fine-tuning pipeline.

Entry types: `observation`, `decision`, `question`, `feedback`.

**Usage:**

```
journal type=observation text="Noticed spike in #code-review activity around AgentIRC IPC changes"
journal type=decision text="Approved PR #14 — all checks passed, pattern matches known-good merges"
journal type=feedback text="Ori corrected my assessment of the retry logic — note for future: retries need timeout bounds"
```

</div>
