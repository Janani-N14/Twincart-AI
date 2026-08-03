from pydantic import BaseModel, Field


class SellerQuestionRequest(BaseModel):
    """A free-form question submitted by a seller to the Intelligence Agent."""

    question: str = Field(..., min_length=5, description="The seller's natural-language question")
    region_id: str | None = Field(None, description="Optional region context for the answer")
    segment_id: str | None = Field(None, description="Optional segment context for the answer")


class SellerQuestionResponse(BaseModel):
    """Answer and supporting context returned by the Seller Intelligence Agent."""

    question: str
    answer: str = Field(..., description="Direct answer to the seller's question")
    supporting_data: dict[str, object] = Field(
        default_factory=dict,
        description="Key data points used to arrive at the answer",
    )
    confidence: str = Field(
        "medium",
        description="Agent's self-assessed confidence: low | medium | high",
    )
    from_cache: bool = Field(False, description="True when the answer was served from semantic cache")
