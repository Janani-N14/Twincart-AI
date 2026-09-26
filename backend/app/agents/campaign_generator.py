"""Campaign Generator Agent.

Produces 3-5 ready-to-use hyperlocal campaign copy lines tailored to the
region's language, festival context, top-demand categories, and customer
segment (if provided).  Uses the large model — generative creative task.
"""
import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.core.llm import get_llm
from app.core.exceptions import AgentExecutionError
from app.graph.state import TwinAIState
from app.twins.regional_twin import regional_twin_store
from app.twins.segment_twin import segment_twin_store

logger = logging.getLogger(__name__)

_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are TwinAI's Hyperlocal Campaign Generator for Indian e-commerce. "
        "Write 3-5 short, punchy campaign copy lines (each ≤ 15 words) in English "
        "that feel local and relevant to the region's language and culture. "
        "Incorporate the top trending products, upcoming festivals, and customer segment. "
        "Respond ONLY with a valid JSON array of strings. No other text.",
    ),
    (
        "human",
        "region_id:{region_id}\n"
        "state:{state}\n"
        "languages:{languages}\n"
        "top_demand_categories:{top_demand}\n"
        "trending_products:{trends}\n"
        "weather_festival_signal:{weather}\n"
        "customer_segment:{segment}\n"
        "catalog_gaps:{gaps}",
    ),
])

_chain = _PROMPT | get_llm(temperature=0.7, fast=False) | JsonOutputParser()


def run(state: TwinAIState) -> dict:
    """LangGraph node: generate hyperlocal campaign copy."""
    region_id = state["region_id"]
    try:
        twin = regional_twin_store.get(region_id)

        # Resolve optional segment label
        segment_label = "general shoppers"
        if state.get("segment_id"):
            seg = segment_twin_store.get_or_none(state["segment_id"])
            if seg:
                segment_label = seg.label

        # Pick top 3 demand categories
        forecast = state.get("demand_forecast") or {}
        top_demand = sorted(forecast, key=forecast.get, reverse=True)[:3]  # type: ignore[arg-type]

        copy_lines: list[str] = _chain.invoke({
            "region_id": region_id,
            "state": twin.state,
            "languages": ", ".join(twin.languages),
            "top_demand": ", ".join(top_demand) or ", ".join(twin.top_categories[:3]),
            "trends": ", ".join(state.get("trends") or []),
            "weather": state.get("weather_signal") or "no special signal",
            "segment": segment_label,
            "gaps": ", ".join(state.get("catalog_gaps") or []),
        })
        if not isinstance(copy_lines, list):
            copy_lines = [str(copy_lines)]
        logger.info("[campaign_generator] %s → %d lines", region_id, len(copy_lines))
        return {
            "campaign_copy": copy_lines,
            "explanation_log": [
                f"Campaign Generator ({region_id}): generated {len(copy_lines)} campaign lines "
                f"targeting {segment_label}."
            ],
        }
    except Exception as exc:
        logger.error("[campaign_generator] failed for %s: %s", region_id, exc)
        raise AgentExecutionError("campaign_generator", str(exc)) from exc
