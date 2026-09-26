"""Trend Detection Agent.

Identifies 3-5 emerging product trends for a given region using the
regional twin's festival calendar, top categories, and temperature signal.
Uses the *fast* (small) model — this is a classification/extraction task.
"""
import json
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
        "You are TwinAI's Trend Detection agent for Indian hyperlocal e-commerce. "
        "Identify 3-5 emerging product trends for the given region. "
        "Base your analysis on the region's top categories, upcoming festivals, "
        "and average temperature. "
        "Respond ONLY with a valid JSON array of short trend strings, e.g. "
        '["cotton kurtas", "water bottles", "LED diyas"]. No other text.',
    ),
    (
        "human",
        "region_id:{region_id}\n"
        "state:{state}\n"
        "top_categories:{categories}\n"
        "active_festivals:{festivals}\n"
        "avg_temp_c:{temp}",
    ),
])

_chain = _PROMPT | get_llm(temperature=0.2, fast=True) | JsonOutputParser()


def run(state: TwinAIState) -> dict:
    """LangGraph node: detect trending products for state['region_id']."""
    region_id = state["region_id"]
    try:
        twin = regional_twin_store.get(region_id)
        trends: list[str] = _chain.invoke({
            "region_id": region_id,
            "state": twin.state,
            "categories": ", ".join(twin.top_categories),
            "festivals": ", ".join(twin.active_festivals),
            "temp": twin.avg_temperature_c,
        })
        if not isinstance(trends, list):
            trends = list(trends)
        logger.info("[trend_detection] %s → %s", region_id, trends)
        return {
            "trends": trends,
            "explanation_log": [f"Trend Detection ({region_id}): {', '.join(trends)}"],
        }
    except Exception as exc:
        logger.error("[trend_detection] failed for %s: %s", region_id, exc)
        raise AgentExecutionError("trend_detection", str(exc)) from exc
