"""Smoke tests — verify all modules import and basic wiring works."""
from __future__ import annotations

import json

import pytest


class TestImports:
    def test_import_logger(self) -> None:
        from daria.daemon.logger import DaRIALogger, LogEntry
        assert DaRIALogger is not None

    def test_import_investigate(self) -> None:
        from daria.skills.investigate import fetch_page, format_result
        assert fetch_page is not None

    def test_import_inspect(self) -> None:
        from daria.skills.inspect import read_file, git_log, grep_files
        assert read_file is not None

    def test_import_ipc(self) -> None:
        from daria.daemon.ipc import make_response, make_request
        assert make_response is not None

    def test_version(self) -> None:
        from daria import __version__
        assert __version__ == "0.1.0"


class TestLoggerIntegration:
    def test_full_cycle(self, tmp_log_dir) -> None:
        from daria.daemon.logger import DaRIALogger, LogEntry

        logger = DaRIALogger(log_dir=tmp_log_dir)

        # Log all three entry types
        logger.log(LogEntry.trigger(source="mention", sender="ori", channel="#general", text="hello"))
        logger.log(LogEntry.tool_call(skill="investigate", args={"url": "https://example.com"}, result={"ok": True}))
        logger.log(LogEntry.response(text="Done", destinations=["#general"]))

        # Verify JSONL output
        log_files = list(tmp_log_dir.glob("daria-*.jsonl"))
        assert len(log_files) == 1

        lines = log_files[0].read_text().strip().split("\n")
        assert len(lines) == 3

        kinds = [json.loads(line)["kind"] for line in lines]
        assert kinds == ["trigger", "tool_call", "response"]
