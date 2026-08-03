from pydantic import BaseModel, Field


class CampaignRequest(BaseModel):
    """Request body to trigger the full campaign generation pipeline."""

    region_id: str = Field(..., description="Target region code, e.g. TN-01")
    segment_id: str | None = Field(None, description="Optional customer segment filter")


class CampaignResponse(BaseModel):
    """Full campaign output from the LangGraph agent pipeline."""

    region_id: str
    segment_id: str | None = None
    trends: list[str] = Field(default_factory=list, description="Detected product trends")
    demand_forecast: dict[str, float] = Field(
        default_factory=dict,
        description="Category → predicted demand index (0–100)",
    )
    campaign_copy: list[str] = Field(
        default_factory=list,
        description="Ready-to-use campaign text lines",
    )
    banner_briefs: list[str] = Field(
        default_factory=list,
        description="Visual banner creative briefs for each campaign",
    )
    budget_allocation: dict[str, float] = Field(
        default_factory=dict,
        description="Channel → recommended budget fraction (sums to 1.0)",
    )
    catalog_gaps: list[str] = Field(
        default_factory=list,
        description="Product categories with supply gaps vs. detected demand",
    )
    weather_signal: str | None = Field(None, description="Current weather context used by agents")
    explanation: str = Field("", description="Plain-language explanation of all recommendations")


class BannerBrief(BaseModel):
    """Structured brief for a single marketing banner."""

    headline: str = Field(..., description="Primary banner headline (max 10 words)")
    subtext: str = Field(..., description="Supporting copy (max 20 words)")
    cta: str = Field(..., description="Call-to-action button text")
    visual_style: str = Field(..., description="Suggested colour palette and imagery style")
    target_segment: str | None = None
