"""
RepoReel — LLM Service
Wrapper around featherless.ai (OpenAI-compatible) using LangChain.
Provides code-specialized and general-purpose model access with fallback chain.
"""
import asyncio
from typing import Optional

from langchain_openai import ChatOpenAI

from config import (
    FEATHERLESS_API_KEY,
    FEATHERLESS_BASE_URL,
    FEATHERLESS_CODE_MODEL,
    FEATHERLESS_GENERAL_MODEL,
    FEATHERLESS_FALLBACK_MODEL,
)
from utils.json_extractor import extract_json_or_raise


def _create_llm(model: str, temperature: float = 0.7, max_tokens: int = 4096) -> ChatOpenAI:
    """Create a LangChain ChatOpenAI instance pointed at featherless.ai."""
    return ChatOpenAI(
        base_url=FEATHERLESS_BASE_URL,
        api_key=FEATHERLESS_API_KEY,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=90,
    )


# ── Pre-initialized model instances ──
_code_model: Optional[ChatOpenAI] = None
_general_model: Optional[ChatOpenAI] = None
_fallback_model: Optional[ChatOpenAI] = None


def get_code_model() -> ChatOpenAI:
    """Get the code-specialized model (Qwen2.5-Coder-32B)."""
    global _code_model
    if _code_model is None:
        _code_model = _create_llm(FEATHERLESS_CODE_MODEL, temperature=0.3)
    return _code_model


def get_general_model() -> ChatOpenAI:
    """Get the general-purpose model (Qwen2.5-72B)."""
    global _general_model
    if _general_model is None:
        _general_model = _create_llm(FEATHERLESS_GENERAL_MODEL, temperature=0.7)
    return _general_model


def get_fallback_model() -> ChatOpenAI:
    """Get the fallback model (glm-4-9b-chat)."""
    global _fallback_model
    if _fallback_model is None:
        _fallback_model = _create_llm(FEATHERLESS_FALLBACK_MODEL, temperature=0.5)
    return _fallback_model


async def call_llm_with_retry(
    prompt: str,
    model_type: str = "general",
    max_retries: int = 2,
    expect_json: bool = True,
) -> str | dict | list:
    """
    Call an LLM with retry logic and model fallback.

    Args:
        prompt: The full prompt to send
        model_type: "code" for Coder-32B, "general" for 72B-Instruct
        max_retries: Number of retries per model before falling back
        expect_json: If True, parse and return JSON; if False, return raw text

    Returns:
        Parsed JSON (dict/list) if expect_json=True, otherwise raw string.

    Raises:
        RuntimeError: If all models and retries are exhausted
    """
    # Build fallback chain based on model_type
    if model_type == "code":
        models = [get_code_model(), get_general_model(), get_fallback_model()]
        model_names = [FEATHERLESS_CODE_MODEL, FEATHERLESS_GENERAL_MODEL, FEATHERLESS_FALLBACK_MODEL]
    else:
        models = [get_general_model(), get_code_model(), get_fallback_model()]
        model_names = [FEATHERLESS_GENERAL_MODEL, FEATHERLESS_CODE_MODEL, FEATHERLESS_FALLBACK_MODEL]

    last_error = None

    for model, model_name in zip(models, model_names):
        for attempt in range(max_retries + 1):
            try:
                print(f"  [LLM] Calling {model_name} (attempt {attempt + 1})...")

                # Use ainvoke for async
                response = await model.ainvoke(prompt)
                content = response.content

                if not content or not content.strip():
                    raise ValueError("Empty response from LLM")

                if expect_json:
                    # Parse and return JSON
                    result = extract_json_or_raise(content, f"{model_name} response")
                    print(f"  [LLM] ✓ Got valid JSON from {model_name}")
                    return result
                else:
                    print(f"  [LLM] ✓ Got text response from {model_name}")
                    return content.strip()

            except Exception as e:
                last_error = e
                print(f"  [LLM] ✗ {model_name} attempt {attempt + 1} failed: {e}")

                # Brief delay before retry
                if attempt < max_retries:
                    await asyncio.sleep(1)

        # All retries exhausted for this model, try next
        print(f"  [LLM] Falling back from {model_name}...")

    raise RuntimeError(
        f"All LLM models and retries exhausted. Last error: {last_error}"
    )
