---
layout: default
title: Pipeline
---

<div class="post-content" markdown="1">

# Pipeline

> **Phase 2 — documented for future implementation.**
>
> The coded logging layer (Phase 1) produces the input this pipeline needs. Build Phase 1 first, accumulate real logs, then build the pipeline.

## Overview

A nightly self-improvement loop. DaRIA acts during the day, generating real observations and receiving real feedback. At night it *dreams* — replaying and recombining the day's experiences through simulated scenarios, evaluating its own performance, and fine-tuning its model on what it learns. It wakes up with better instincts.

The pipeline runs after midnight, processes the day's [JSONL logs](../logging/), simulates new experiences, and fine-tunes Nemotron 3 Nano using DaRIA's own self-evaluation as the reward signal.

## Hardware

| Machine | Model | Role |
|---------|-------|------|
| Jetson Thor (128GB Blackwell) | Nemotron 3 Super | Dungeon master / simulator |
| DGX Spark (128GB Blackwell) | Nemotron 3 Nano | DaRIA dreamer + fine-tune target |

## Stages

### Stage 1: Digest

*Nano reads the day's logs and extracts what matters.*

Nemotron 3 Nano with extended thinking reads the day's JSONL logs and IRC history. It identifies decisions, corrections, and patterns — what Ori corrected, what worked, what was novel. Produces a structured digest that seeds the dream scenarios.

**Input:** `logs/daria-YYYY-MM-DD.jsonl`
**Output:** Structured digest — situations, decisions, corrections, patterns

---

### Stage 2: Dream

*Super presents situations. DaRIA responds as if each is real.*

Nemotron 3 Super (on Jetson Thor) acts as dungeon master. It presents situations drawn from the digest: replays of situations Ori corrected, novel variations of real events, edge cases the day didn't encounter.

DaRIA (Nano on DGX Spark) is the dreamer. It responds as if each situation is real — it does not know it is in a simulation. Super plays all other roles (Ori, other agents, the world) and reacts to DaRIA's choices. The result is multi-turn transcripts.

**Training pair format:** Super's situation prompt = question, DaRIA's action = answer.

---

### Stage 3: Evaluate

*DaRIA reviews its own transcripts and self-scores each action.*

DaRIA reviews the dream transcripts and scores each action on a -1 to +1 scale:

| Score | Meaning |
|-------|---------|
| `-1` | Bad decision — would have been corrected |
| `0` | Neutral — neither good nor bad |
| `+1` | Good decision — aligned with how Ori operates |

Evaluation criteria: "Did I handle that well? Would Ori have corrected me? Did I ask when I should have? Was I curious enough?"

**Output:** Scored pairs `{situation, action, self_score}`

---

### Stage 4: Fine-Tune (RL)

*Self-evaluation scores become the reward signal.*

Reinforcement learning on Nemotron 3 Nano using the scored pairs:

- Positive scores reinforce those action patterns
- Negative scores discourage those action patterns
- Training data: tonight's scored pairs **plus all accumulated pairs from previous nights**

The accumulator ensures the model never forgets previous lessons. Runs locally on DGX Spark.

---

### Stage 5: Deploy

*Validate, swap weights, restart.*

1. Sanity check the new model with a basic evaluation suite
2. Swap weights in DaRIA's agent configuration
3. Restart the DaRIA daemon to pick up the new model
4. Log training data lineage for this model version

---

## The Loop

```
Day:   DaRIA acts → real feedback from Ori and agents → logs accumulate
Night: Digest → Dream → Evaluate → Fine-Tune → Deploy
Dawn:  DaRIA wakes up with better instincts → repeat
```

Each cycle tightens DaRIA's judgment. The learning compounds.

</div>
