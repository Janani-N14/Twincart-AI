"""Demand Forecasting Agent.

Fan-in node: runs after trend_detection, weather_festival, and catalog_gap
have all completed.  Produces a demand_forecast dict mapping each of the
region's top categories to a predicted demand index (0–100).
Uses the large model — this is a reasoning-heavy estimation task.
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
        "You are TwinAI's Demand Forecasting agent for Indian hyperlocal e-commerce. "
        "Given the regional context, trending products, weather/festival signal, and "
        "catalog gaps, forecast demand for the next 30 days. "
        "Respond ONLY with a valid JSON object mapping category names to demand index "
        "values (0-100, where 100 = peak seasonal demand), e.g. "
        '{{"apparel": 82, "kitchenware": 60}}. No other text.',
    ),
    (
        "human",
        "region_id:{region_id}\n"
        "state:{state}\n"
        "price_sensitivity:{sensitivity}\n"
        "top_categories:{categories}\n"
        "trending_products:{trends}\n"
        "weather_festival_signal:{weather}\n"
        "catalog_gaps:{gaps}",
    ),
])

_chain = _PROMPT | get_llm(temperature=0.2, fast=False) | JsonOutputParser()


def run(state: TwinAIState) -> dict:
    """LangGraph node: generate demand forecast."""
    region_id = state["region_id"]
    try:
        twin = regional_twin_store.get(region_id)
        forecast: dict[str, float] = _chain.invoke({
            "region_id": region_id,
            "state": twin.state,
            "sensitivity": twin.price_sensitivity,
            "categories": ", ".join(twin.top_categories),
            "trends": ", ".join(state.get("trends") or []),
            "weather": state.get("weather_signal") or "unavailable",
            "gaps": ", ".join(state.get("catalog_gaps") or []),
        })
        if not isinstance(forecast, dict):
            forecast = {}
        logger.info("[demand_forecasting] %s → %s", region_id, forecast)
        summary = ", ".join(f"{k}:{v}" for k, v in list(forecast.items())[:3])
        return {
            "demand_forecast": forecast,
            "explanation_log": [f"Demand Forecast ({region_id}): {summary}..."],
        }
    except Exception as exc:
        logger.error("[demand_forecasting] failed for %s: %s", region_id, exc)
        raise AgentExecutionError("demand_forecasting", str(exc)) from exc
