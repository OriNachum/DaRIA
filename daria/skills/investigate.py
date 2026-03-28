"""Investigate skill — browse the web via Playwright.

Provides headless web browsing for autonomous research. Used by DaRIA
to look up documentation, read GitHub issues, and research topics.
"""
from __future__ import annotations

import json
from urllib.parse import urlparse

MAX_TEXT_LENGTH = 10000


def format_result(
    url: str,
    title: str,
    text: str,
    ok: bool,
    error: str | None = None,
) -> str:
    """Format a page fetch result as JSON."""
    truncated = text[:MAX_TEXT_LENGTH] if len(text) > MAX_TEXT_LENGTH else text
    payload: dict = {"ok": ok, "url": url}
    if ok:
        payload["title"] = title
        payload["text"] = truncated
    else:
        payload["error"] = error or "Unknown error"
    return json.dumps(payload, ensure_ascii=False)


async def fetch_page(url: str, timeout_ms: int = 15000) -> str:
    """Fetch a page with Playwright and return its text content as JSON."""
    if not url:
        return format_result(url=url, title="", text="", ok=False, error="Empty URL")

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return format_result(
            url=url, title="", text="", ok=False,
            error=f"Only http/https URLs are allowed, got: {parsed.scheme or 'none'}",
        )

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        return format_result(
            url=url, title="", text="", ok=False,
            error="Playwright not installed. Run: uv sync --extra investigate && uv run playwright install chromium",
        )

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                page = await browser.new_page()
                await page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
                title = await page.title()
                text = await page.inner_text("body")
                return format_result(url=url, title=title, text=text, ok=True)
            finally:
                await browser.close()
    except Exception as exc:
        return format_result(url=url, title="", text="", ok=False, error=str(exc))
