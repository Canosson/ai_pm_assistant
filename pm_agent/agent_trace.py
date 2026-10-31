"""Trace lines for a live agent run: which model answered, which tools it called, what it cost.

Dispatches on the SDK message class *name*, so it needs no SDK import and is testable with stand-ins.
"""

from __future__ import annotations

import json
from typing import Any

MAX_INPUT_CHARS = 100


def _short(value: Any) -> str:
    text = json.dumps(value, default=str, ensure_ascii=False)
    return text if len(text) <= MAX_INPUT_CHARS else text[: MAX_INPUT_CHARS - 3] + "..."


def _result_size(content: Any) -> int:
    """Characters of text in a tool result (string, or a list of {"type": "text", "text": ...} blocks)."""
    if isinstance(content, list):
        return sum(len(item.get("text", "")) if isinstance(item, dict) else len(str(item)) for item in content)
    return len(str(content or ""))


def trace_lines(message: Any) -> list[str]:
    kind = type(message).__name__
    if kind == "SystemMessage" and getattr(message, "subtype", "") == "init":
        data = getattr(message, "data", None) or {}
        return [f"[init] model={data.get('model')} tools={data.get('tools')}"]
    if kind == "AssistantMessage":
        calls = [b for b in getattr(message, "content", []) if type(b).__name__ == "ToolUseBlock"]
        usage = getattr(message, "usage", None)
        if not calls and not usage:
            return []
        lines = [f"[assistant] model={getattr(message, 'model', None)}"]
        if usage:
            lines.append(
                f"[turn usage] in={usage.get('input_tokens')} cache_write={usage.get('cache_creation_input_tokens')} "
                f"cache_read={usage.get('cache_read_input_tokens')} out={usage.get('output_tokens')}")
        lines += [f"[tool] {call.name} {_short(call.input)}" for call in calls]
        return lines
    if kind == "UserMessage":
        content = getattr(message, "content", None)
        blocks = content if isinstance(content, list) else []
        return [
            f"[tool-result] {str(getattr(b, 'tool_use_id', ''))[-8:]} {_result_size(getattr(b, 'content', ''))} chars"
            for b in blocks if type(b).__name__ == "ToolResultBlock"
        ]
    if kind == "ResultMessage":
        cost = getattr(message, "total_cost_usd", None)
        head = f"[result] {getattr(message, 'num_turns', '?')} turns"
        if cost is not None:
            head += f", ${cost:.4f}"
        if getattr(message, "is_error", False):
            head += ", ERROR"
        lines = [head]
        if getattr(message, "usage", None):
            lines.append(f"[usage] {_short(message.usage)}")
        if getattr(message, "model_usage", None):
            lines.append(f"[usage by model] {json.dumps(message.model_usage, default=str)}")
        return lines
    return []
