"""Tests for DaRIA coded logging."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from daria.daemon.logger import DaRIALogger, LogEntry


class TestLogEntry:
    def test_trigger_entry(self) -> None:
        entry = LogEntry.trigger(
            source="mention",
            sender="ori",
            channel="#general",
            text="should we use Redis?",
        )
        assert entry.kind == "trigger"
        assert entry.data["source"] == "mention"
        assert entry.data["sender"] == "ori"
        assert isinstance(entry.timestamp, str)

    def test_tool_call_entry(self) -> None:
        entry = LogEntry.tool_call(
            skill="investigate",
            args={"url": "https://example.com"},
            result={"ok": True, "summary": "Example page"},
        )
        assert entry.kind == "tool_call"
        assert entry.data["skill"] == "investigate"

    def test_response_entry(self) -> None:
        entry = LogEntry.response(
            text="I recommend SQLite",
            destinations=["#general", "#daria-journal"],
        )
        assert entry.kind == "response"
        assert entry.data["destinations"] == ["#general", "#daria-journal"]

    def test_to_json_is_valid_jsonl(self) -> None:
        entry = LogEntry.trigger(source="patrol", sender="daria", channel=None, text="")
        line = entry.to_json()
        parsed = json.loads(line)
        assert parsed["kind"] == "trigger"
        assert "timestamp" in parsed


class TestDaRIALogger:
    def test_log_creates_daily_file(self, tmp_path: Path) -> None:
        logger = DaRIALogger(log_dir=tmp_path)
        entry = LogEntry.trigger(source="test", sender="test", channel=None, text="hello")
        logger.log(entry)

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = tmp_path / f"daria-{today}.jsonl"
        assert log_file.exists()

        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 1
        parsed = json.loads(lines[0])
        assert parsed["kind"] == "trigger"

    def test_log_appends_multiple_entries(self, tmp_path: Path) -> None:
        logger = DaRIALogger(log_dir=tmp_path)
        logger.log(LogEntry.trigger(source="a", sender="x", channel=None, text=""))
        logger.log(LogEntry.response(text="reply", destinations=["#general"]))

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = tmp_path / f"daria-{today}.jsonl"
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 2

    def test_log_dir_created_if_missing(self, tmp_path: Path) -> None:
        log_dir = tmp_path / "subdir" / "logs"
        logger = DaRIALogger(log_dir=log_dir)
        logger.log(LogEntry.trigger(source="test", sender="test", channel=None, text=""))
        assert log_dir.exists()
