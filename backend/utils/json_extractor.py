"""
AutoMotion — Robust JSON Extractor
Handles LLM responses that wrap JSON in markdown code blocks or include extra text.
"""
import json
import re
from typing import Any, Optional


def extract_json(text: str) -> Optional[Any]:
    """
    Extract JSON from an LLM response that may contain markdown formatting.

    Strategy (tried in order):
    1. Direct JSON parse
    2. Extract from ```json code block
    3. Extract from ``` code block (no language tag)
    4. Find first { and last } and parse the substring
    5. Find first [ and last ] and parse the substring (for arrays)

    Returns the parsed JSON object, or None if all strategies fail.
    """
    if not text or not text.strip():
        return None

    text = text.strip()

    # Strategy 1: Direct parse
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        pass

    # Strategy 2: Extract from ```json ... ``` block
    json_block = re.search(r"```json\s*\n?(.*?)```", text, re.DOTALL)
    if json_block:
        try:
            return json.loads(json_block.group(1).strip())
        except (json.JSONDecodeError, ValueError):
            pass

    # Strategy 3: Extract from ``` ... ``` block (no language tag)
    code_block = re.search(r"```\s*\n?(.*?)```", text, re.DOTALL)
    if code_block:
        try:
            return json.loads(code_block.group(1).strip())
        except (json.JSONDecodeError, ValueError):
            pass

    # Strategy 4: Find first { and last } (for objects)
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        try:
            return json.loads(text[first_brace:last_brace + 1])
        except (json.JSONDecodeError, ValueError):
            pass

    # Strategy 5: Find first [ and last ] (for arrays)
    first_bracket = text.find("[")
    last_bracket = text.rfind("]")
    if first_bracket != -1 and last_bracket != -1 and last_bracket > first_bracket:
        try:
            return json.loads(text[first_bracket:last_bracket + 1])
        except (json.JSONDecodeError, ValueError):
            pass

    return None


def extract_json_or_raise(text: str, context: str = "LLM response") -> Any:
    """
    Extract JSON from text, raising ValueError if extraction fails.

    Args:
        text: The raw LLM response text
        context: Description of what this JSON represents (for error messages)

    Returns:
        Parsed JSON object

    Raises:
        ValueError: If no valid JSON can be extracted
    """
    result = extract_json(text)
    if result is None:
        # Truncate text for error message
        preview = text[:200] + "..." if len(text) > 200 else text
        raise ValueError(
            f"Failed to extract JSON from {context}. "
            f"Response preview: {preview}"
        )
    return result
