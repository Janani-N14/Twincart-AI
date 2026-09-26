"""Catalog Gap Detection Agent.

Compares the region's detected demand trends against its known top
categories to surface product gaps — categories that are trending but
under-represented in the current catalog.  Uses the fast model.
"""
import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.core.llm import get_llm
from app.core.exceptions import AgentExecutionError
from app.graph.state import TwinAIState
from app.twins.regional_twin import regional_twin_store

logger = logging.getLogger(__name__)

_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are TwinAI's Catalog Gap Detection agent. "
        "Given a region's trending products and its existing top catalog categories, "
        "identify 2-4 product sub-categories that are trending but currently under-served. "
        "Respond ONLY with a valid JSON array of short gap strings, e.g. "
        '["ethnic footwear", "stainless steel bottles"]. No other text.',
    ),
    (
        "human",
        "region_id:{region_id}\n"
        "trending_products:{trends}\n"
        "existing_catalog_categories:{categories}\n"
        "weather_signal:{weather}",
    ),
])

_chain = _PROMPT | get_llm(temperature=0.1, fast=True) | JsonOutputParser()


def run(state: TwinAIState) -> dict:
    """LangGraph node: detect catalog gaps for state['region_id']."""
    region_id = state["region_id"]
    twin = regional_twin_store.get(region_id)
    try:
        gaps: list[str] = _chain.invoke({
            "region_id": region_id,
            "trends": ", ".join(state.get("trends") or []),
            "categories": ", ".join(twin.top_categories),
            "weather": state.get("weather_signal") or "unavailable",
        })
        if not isinstance(gaps, list):
            gaps = list(gaps)
    except Exception as exc:
        logger.warning("[catalog_gap] Groq/LLM failed for %s (%s), using domain twin fallback", region_id, exc)
        gaps = [
            f"Affordable {twin.top_categories[0]} value packs",
            f"Regional artisanal {twin.top_categories[1]}",
            "Local festive gift sets",
        ]

    logger.info("[catalog_gap] %s → %s", region_id, gaps)
    return {
        "catalog_gaps": gaps,
        "explanation_log": [f"Catalog Gaps ({region_id}): {', '.join(gaps)}"],
    }
