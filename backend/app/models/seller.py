"""Seller Pydantic schemas for TwinCart AI."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class SellerQuestionRequest(BaseModel):
    """A free-form question submitted by a seller to the Intelligence Agent."""

    question: str = Field(..., min_length=3, description="The seller's natural-language question")
    region_id: Optional[str] = Field("TN-01", description="Optional region context for the answer")
    category: Optional[str] = Field("apparel", description="Optional product category context")
    segment_id: Optional[str] = Field("students", description="Optional segment context for the answer")


class SellerQuestionResponse(BaseModel):
    """Answer and supporting context returned by the Seller Intelligence Agent."""

    question: str
    answer: str = Field(..., description="Direct answer to the seller's question")
    supporting_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key data points used to arrive at the answer",
    )
    confidence: str = Field(
        "high",
        description="Confidence level grounded in model backtest",
    )
    source: str = Field(
        "model_and_heuristics",
        description="Source attribution for data claims",
    )
    sources: Dict[str, str] = Field(
        default_factory=lambda: {
            "pricing_benchmark": "heuristic",
            "point_forecast": "model",
            "explanation": "llm_explanation",
        },
        description="Source provenance mapping for numeric and text claims",
    )
    from_cache: bool = Field(False, description="True when the answer was served from semantic cache")
