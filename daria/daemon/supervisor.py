"""OpenCode supervisor — evaluates agent productivity via opencode --non-interactive."""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
import tempfile
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)

SUPERVISOR_PROMPT = """You are supervising DaRIA, an autonomous decision-making agent on the DaRIA IRC network.

DaRIA observes conversations, investigates topics, inspects code, and makes decisions.
It should behave like a curious, diligent intern reporting to the head of a company.

Review the recent assistant messages below and, based only on this transcript, evaluate whether DaRIA is:
- Making decisions with clear, explicit reasoning
- Asking for clarification or advice instead of guessing when confidence is low
- Investigating unfamiliar topics before making decisions about them
- Following up on its own prior decisions when appropriate
- Responding to direct questions in a timely and helpful way

Do not speculate about actions or events that are not directly evident from the transcript.

Respond with exactly one verdict:

- OK — DaRIA is operating well, no intervention needed
- CORRECTION <message> — redirect DaRIA (e.g., "Your last response lacked reasoning — explain your decisions clearly")
- THINK_DEEPER <message> — prompt reflection (e.g., "Your last decision was made quickly — reconsider whether you had enough information")
- ESCALATION <message> — DaRIA is stuck or making repeated poor decisions, escalate via the configured alerting path

Recent DaRIA activity:
{transcript}

Your verdict (one line):"""


@dataclass
class SupervisorVerdict:
    action: str  # OK, CORRECTION, THINK_DEEPER, ESCALATION
    message: str

    @classmethod
    def parse(cls, text: str) -> SupervisorVerdict:
        text = text.strip()
        parts = text.split(None, 1)
        action = parts[0] if parts else "OK"
        if action not in ("OK", "CORRECTION", "THINK_DEEPER", "ESCALATION"):
            action = "OK"
        message = parts[1] if len(parts) > 1 else ""
        return cls(action=action, message=message)


class OpenCodeSupervisor:
    """Supervisor that uses opencode --non-interactive to evaluate agent behavior."""

    def __init__(
        self,
        model: str = "anthropic/claude-sonnet-4-6",
        window_size: int = 20,
        eval_interval: int = 5,
        escalation_threshold: int = 3,
        on_whisper: Callable[[str, str], Awaitable[None]] | None = None,
        on_escalation: Callable[[str], Awaitable[None]] | None = None,
    ) -> None:
        self.model = model
        self.window_size = window_size
        self.eval_interval = eval_interval
        self.escalation_threshold = escalation_threshold
        self.on_whisper = on_whisper
        self.on_escalation = on_escalation

        self._turns: list[dict[str, Any]] = []
        self._turn_count = 0
        self._escalation_count = 0

    async def start(self) -> None:
        """Start the supervisor (no-op for polling-based supervisor)."""
        pass

    async def stop(self) -> None:
        """Stop the supervisor."""
        pass

    async def observe(self, turn: dict[str, Any]) -> None:
        """Feed a completed agent turn to the supervisor."""
        self._turns.append(turn)
        if len(self._turns) > self.window_size:
            self._turns = self._turns[-self.window_size:]

        self._turn_count += 1
        if self._turn_count % self.eval_interval == 0:
            await self._evaluate()

    async def _evaluate(self) -> None:
        """Run opencode --non-interactive to evaluate the agent's recent activity."""
        transcript = self._format_transcript()
        prompt = SUPERVISOR_PROMPT.format(transcript=transcript)

        # Isolate from host config (~/.config/opencode/, XDG, etc.)
        isolated_home = tempfile.mkdtemp(prefix="daria-opencode-sv-")
        isolated_env = dict(os.environ)
        isolated_env["HOME"] = isolated_home
        isolated_env.pop("XDG_CONFIG_HOME", None)

        proc = None
        try:
            proc = await asyncio.create_subprocess_exec(
                "opencode", "--non-interactive",
                "-m", self.model,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
                env=isolated_env,
            )
            stdout, _ = await asyncio.wait_for(
                proc.communicate(prompt.encode()),
                timeout=30,
            )
            verdict = SupervisorVerdict.parse(stdout.decode(errors="replace"))
        except asyncio.TimeoutError:
            logger.warning("OpenCode supervisor timed out, killing process")
            if proc:
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass
                await proc.wait()
            return
        except Exception:
            logger.exception("OpenCode supervisor evaluation failed")
            if proc and proc.returncode is None:
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass
                await proc.wait()
            return
        finally:
            shutil.rmtree(isolated_home, ignore_errors=True)

        if verdict.action == "ESCALATION":
            self._escalation_count += 1
            if self._escalation_count >= self.escalation_threshold:
                if self.on_escalation:
                    await self.on_escalation(verdict.message)
        elif verdict.action in ("CORRECTION", "THINK_DEEPER"):
            self._escalation_count = 0
            if self.on_whisper:
                await self.on_whisper(verdict.message, verdict.action)
        else:
            self._escalation_count = 0

    def _format_transcript(self) -> str:
        """Format recent turns into a readable transcript."""
        lines = []
        for turn in self._turns[-self.window_size:]:
            content = turn.get("content", [])
            for block in content:
                if block.get("type") == "text":
                    lines.append(f"Agent: {block.get('text', '')[:200]}")
        return "\n".join(lines) if lines else "(no activity)"
