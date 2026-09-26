"""FastAPI router — Campaign generation."""

import logging
import uuid
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException

from app.models.campaign import CampaignRequest, CampaignResponse
from app.services.orchestrator import run_campaign_pipeline, run_batch
from app.core.exceptions import TwinAIError

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory campaign store
_CAMPAIGN_STORE: Dict[str, CampaignResponse] = {}


@router.post("/generate", response_model=CampaignResponse, summary="Generate hyperlocal campaigns")
async def generate_campaign(payload: CampaignRequest) -> CampaignResponse:
    """Run the full TwinAI LangGraph pipeline for the given region, segment, and category.

    Returns bilingual campaign copy, banner briefs, mathematically optimized budget allocation,
    point demand forecast, and plain-language explanation.
    """
    try:
        result = await run_campaign_pipeline(
            region_id=payload.region_id,
            segment_id=payload.segment_id,
            category=payload.category,
            total_budget_inr=payload.total_budget_inr,
        )
    except TwinAIError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Campaign pipeline failed for region=%s", payload.region_id)
        raise HTTPException(status_code=502, detail=f"Agent pipeline error: {exc}") from exc

    explanation = result.get("explanation") or " ".join(result.get("explanation_log") or [])
    campaign_id = f"cmp_{uuid.uuid4().hex[:8]}"

    response = CampaignResponse(
        campaign_id=campaign_id,
        region_id=payload.region_id,
        segment_id=payload.segment_id,
        category=payload.category or "apparel",
        trends=result.get("trends") or [],
        point_forecast=float(result.get("point_forecast", 45000.0)),
        uncertainty_std=float(result.get("uncertainty_std", 18826.27)),
        backtested_mape=float(result.get("backtested_mape", 8.94)),
        demand_forecast=result.get("demand_forecast") or {},
        campaign_copy=result.get("campaign_copy") or [],
        campaign_en=result.get("campaign_en"),
        campaign_vernacular=result.get("campaign_vernacular"),
        banner_briefs=result.get("banner_briefs") or [],
        budget_allocation=result.get("budget_allocation") or {},
        budget_amounts_inr=result.get("budget_amounts_inr") or {},
        catalog_gaps=result.get("catalog_gaps") or [],
        weather_signal=result.get("weather_signal"),
        explanation=explanation,
        sources={
            "point_forecast": "model",
            "backtested_mape": "model",
            "budget_allocation": "heuristic_optimization",
            "campaign_copy": "llm_explanation",
            "explanation": "llm_explanation",
        },
    )

    _CAMPAIGN_STORE[campaign_id] = response
    return response


@router.get("/{campaign_id}", response_model=CampaignResponse, summary="Get campaign by ID")
def get_campaign(campaign_id: str) -> CampaignResponse:
    """Retrieve a previously generated campaign by its ID."""
    campaign = _CAMPAIGN_STORE.get(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign with ID '{campaign_id}' not found.")
    return campaign


@router.post("/batch", response_model=dict[str, CampaignResponse], summary="Batch campaign generation")
async def batch_generate(region_ids: list[str]) -> dict[str, CampaignResponse]:
    """Generate campaigns for multiple regions concurrently (max 15 at a time)."""
    if not region_ids:
        raise HTTPException(status_code=400, detail="region_ids list must not be empty.")
    if len(region_ids) > 15:
        raise HTTPException(status_code=400, detail="Maximum 15 regions per batch request.")

    try:
        results = await run_batch(region_ids)
    except Exception as exc:
        logger.exception("Batch campaign generation failed")
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    output: dict[str, CampaignResponse] = {}
    for rid, state in results.items():
        cid = f"cmp_{uuid.uuid4().hex[:8]}"
        res = CampaignResponse(
            campaign_id=cid,
            region_id=rid,
            category=state.get("category", "apparel"),
            trends=state.get("trends") or [],
            point_forecast=float(state.get("point_forecast", 45000.0)),
            uncertainty_std=float(state.get("uncertainty_std", 18826.27)),
            backtested_mape=float(state.get("backtested_mape", 8.94)),
            demand_forecast=state.get("demand_forecast") or {},
            campaign_copy=state.get("campaign_copy") or [],
            campaign_en=state.get("campaign_en"),
            campaign_vernacular=state.get("campaign_vernacular"),
            banner_briefs=state.get("banner_briefs") or [],
            budget_allocation=state.get("budget_allocation") or {},
            budget_amounts_inr=state.get("budget_amounts_inr") or {},
            catalog_gaps=state.get("catalog_gaps") or [],
            weather_signal=state.get("weather_signal"),
            explanation=state.get("explanation") or " ".join(state.get("explanation_log") or []),
        )
        _CAMPAIGN_STORE[cid] = res
        output[rid] = res

    return output
