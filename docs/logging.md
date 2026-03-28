---
layout: default
title: Logging
---

<div class="post-content" markdown="1">

# Logging

DaRIA's coded logging layer captures every trigger, tool call, and model response — independent of model behavior. The logs are the primary input for the [Phase 2 fine-tuning pipeline](../pipeline/).

## Format

Append-only JSONL (one JSON object per line). One file per UTC day, rotated at midnight UTC.

**File naming:** `daria-YYYY-MM-DD.jsonl`

**Location:** `<agent_directory>/logs/` (from `AgentConfig.directory`)

Example: `~/git/daria/logs/daria-2026-03-27.jsonl`

## Schema

Three entry kinds. Each entry has a top-level `kind`, a `data` object, and a `timestamp`.

### trigger

What prompted a turn — a mention, supervisor nudge, or patrol event.

```json
{
  "kind": "trigger",
  "data": {
    "source": "mention",
    "sender": "ori",
    "channel": "#code-review",
    "text": "@daria can you look at PR #14?"
  },
  "timestamp": "2026-03-27T14:32:01+00:00"
}
```

`source` values: `"mention"`, `"supervisor"`, `"patrol"`

### tool_call

Every skill invocation — arguments and result.

```json
{
  "kind": "tool_call",
  "data": {
    "skill": "irc_read",
    "args": {
      "channel": "#general",
      "limit": "50"
    },
    "result": {"ok": true}
  },
  "timestamp": "2026-03-27T14:32:04+00:00"
}
```

### response

Every model output — the text and where it was sent.

```json
{
  "kind": "response",
  "data": {
    "text": "PR #14 looks good — all checks pass and the retry logic is bounded. Approving.",
    "destinations": ["#code-review"]
  },
  "timestamp": "2026-03-27T14:32:09+00:00"
}
```

## Hook Points

The three entry kinds map directly to hook points in `daria/daemon/daemon.py`:

| Entry kind | Hook | Trigger |
|------------|------|---------|
| `trigger` | `_on_mention()` | Incoming mention or supervisor nudge |
| `tool_call` | `_handle_ipc()` | Every skill invocation |
| `response` | `_on_agent_message()` | Every model output |

## Schema Contract

This schema is the contract between Phase 1 (logging) and Phase 2 (pipeline). The Digest stage reads these files verbatim. Do not change field names or structure without updating the pipeline accordingly.

Any schema evolution should be versioned — add a `"schema_version"` field to entries if the format changes.

</div>
