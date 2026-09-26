"""FastAPI router — Seller Intelligence Agent."""

import logging
from fastapi import APIRouter, HTTPException

from app.models.seller import SellerQuestionRequest, SellerQuestionResponse
from app.agents import seller_intelligence
from app.core.exceptions import TwinAIError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/ask", response_model=SellerQuestionResponse, summary="Ask the Seller Intelligence Agent")
async def ask_seller_agent(payload: SellerQuestionRequest) -> SellerQuestionResponse:
    """Answer a seller's free-form question using regional digital twin forecasts,
    festival calendars, and category benchmark pricing percentiles.
    """
    try:
        result = seller_intelligence.answer(
            question=payload.question,
            region_id=payload.region_id,
            category=payload.category,
            segment_id=payload.segment_id,
        )
    except TwinAIError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Seller intelligence agent failed")
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return SellerQuestionResponse(
        question=payload.question,
        answer=result.get("answer", ""),
        supporting_data=result.get("supporting_data", {}),
        confidence=result.get("confidence", "high"),
        source=result.get("source", "model_and_heuristics"),
        sources=result.get("sources", {
            "pricing_benchmark": "heuristic",
            "point_forecast": "model",
            "explanation": "llm_explanation",
        }),
        from_cache=result.get("from_cache", False),
    )
