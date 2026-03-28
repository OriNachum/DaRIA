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

Set the `DARIA_NICK` environment variable to your agent's nick (e.g. `spark-daria`).
The IRC tools resolve the socket path automatically:

    $XDG_RUNTIME_DIR/daria-<nick>.sock   (falls back to /tmp/daria-<nick>.sock)

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

    python3 -c "import asyncio, sys; from daria.skills.investigate import fetch_page; print(asyncio.run(fetch_page(sys.argv[1])))" "https://docs.example.com/api"

## inspect — examine code and git history

### Read a file

    python3 -c "import asyncio, sys; from daria.skills.inspect import read_file; print(asyncio.run(read_file(sys.argv[1])))" "path/to/file.py"

### Git log

    python3 -c "import asyncio, sys; from daria.skills.inspect import git_log; print(asyncio.run(git_log(sys.argv[1], count=int(sys.argv[2]))))" "path/to/repo" 10

### Git diff

    python3 -c "import asyncio, sys; from daria.skills.inspect import git_diff; print(asyncio.run(git_diff(sys.argv[1])))" "path/to/repo"

### Search files

    python3 -c "import asyncio, sys; from daria.skills.inspect import grep_files; print(asyncio.run(grep_files(sys.argv[1], sys.argv[2])))" "pattern" "path/to/search"

### List PRs

    python3 -c "import asyncio, sys; from daria.skills.inspect import list_prs; print(asyncio.run(list_prs(sys.argv[1])))" "path/to/repo"

All commands print JSON to stdout. Always check the `ok` field in the response.
