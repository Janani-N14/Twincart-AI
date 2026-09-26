from pydantic import BaseModel, Field


SEGMENT_IDS = ["students", "working_professionals", "homemakers", "budget_shoppers", "young_parents"]


class CustomerSegmentTwin(BaseModel):
    """Represents a Customer Segment Digital Twin."""

    segment_id: str = Field(..., description="Unique segment identifier, e.g. 'students'")
    id: str | None = Field(None, description="Alternative ID field matching segment_id")
    label: str = Field(..., description="Human-readable segment name")
    age_range: str = Field(..., description="Typical age bracket, e.g. '18-24'")
    budget_range: str | None = Field("₹500 - ₹2,000", description="Typical order budget range")
    income_bracket: str = Field(..., description="Approximate monthly income range (INR)")
    preferred_categories: list[str] = Field(..., description="Top categories this segment buys")
    languages: list[str] = Field(default_factory=lambda: ["English", "Hindi"], description="Preferred communication languages")
    purchase_trigger: str | None = Field("Promotional discounts and seasonal offers", description="Key trigger driving conversions")
    platform_behaviour: str = Field(..., description="Brief description of shopping behaviour")
    price_sensitivity: float = Field(..., ge=0.0, le=1.0)
    region_ids: list[str] = Field(default_factory=list, description="Regions where this segment is significant")

    def model_post_init(self, __context) -> None:
        if not self.id:
            self.id = self.segment_id



class SegmentInsightRequest(BaseModel):
    segment_id: str = Field(..., description="Target segment identifier")
    region_id: str | None = Field(None, description="Optional regional context")


class SegmentInsightResponse(BaseModel):
    segment_id: str
    label: str
    top_trends: list[str]
    recommended_campaigns: list[str]
    explanation: str
