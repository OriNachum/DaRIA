"""Tests for the investigate skill (Playwright web browsing)."""
from __future__ import annotations

import json

import pytest

from daria.skills.investigate import fetch_page, format_result


class TestFormatResult:
    def test_formats_success(self) -> None:
        result = format_result(
            url="https://example.com",
            title="Example",
            text="Hello world",
            ok=True,
        )
        parsed = json.loads(result)
        assert parsed["ok"] is True
        assert parsed["url"] == "https://example.com"
        assert parsed["title"] == "Example"
        assert "Hello world" in parsed["text"]

    def test_formats_error(self) -> None:
        result = format_result(
            url="https://bad.example",
            title="",
            text="",
            ok=False,
            error="Connection refused",
        )
        parsed = json.loads(result)
        assert parsed["ok"] is False
        assert "Connection refused" in parsed["error"]

    def test_truncates_long_text(self) -> None:
        long_text = "x" * 20000
        result = format_result(url="https://example.com", title="T", text=long_text, ok=True)
        parsed = json.loads(result)
        assert len(parsed["text"]) <= 10000


class TestFetchPage:
    @pytest.mark.asyncio
    async def test_rejects_non_http_url(self) -> None:
        result = await fetch_page("file:///etc/passwd")
        parsed = json.loads(result)
        assert parsed["ok"] is False
        assert "http" in parsed["error"].lower()

    @pytest.mark.asyncio
    async def test_rejects_empty_url(self) -> None:
        result = await fetch_page("")
        parsed = json.loads(result)
        assert parsed["ok"] is False
