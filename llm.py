"""Shared chat model for gold mining framework agents."""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from pydantic import ValidationError

# Load repo-root .env (LLM_MODEL, provider API keys, TAVILY_API_KEY, etc.)
load_dotenv(Path(__file__).resolve().parent / ".env")

# Current model used by this project's agents.
# Override with LLM_MODEL using init_chat_model's "provider:model" form.
DEFAULT_MODEL = "xai:grok-4.7"

# Documented providers and the API key each integration reads from the environment.
# Gemini uses the Gemini API (`google_genai`), which takes GOOGLE_API_KEY.
_PROVIDER_API_KEYS = {
    "xai": "XAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "google_genai": "GOOGLE_API_KEY",
}

_PROVIDER_PACKAGES = {
    "xai": "langchain-xai",
    "anthropic": "langchain-anthropic",
    "openai": "langchain-openai",
    "google_genai": "langchain-google-genai",
}


def _selected_model() -> str:
    """Return the configured model, falling back to the current xAI default."""
    return os.getenv("LLM_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def _provider_name(model: str) -> str | None:
    """Return the init_chat_model provider prefix, when the id includes one."""
    provider, separator, _name = model.partition(":")
    if separator and provider:
        return provider
    return None


def get_chat_model(
    temperature: float = 0.0,
    model: str | None = None,
) -> BaseChatModel:
    """Return the chat model used by pipeline agents.

    The current model is xAI Grok (`xai:grok-4.7`). Set `LLM_MODEL` to any
    `provider:model` id accepted by `init_chat_model`. Pass `model` to use a
    different id for one call. Documented providers:

    - `xai` — `XAI_API_KEY` (current default)
    - `anthropic` — Claude, `ANTHROPIC_API_KEY`
    - `openai` — `OPENAI_API_KEY`
    - `google_genai` — Gemini, `GOOGLE_API_KEY`

    Args:
        temperature: Sampling temperature. Defaults to 0 for deterministic output.
        model: Optional `provider:model` id. Defaults to `LLM_MODEL` or the
            current xAI model.

    Returns:
        An initialized LangChain chat model.
    """
    model = (model or _selected_model()).strip() or DEFAULT_MODEL
    provider = _provider_name(model)
    api_key_env = _PROVIDER_API_KEYS.get(provider or "")
    if api_key_env and not os.getenv(api_key_env):
        raise RuntimeError(
            f"{model} is not configured. Set {api_key_env} in the repo-root .env file."
        )

    try:
        return init_chat_model(model=model, temperature=temperature)
    except ImportError as exc:
        package = _PROVIDER_PACKAGES.get(provider or "")
        install = f" Install it with `pip install {package}`." if package else ""
        raise RuntimeError(
            f"Could not initialize {model}.{install}".rstrip()
        ) from exc
    except (ValidationError, ValueError) as exc:
        hint = (
            f"Set {api_key_env} in the repo-root .env file."
            if api_key_env
            else (
                "Set LLM_MODEL to a provider:model id such as "
                "xai:grok-4.7, anthropic:claude-sonnet-4-5, openai:gpt-5.5, "
                "or google_genai:gemini-2.5-pro."
            )
        )
        raise RuntimeError(f"Could not initialize {model}. {hint}") from exc
