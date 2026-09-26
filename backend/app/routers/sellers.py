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
    """Answer a seller's free-form question using regional twin data and the
    festival calendar.

    Responses for semantically similar questions are served from an
    in-process semantic cache to reduce Groq API calls.
    """
    try:
        result = seller_intelligence.answer(
            question=payload.question,
            region_id=payload.region_id,
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
        confidence=result.get("confidence", "medium"),
        from_cache=result.get("from_cache", False),
    )
