"""Orchestrator service — glue between FastAPI routers and the LangGraph pipeline.

The TTL cache from core/cache.py is applied here so repeated requests
for the same region within a 6-hour window don't trigger extra Groq calls.
"""
import asyncio
import logging

from app.graph.workflow import compiled_workflow
from app.graph.state import TwinAIState
from app.core.cache import cached, _campaign_cache

logger = logging.getLogger(__name__)

# Semaphore caps concurrent LangGraph runs to stay comfortably under
# Groq's 30 RPM free-tier limit when batch-processing multiple regions.
_SEMAPHORE = asyncio.Semaphore(5)


@cached(_campaign_cache)
async def run_campaign_pipeline(
    region_id: str,
    segment_id: str | None = None,
) -> TwinAIState:
    """Run the full TwinAI agent pipeline for one region.

    Results are cached for 6 hours keyed on (region_id, segment_id).

    Args:
        region_id:  Target region code, e.g. "TN-01".
        segment_id: Optional customer segment filter.

    Returns:
        The final TwinAIState after all agent nodes have run.
    """
    initial: TwinAIState = {
        "region_id": region_id,
        "segment_id": segment_id,
        "trends": [],
        "demand_forecast": {},
        "campaign_copy": [],
        "banner_briefs": [],
        "budget_allocation": {},
        "catalog_gaps": [],
        "weather_signal": None,
        "simulation_result": None,
        "explanation_log": [],
    }
    logger.info("Orchestrator: starting pipeline for region=%s segment=%s", region_id, segment_id)
    result: TwinAIState = await compiled_workflow.ainvoke(initial)
    logger.info("Orchestrator: pipeline complete for region=%s", region_id)
    return result


async def run_batch(region_ids: list[str]) -> dict[str, TwinAIState]:
    """Run the campaign pipeline for multiple regions concurrently.

    A bounded semaphore (size 5) keeps total concurrent Groq calls well
    under the 30 RPM free-tier limit.

    Args:
        region_ids: List of region codes to process.

    Returns:
        Dict mapping each region_id to its final TwinAIState.
    """
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
