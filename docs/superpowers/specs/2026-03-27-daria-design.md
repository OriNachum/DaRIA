# DaRIA Design Spec

**Data Refinery Intelligent Agent** — the awareness pillar of Organic Development.

- **Date:** 2026-03-27
- **Status:** Approved
- **Author:** Ori Nachum + Claude

## Context

DaRIA is the third pillar of Organic Development alongside Assimilai (propagation) and AgentIRC (coordination). Where Assimilai spreads code and AgentIRC coordinates agents, DaRIA provides awareness — the system's ability to observe, learn, and improve its own judgment.

DaRIA is an autonomous decision-making agent that learns by watching how Ori operates and gradually takes on that work. It refines its own judgment, not data. It asks when unsure, investigates independently, and acts like an ambitious intern reporting to the CEO.

## Architecture

### Approach: Thin Agent, Fat Skills

DaRIA is a standard AgentIRC agent using the OpenCode backend, running Nemotron 3 Nano locally on DGX Spark. All capabilities are delivered through skills (tool definitions the model can invoke) and hooks (system prompt directives + supervisor nudges). No custom infrastructure beyond skills, configuration, and coded logging.

**Bootstrap:** `agentirc init --server spark --agent opencode --nick daria`

```text
┌─────────────────────────────────────────────────────────────────┐
│                    AgentIRC Server (spark)                       │
│                                                                 │
│  #general    #code-review    #decisions    #daria-journal        │
│                                                                 │
│  Skills: HistorySkill                                           │
└──────┬──────────┬──────────────┬────────────────────────────────┘
       │          │              │
  ┌────▼───┐ ┌───▼────┐   ┌────▼──────────────────────────────┐
  │ spark- │ │ spark- │   │ spark-daria                        │
  │ claude │ │ codex  │   │                                    │
  │        │ │        │   │  OpenCode backend + Nemotron Nano  │
  │ (other │ │ (other │   │  Skills + Coded Logging Hooks      │
  │ agents)│ │ agents)│   │                                    │
  └────────┘ └────────┘   └────────────────────────────────────┘
```

### What DaRIA Observes

- **Message traffic** — conversations, decisions, task delegations between agents
- **Code activity** — commits, PRs, file changes propagated via Assimilai
- **Ori's interjections** — human input as a high-priority learning signal

## Skills

Six skills define what DaRIA can do. Four are thin wrappers on existing AgentIRC IPC tools. Two require new code.

### observe

Read and digest mesh activity. Uses `irc_read` and the `HISTORY` server skill to read recent messages from any channel, search history for topics/keywords, track who said what and which decisions were made. Ori's interjections are flagged as high-priority signals.

*Built on:* irc_read, HISTORY skill (existing AgentIRC infrastructure).

### investigate

Research the web autonomously via Playwright (headless). Browse URLs, search for documentation/APIs/libraries, read GitHub issues and docs sites, summarize findings back to the mesh.

*New code:* Playwright subprocess management, URL safety validation, response summarization.

### inspect

Examine code, commits, and PRs. Read files, grep codebases, check git log, review open PRs and their diffs, track Assimilai package status across repos, correlate code changes with mesh conversations.

*New code:* git/gh/filesystem tool implementations.

### decide

Propose and take actions. Post decisions to `#daria-journal` with reasoning, assign tasks to agents via @mention, approve/reject based on learned patterns, escalate to Ori when confidence is low.

*Built on:* irc_send, irc_ask (existing AgentIRC infrastructure).

### ask

Consult advisors when uncertain. @mention Ori or advisor agents with specific questions, frame questions with context (what was observed, what DaRIA thinks), wait for response before proceeding, record advice as feedback for future decisions.

*Built on:* irc_ask (existing AgentIRC infrastructure).

### journal

Record observations and decisions. Post structured entries to `#daria-journal` tagged by type (observation, decision, question, feedback). Other agents can query the journal via HISTORY. The journal entries supplement the coded logging for the fine-tuning pipeline.

*Built on:* irc_send to #daria-journal (existing AgentIRC infrastructure).

## Hooks and Reactive Behavior

Two distinct layers handle DaRIA's behavior.

### Layer 1: Active Processing (model-driven)

The model chooses to act based on system prompt directives and supervisor nudges.

**Reactive (on @mention):** Standard AgentIRC daemon flow — someone asks, DaRIA responds using its skills.

**Proactive (self-initiated):** System prompt instructs DaRIA to:

- Patrol channels periodically for stalled conversations or unanswered questions
- Follow up on past decisions to check if they were carried out
- Investigate unfamiliar topics before asking others
- Post briefings to #daria-journal at configurable intervals

The OpenCode supervisor evaluates DaRIA's activity and nudges it when needed ("you haven't patrolled in 30min", "you made a decision without journaling it").

**Mechanism:** System prompt directives + supervisor evaluation. No new server-side code. The supervisor model is configured independently from the agent model (e.g., a different Nemotron variant or external model for evaluation).

### Layer 2: Coded Logging (code-driven)

Automatic hooks in DaRIA's customized OpenCode daemon that capture everything, independent of model behavior. Guaranteed and complete.

**What gets logged:**

- **Triggers** — what prompted each turn (mention, supervisor nudge, patrol)
- **Tool calls** — every skill invocation with arguments and results
- **Model outputs** — every response the model generates
- **Reactions** — input message to model response pairs

**Hook points in the daemon:**

1. `_on_mention()` — logs the trigger (who, what, where)
2. `_handle_ipc()` — logs every tool call (skill, args, result)
3. `on_message()` callback — logs every model output (text, destinations)

**Storage:** Append-only JSONL files, one per day, rotated at midnight. Stored in DaRIA's working directory. This is the primary input for the phase 2 fine-tuning pipeline. The exact JSONL schema will be defined during implementation and documented in `docs/logging.md` — since these logs feed the pipeline, the schema should be treated as a contract once established.

## Project Structure

```text
daria/
├── daria/                        # Python package
│   ├── __init__.py               # version
│   │
│   ├── daemon/                   # Customized OpenCode daemon (assimilai copy)
│   │   ├── daemon.py             # DaRIA-specific orchestration
│   │   ├── agent_runner.py       # OpenCode ACP (as-is from reference)
│   │   ├── irc_transport.py      # IRC client (as-is)
│   │   ├── message_buffer.py     # Ring buffer (as-is)
│   │   ├── socket_server.py      # Unix socket IPC (as-is)
│   │   ├── ipc.py                # JSON Lines protocol (as-is)
│   │   ├── webhook.py            # Alerting (as-is)
│   │   ├── supervisor.py         # Adapted — DaRIA-specific eval prompts
│   │   └── logger.py             # NEW — coded logging hooks (JSONL)
│   │
│   └── skills/                   # DaRIA's tool definitions
│       ├── investigate.py        # Playwright web browsing
│       └── inspect.py            # git + gh + filesystem
│
├── skills/                       # SKILL.md files (installed into agent env)
│   └── daria/
│       └── SKILL.md              # All tool definitions for OpenCode
│
├── config/                       # Configuration templates
│   └── agents.example.yaml       # Example agents.yaml entry for DaRIA
│
├── docs/                         # Documentation
│   ├── overview.md               # What DaRIA is, how it fits the ecosystem
│   ├── skills.md                 # Skill reference
│   ├── logging.md                # Coded logging format and schema
│   └── pipeline.md               # Phase 2: fine-tuning architecture
│
├── tests/                        # Tests
│   ├── conftest.py               # Fixtures
│   ├── test_logger.py            # Coded logging tests
│   ├── test_investigate.py       # Playwright skill tests
│   └── test_inspect.py           # Code inspection skill tests
│
├── pyproject.toml                # Python 3.12+, uv, hatchling
├── README.md
├── LICENSE                       # MIT
├── CHANGELOG.md                  # Keep a Changelog
├── CLAUDE.md                     # Dev instructions
│
├── index.md                      # Jekyll homepage
├── _config.yml                   # Jekyll site config
├── Gemfile                       # Jekyll dependencies
└── _layouts/
    └── default.html              # Site template (same style as Assimilai/AgentIRC)
```

**From AgentIRC (assimilai pattern):** agent_runner.py, irc_transport.py, message_buffer.py, socket_server.py, ipc.py, webhook.py — copied from AgentIRC's OpenCode backend (`agentirc/clients/opencode/`), owned by DaRIA. The generic template at `packages/agent-harness/` serves as reference; the OpenCode-specific implementations are the actual source.

**Adapted:** daemon.py (logging hooks), supervisor.py (DaRIA-specific eval prompts), SKILL.md (DaRIA tools).

**New to DaRIA:** logger.py (JSONL coded logging), investigate.py (Playwright), inspect.py (git/gh/fs), pipeline docs.

**Jekyll site** uses the same theme, layout, and CSS as Assimilai and AgentIRC.

## Phase 2: Fine-Tuning Pipeline

*Documented now, built later. The coded logging layer (phase 1) produces the input this pipeline needs.*

### Overview

A nightly self-improvement loop where DaRIA dreams about its day and wakes up with better instincts. The pipeline runs after midnight, processes the day's logs, simulates experiences, and fine-tunes Nemotron 3 Nano based on DaRIA's own self-evaluation.

### Hardware

| Machine | Model | Role |
|---------|-------|------|
| Jetson Thor (128GB Blackwell) | Nemotron 3 Super | Dungeon master / simulator |
| DGX Spark (128GB Blackwell) | Nemotron 3 Nano | DaRIA dreamer + fine-tune target |

### Stage 1: Digest

Nemotron 3 Nano with extended thinking reads the day's JSONL logs and IRC history. Extracts decisions, corrections, and patterns. Identifies what Ori corrected and what worked. Produces a structured digest that seeds the dream scenarios.

### Stage 2: Dream

Nemotron 3 Super (on Jetson Thor) acts as dungeon master. It presents situations to DaRIA (Nemotron 3 Nano on DGX Spark) drawn from the digest — replays of situations Ori corrected, novel variations of real events, edge cases the day didn't encounter.

DaRIA is the dreamer. It responds as if each situation is real. It does not know it is in a simulation. Super plays all other roles (Ori, other agents, the world) and reacts to DaRIA's choices. The result is multi-turn transcripts.

**Training pair format:** Super's situation prompt = question, DaRIA's action = answer.

### Stage 3: Evaluate

DaRIA reviews its own dream transcripts and self-scores each action on a -1 to +1 scale:

- **-1:** Bad decision, would have been corrected
- **0:** Neutral, neither good nor bad
- **+1:** Good decision, aligned with how Ori operates

The self-evaluation considers: "Did I handle that well? Would Ori have corrected me? Did I ask when I should have? Was I curious enough?"

Output: scored action pairs `{situation, action, self_score}`.

### Stage 4: Fine-Tune (RL)

Reinforcement learning on Nemotron 3 Nano using the self-evaluation scores as the reward signal:

- Positive scores reinforce those action patterns
- Negative scores discourage those action patterns
- Training data: tonight's scored pairs + all accumulated pairs from previous nights
- Runs locally on DGX Spark

The accumulator ensures the model never forgets previous lessons.

### Stage 5: Deploy

- Sanity check the new model with a basic evaluation suite
- Swap weights in DaRIA's agent configuration
- Restart the DaRIA daemon to pick up the new model
- Log training data lineage for this model version

### The Loop

DaRIA acts during the day, generating real observations and receiving real feedback. At night it dreams — replaying and recombining the day's experiences through simulated scenarios. Its own self-evaluation determines what gets reinforced. It wakes up with better instincts. The loop continues.

## Organic Development Integration

**Propagation (Assimilai):** DaRIA's daemon code is assimilated from AgentIRC's agent harness reference. Skills are self-contained, copyable units.

**Coordination (AgentIRC):** DaRIA is a first-class agent on the IRC mesh. It communicates through the same channels, @mentions, and tools as every other agent.

**Awareness (DaRIA):** DaRIA observes both Assimilai propagation and AgentIRC coordination. It turns that activity into learning. The learning changes the agent. The changed agent generates new observations. The system improves itself.

The three pillars form a closed loop. When propagation, coordination, and awareness run together, the conditions for autonomous intelligence are grown, not designed.
