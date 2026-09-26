"""TTL-based response cache for TwinAI's structured agent inputs.

Because TwinAI's agent inputs are structured (region_id, segment_id,
scenario) rather than freeform text, simple TTL-keyed caching captures
nearly all the efficiency gain that embedding-based semantic caching
provides for chat-style systems — with far less complexity.

Cache TTLs:
- Campaign pipeline: 6 hours (trends/demand don't change between requests
  minutes apart; protects the Groq 30 RPM / TPD free-tier budget).
- Simulation results: 30 minutes (scenario outputs are deterministic for the
  same inputs, but scenarios are expected to change more frequently).
"""
import hashlib
import json
from functools import wraps

from cachetools import TTLCache

# ---------------------------------------------------------------------------
# Shared cache instances
# ---------------------------------------------------------------------------
_campaign_cache: TTLCache = TTLCache(maxsize=512, ttl=60 * 60 * 6)   # 6 h
_simulation_cache: TTLCache = TTLCache(maxsize=512, ttl=60 * 30)     # 30 min


def _make_key(*parts: object) -> str:
    """Create a deterministic SHA-256 cache key from arbitrary arguments."""
    raw = json.dumps(parts, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def cached(cache: TTLCache):
    """Decorator for async functions; keys on the function name + all args.

    Usage::

        @cached(_campaign_cache)
        async def run_campaign_pipeline(region_id: str, ...) -> TwinAIState:
            ...
    """
    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            key = _make_key(fn.__name__, args, kwargs)
            if key in cache:
                return cache[key]
            result = await fn(*args, **kwargs)
            cache[key] = result
            return result
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Optional: in-process semantic cache for Seller Q&A (freeform text only)
# ---------------------------------------------------------------------------
try:
    import numpy as np
    from sentence_transformers import SentenceTransformer

    _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    _qa_cache: list[tuple] = []   # (embedding, question, answer)
    _SIM_THRESHOLD = 0.92
    _SEMANTIC_AVAILABLE = True
except ImportError:
    _SEMANTIC_AVAILABLE = False


def semantic_lookup(question: str) -> str | None:
    """Return a cached answer if a semantically similar question was seen.

    Returns None when semantic caching is unavailable or no match is found
    above the similarity threshold.
    """
    if not _SEMANTIC_AVAILABLE or not _qa_cache:
        return None
    import numpy as np
    q_emb = _embedder.encode(question, normalize_embeddings=True)
    sims = [float(np.dot(q_emb, entry[0])) for entry in _qa_cache]
    best = max(range(len(sims)), key=lambda i: sims[i])
    return _qa_cache[best][2] if sims[best] >= _SIM_THRESHOLD else None


def semantic_store(question: str, answer: str) -> None:
    """Store a question/answer pair in the semantic cache."""
    if not _SEMANTIC_AVAILABLE:
        return
    q_emb = _embedder.encode(question, normalize_embeddings=True)
    _qa_cache.append((q_emb, question, answer))
