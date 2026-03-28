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
