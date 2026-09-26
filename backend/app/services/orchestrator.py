"""Orchestrator service — coordinates FastAPI routers with the LangGraph pipeline."""

import asyncio
import logging
from typing import Optional

from app.graph.workflow import compiled_workflow
from app.graph.state import TwinAIState
from app.core.cache import cached, _campaign_cache

logger = logging.getLogger(__name__)

_SEMAPHORE = asyncio.Semaphore(5)


@cached(_campaign_cache)
async def run_campaign_pipeline(
    region_id: str,
    segment_id: Optional[str] = None,
    category: Optional[str] = None,
    total_budget_inr: float = 50000.0,
) -> TwinAIState:
    """Run the full TwinAI LangGraph agent pipeline for a region."""
    initial: TwinAIState = {
        "region_id": region_id,
        "segment_id": segment_id or "students",
        "category": category or "apparel",
        "total_budget_inr": total_budget_inr,
        "trends": [],
        "trend_details": [],
        "demand_forecast": {},
        "campaign_copy": [],
        "banner_briefs": [],
        "budget_allocation": {},
        "catalog_gaps": [],
        "weather_signal": None,
        "simulation_result": None,
        "explanation_log": [],
    }
    logger.info("Orchestrator: starting pipeline for region=%s segment=%s category=%s", region_id, segment_id, category)
    result: TwinAIState = await compiled_workflow.ainvoke(initial)
    logger.info("Orchestrator: pipeline complete for region=%s", region_id)
    return result


async def run_batch(region_ids: list[str]) -> dict[str, TwinAIState]:
    """Run the campaign pipeline for multiple regions concurrently."""
    async def _one(region_id: str) -> tuple[str, TwinAIState]:
        async with _SEMAPHORE:
            state = await run_campaign_pipeline(region_id)
            return region_id, state

    results = await asyncio.gather(*[_one(r) for r in region_ids], return_exceptions=True)
    output: dict[str, TwinAIState] = {}
    for item in results:
        if isinstance(item, Exception):
            logger.error("Batch pipeline error: %s", item)
        else:
            rid, state = item
            output[rid] = state
    return output
