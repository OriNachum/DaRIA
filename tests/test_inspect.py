"""Tests for the inspect skill (git/gh/filesystem)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from daria.skills.inspect import (
    git_log,
    git_diff,
    read_file,
    grep_files,
    list_prs,
)


class TestReadFile:
    @pytest.mark.asyncio
    async def test_reads_existing_file(self, tmp_path: Path) -> None:
        f = tmp_path / "hello.txt"
        f.write_text("hello world")
        result = await read_file(str(f))
        parsed = json.loads(result)
        assert parsed["ok"] is True
        assert parsed["content"] == "hello world"

    @pytest.mark.asyncio
    async def test_rejects_missing_file(self) -> None:
        result = await read_file("/nonexistent/path/file.txt")
        parsed = json.loads(result)
        assert parsed["ok"] is False

    @pytest.mark.asyncio
    async def test_rejects_directory(self, tmp_path: Path) -> None:
        result = await read_file(str(tmp_path))
        parsed = json.loads(result)
        assert parsed["ok"] is False


class TestGitLog:
    @pytest.mark.asyncio
    async def test_git_log_in_repo(self) -> None:
        result = await git_log(repo_path=".", count=5)
        parsed = json.loads(result)
        assert parsed["ok"] is True
        assert isinstance(parsed["commits"], list)
        assert len(parsed["commits"]) > 0

    @pytest.mark.asyncio
    async def test_git_log_invalid_repo(self, tmp_path: Path) -> None:
        result = await git_log(repo_path=str(tmp_path), count=5)
        parsed = json.loads(result)
        assert parsed["ok"] is False


class TestGrepFiles:
    @pytest.mark.asyncio
    async def test_grep_finds_pattern(self, tmp_path: Path) -> None:
        f = tmp_path / "code.py"
        f.write_text("def hello():\n    return 'world'\n")
        result = await grep_files(pattern="hello", path=str(tmp_path))
        parsed = json.loads(result)
        assert parsed["ok"] is True
        assert len(parsed["matches"]) > 0

    @pytest.mark.asyncio
    async def test_grep_no_matches(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.py"
        f.write_text("pass\n")
        result = await grep_files(pattern="nonexistent_xyz", path=str(tmp_path))
        parsed = json.loads(result)
        assert parsed["ok"] is True
        assert len(parsed["matches"]) == 0
