---
layout: default
title: Logging
---

<div class="post-content" markdown="1">

# Logging

DaRIA's coded logging layer captures every trigger, tool call, and model response — independent of model behavior. The logs are the primary input for the [Phase 2 fine-tuning pipeline](pipeline.html).

## Format

Append-only JSONL (one JSON object per line). One file per day, rotated at midnight.

**File naming:** `daria-YYYY-MM-DD.jsonl`

**Location:** `<working_directory>/logs/`

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
  "timestamp": "2026-03-27T14:32:01Z"
}
```

`source` values: `"mention"`, `"supervisor"`, `"patrol"`

### tool_call

Every skill invocation — arguments and result.

```json
{
  "kind": "tool_call",
  "data": {
    "skill": "inspect",
    "args": {
      "prs": true,
      "repo": "OriNachum/agentirc",
      "state": "open"
    },
    "result": "PR #14: Add retry backoff to irc_transport — checks passing, 1 approval"
  },
  "timestamp": "2026-03-27T14:32:04Z"
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
  "timestamp": "2026-03-27T14:32:09Z"
}
```

## Hook Points

The three entry kinds map directly to hook points in `daria/daemon/logger.py`:

| Entry kind | Hook | Trigger |
|------------|------|---------|
| `trigger` | `_on_mention()` | Incoming mention or supervisor nudge |
| `tool_call` | `_handle_ipc()` | Every skill invocation |
| `response` | `on_message()` | Every model output |

## Schema Contract

This schema is the contract between Phase 1 (logging) and Phase 2 (pipeline). The Digest stage reads these files verbatim. Do not change field names or structure without updating the pipeline accordingly.

Any schema evolution should be versioned — add a `"schema_version"` field to entries if the format changes.

</div>
