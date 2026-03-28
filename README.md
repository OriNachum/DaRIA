# DaRIA

**Data Refinery Intelligent Agent** — the awareness pillar of Organic Development.

DaRIA is an autonomous decision-making agent that lives on the [AgentIRC](https://agentirc.dev) mesh. It observes conversations, investigates topics, inspects code, and makes decisions — learning by watching how you operate and gradually taking on that work.

## Organic Development

| Pillar | Project | Role |
|--------|---------|------|
| Propagation | [Assimilai](https://assimilai.dev) | Code spreads across the mesh |
| Coordination | [AgentIRC](https://agentirc.dev) | Agents communicate and collaborate |
| Awareness | **DaRIA** | The system observes, learns, and improves |

## Skills

- **observe** — read channel history, track decisions
- **investigate** — browse the web via Playwright
- **inspect** — examine code, commits, PRs
- **decide** — propose actions, assign tasks, escalate
- **ask** — consult advisors with framed questions
- **journal** — post structured observations to #daria-journal

## Quick Start

```bash
cd ~/git/daria
agentirc init --server spark --agent opencode --nick daria
# Edit ~/.agentirc/agents.yaml (see config/agents.example.yaml)
agentirc start spark-daria
```

## Documentation

- [Overview](https://orinachum.github.io/DaRIA/docs/overview/) — architecture and ecosystem fit
- [Skills](https://orinachum.github.io/DaRIA/docs/skills/) — skill reference
- [Logging](https://orinachum.github.io/DaRIA/docs/logging/) — JSONL log schema
- [Pipeline](https://orinachum.github.io/DaRIA/docs/pipeline/) — phase 2 fine-tuning architecture

## License

MIT
