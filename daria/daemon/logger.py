"""JSONL coded logging for DaRIA.

Append-only daily log files that capture triggers, tool calls, and model
outputs.  These logs are the primary input for the phase 2 fine-tuning
pipeline — treat the schema as a contract once established.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class LogEntry:
    kind: str
    data: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @classmethod
    def trigger(
        cls,
        source: str,
        sender: str,
        channel: str | None,
        text: str,
    ) -> LogEntry:
        return cls(
            kind="trigger",
            data={"source": source, "sender": sender, "channel": channel, "text": text},
        )

    @classmethod
    def tool_call(
        cls,
        skill: str,
        args: dict[str, Any],
        result: dict[str, Any],
    ) -> LogEntry:
        return cls(
            kind="tool_call",
            data={"skill": skill, "args": args, "result": result},
        )

    @classmethod
    def response(
        cls,
        text: str,
        destinations: list[str],
    ) -> LogEntry:
        return cls(
            kind="response",
            data={"text": text, "destinations": destinations},
        )

    def to_json(self) -> str:
        return json.dumps(
            {"kind": self.kind, "data": self.data, "timestamp": self.timestamp},
            ensure_ascii=False,
        )


class DaRIALogger:
    """Append-only JSONL logger, one file per UTC day."""

    def __init__(self, log_dir: str | Path) -> None:
        self._log_dir = Path(log_dir)

    def _log_path(self) -> Path:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self._log_dir / f"daria-{today}.jsonl"

    def log(self, entry: LogEntry) -> None:
        self._log_dir.mkdir(parents=True, exist_ok=True)
        with open(self._log_path(), "a", encoding="utf-8") as f:
            f.write(entry.to_json() + "\n")
