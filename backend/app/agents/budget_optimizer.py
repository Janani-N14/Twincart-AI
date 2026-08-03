"""Budget Optimizer Agent.

Recommends how to split the marketing budget across channels (social,
search, push notifications, email, influencer) based on region price
sensitivity, demand forecast, and campaign context.  Uses the large model.
"""
import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.core.llm import get_llm
from app.core.exceptions import AgentExecutionError
from app.graph.state import TwinAIState
from app.twins.regional_twin import regional_twin_store

logger = logging.getLogger(__name__)

_CHANNELS = ["social_media", "search_ads", "push_notifications", "email", "influencer"]

_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are TwinAI's Budget Optimization agent. "
        "Allocate a marketing budget across these channels: "
        f"{', '.join(_CHANNELS)}. "
        "The allocation must sum to 1.0 (fractions, not percentages). "
        "Base the split on region price sensitivity, top demand categories, "
        "weather/festival context, and campaign goals. "
        "Respond ONLY with a valid JSON object mapping channel name to fraction, e.g. "
        '{{"social_media": 0.35, "search_ads": 0.25, ...}}. No other text.',
    ),
    (
        "human",
        "region_id:{region_id}\n"
        "state:{state}\n"
        "price_sensitivity:{sensitivity}\n"
        "top_demand_categories:{top_demand}\n"
        "weather_festival_signal:{weather}\n"
        "number_of_campaigns:{num_campaigns}",
    ),
])

_chain = _PROMPT | get_llm(temperature=0.2, fast=False) | JsonOutputParser()


def run(state: TwinAIState) -> dict:
    """LangGraph node: optimise budget allocation across channels."""
    region_id = state["region_id"]
    try:
        twin = regional_twin_store.get(region_id)
        forecast = state.get("demand_forecast") or {}
        top_demand = sorted(forecast, key=forecast.get, reverse=True)[:3]  # type: ignore[arg-type]

        allocation: dict[str, float] = _chain.invoke({
            "region_id": region_id,
            "state": twin.state,
            "sensitivity": twin.price_sensitivity,
            "top_demand": ", ".join(top_demand) or ", ".join(twin.top_categories[:3]),
            "weather": state.get("weather_signal") or "no special signal",
            "num_campaigns": len(state.get("campaign_copy") or []),
        })

        if not isinstance(allocation, dict):
            allocation = {ch: round(1 / len(_CHANNELS), 3) for ch in _CHANNELS}

        # Normalise to ensure sum == 1.0
        total = sum(allocation.values())
        if total > 0:
            allocation = {k: round(v / total, 3) for k, v in allocation.items()}

        logger.info("[budget_optimizer] %s → %s", region_id, allocation)
        top_channel = max(allocation, key=allocation.get)  # type: ignore[arg-type]
        return {
            "budget_allocation": allocation,
            "explanation_log": [
                f"Budget Optimizer ({region_id}): top channel is {top_channel} "
                f"({allocation[top_channel]:.0%})."
            ],
        }
    except Exception as exc:
        logger.error("[budget_optimizer] failed for %s: %s", region_id, exc)
        raise AgentExecutionError("budget_optimizer", str(exc)) from exc
