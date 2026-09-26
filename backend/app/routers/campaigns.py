"""FastAPI router — Campaign generation."""
import logging

from fastapi import APIRouter, HTTPException

from app.models.campaign import CampaignRequest, CampaignResponse
from app.services.orchestrator import run_campaign_pipeline, run_batch
from app.core.exceptions import TwinAIError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate", response_model=CampaignResponse, summary="Generate hyperlocal campaigns")
async def generate_campaign(payload: CampaignRequest) -> CampaignResponse:
    """Run the full TwinAI LangGraph pipeline for the given region and return
    campaign copy, banner briefs, budget allocation, and a plain-language
    explanation.

    Results are cached for 6 hours per (region_id, segment_id) pair.
    """
    try:
        result = await run_campaign_pipeline(payload.region_id, payload.segment_id)
    except TwinAIError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Campaign pipeline failed for region=%s", payload.region_id)
        raise HTTPException(status_code=502, detail=f"Agent pipeline error: {exc}") from exc

    # The last entry in explanation_log is the human-readable summary from
    # the explainability agent; join all entries as a fallback.
    explanation = " ".join(result.get("explanation_log") or [])

    return CampaignResponse(
        region_id=payload.region_id,
        segment_id=payload.segment_id,
        trends=result.get("trends") or [],
        demand_forecast=result.get("demand_forecast") or {},
        campaign_copy=result.get("campaign_copy") or [],
        banner_briefs=result.get("banner_briefs") or [],
        budget_allocation=result.get("budget_allocation") or {},
        catalog_gaps=result.get("catalog_gaps") or [],
        weather_signal=result.get("weather_signal"),
        explanation=explanation,
    )


@router.post("/batch", response_model=dict[str, CampaignResponse], summary="Batch campaign generation")
async def batch_generate(region_ids: list[str]) -> dict[str, CampaignResponse]:
    """Generate campaigns for multiple regions concurrently (max 5 at a time)."""
    if not region_ids:
        raise HTTPException(status_code=400, detail="region_ids list must not be empty.")
    if len(region_ids) > 15:
        raise HTTPException(status_code=400, detail="Maximum 15 regions per batch request.")

    try:
        results = await run_batch(region_ids)
    except Exception as exc:
        logger.exception("Batch campaign generation failed")
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {
        rid: CampaignResponse(
            region_id=rid,
            trends=state.get("trends") or [],
            demand_forecast=state.get("demand_forecast") or {},
            campaign_copy=state.get("campaign_copy") or [],
            banner_briefs=state.get("banner_briefs") or [],
            budget_allocation=state.get("budget_allocation") or {},
            catalog_gaps=state.get("catalog_gaps") or [],
            weather_signal=state.get("weather_signal"),
            explanation=" ".join(state.get("explanation_log") or []),
        )
        for rid, state in results.items()
    }
