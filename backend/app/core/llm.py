from functools import lru_cache

from langchain_groq import ChatGroq
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from app.config import get_settings


@lru_cache
def get_llm(temperature: float = 0.3, fast: bool = False) -> ChatGroq:
    """Return a cached ChatGroq client.

    Args:
        temperature: Sampling temperature (0 = deterministic, 1 = creative).
        fast: True uses the smaller/faster model for lightweight nodes
              (trend tagging, classification); False uses the larger model
              for reasoning-heavy nodes (campaign copy, explanations).

    Returns:
        A cached ChatGroq instance.
    """
    settings = get_settings()
    model = settings.groq_model_fast if fast else settings.groq_model
    return ChatGroq(
        api_key=settings.groq_api_key,
        model=model,
        temperature=temperature,
    )


def invoke_with_backoff(chain, payload: dict):
    """Invoke a LangChain chain with exponential backoff on Groq rate-limit errors.

    Handles HTTP 429 responses gracefully so transient rate limits don't
    fail the whole pipeline.
    """
    try:
        from groq import RateLimitError
        exception_type = RateLimitError
    except ImportError:
        exception_type = Exception  # fallback if groq package not installed yet

    @retry(
        retry=retry_if_exception_type(exception_type),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(4),
    )
    def _invoke():
        return chain.invoke(payload)

    return _invoke()
