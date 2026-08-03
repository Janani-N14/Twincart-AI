"""Seller Intelligence Agent.

Answers free-form seller questions using regional twin data and the
festival calendar as context.  This agent is *not* a LangGraph node —
it is invoked directly from the /api/sellers router because it answers
one-off questions rather than participating in the campaign pipeline.

Semantic caching is applied here (see core/cache.py) because seller
questions are the only genuinely freeform text input in TwinAI.
"""
import json
import logging
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.core.llm import get_llm
from app.core.cache import semantic_lookup, semantic_store
from app.core.exceptions import AgentExecutionError
from app.twins.regional_twin import regional_twin_store
from app.twins.segment_twin import segment_twin_store

logger = logging.getLogger(__name__)

_FESTIVALS_PATH = Path(__file__).resolve().parents[1] / "data" / "festivals.json"
_festivals_str: str | None = None


def _get_festivals_summary() -> str:
    global _festivals_str
    if _festivals_str is None:
        data = json.loads(_FESTIVALS_PATH.read_text(encoding="utf-8"))
        # Compact representation to save tokens
        _festivals_str = "; ".join(
            f"{f['festival']} ({f['approx_date_2026']})" for f in data[:10]
        )
    return _festivals_str


_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are TwinAI's Seller Intelligence agent, an expert in Indian hyperlocal "
        "e-commerce for Bharat/Meesho-style platforms. "
        "Answer the seller's question concisely and accurately using the provided context. "
        'Respond ONLY with a valid JSON object with keys: "answer" (string), '
        '"supporting_data" (object with 1-3 key facts), "confidence" ("low"|"medium"|"high"). '
        "No other text.",
    ),
    (
        "human",
        "question:{question}\n"
        "region_context:{region_ctx}\n"
        "segment_context:{segment_ctx}\n"
        "upcoming_festivals:{festivals}",
    ),
])

_chain = _PROMPT | get_llm(temperature=0.3, fast=False) | JsonOutputParser()


def answer(
    question: str,
    region_id: str | None = None,
    segment_id: str | None = None,
) -> dict:
    """Answer a seller's free-form question.

    Returns a dict with keys: answer, supporting_data, confidence, from_cache.
    """
    # --- Semantic cache lookup ----------------------------------------
    cached = semantic_lookup(question)
    if cached:
        logger.info("[seller_intelligence] cache hit for question: %.60s...", question)
        return {"answer": cached, "supporting_data": {}, "confidence": "high", "from_cache": True}

    # --- Build context ------------------------------------------------
    region_ctx = "No specific region provided."
    if region_id:
        twin = regional_twin_store.get_or_none(region_id)
        if twin:
            region_ctx = (
                f"state:{twin.state}, price_sensitivity:{twin.price_sensitivity}, "
                f"top_categories:{', '.join(twin.top_categories)}, "
                f"festivals:{', '.join(twin.active_festivals)}"
            )

    segment_ctx = "No specific segment provided."
    if segment_id:
        seg = segment_twin_store.get_or_none(segment_id)
        if seg:
            segment_ctx = (
                f"segment:{seg.label}, age:{seg.age_range}, "
                f"preferred:{', '.join(seg.preferred_categories)}, "
                f"price_sensitivity:{seg.price_sensitivity}"
            )

    try:
        result: dict = _chain.invoke({
            "question": question,
            "region_ctx": region_ctx,
            "segment_ctx": segment_ctx,
            "festivals": _get_festivals_summary(),
        })
        if not isinstance(result, dict):
            result = {"answer": str(result), "supporting_data": {}, "confidence": "medium"}

        answer_text = result.get("answer", "")
        if answer_text:
            semantic_store(question, answer_text)

        result["from_cache"] = False
        logger.info("[seller_intelligence] answered: %.60s...", question)
        return result
    except Exception as exc:
        logger.error("[seller_intelligence] failed: %s", exc)
        raise AgentExecutionError("seller_intelligence", str(exc)) from exc
