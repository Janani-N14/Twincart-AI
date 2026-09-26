"""Campaign Pydantic schemas for TwinCart AI."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CampaignRequest(BaseModel):
    """Request body to trigger the full campaign generation pipeline."""

    region_id: str = Field("TN-01", description="Target region code, e.g. TN-01")
    segment_id: Optional[str] = Field("students", description="Target customer segment")
    category: Optional[str] = Field("apparel", description="Target product category")
    total_budget_inr: float = Field(50000.0, description="Total marketing budget in INR")


class CampaignResponse(BaseModel):
    """Full campaign output from the LangGraph agent pipeline."""

    campaign_id: str = Field(..., description="Unique campaign execution ID")
    region_id: str
    segment_id: Optional[str] = None
    category: str = "apparel"
    trends: List[str] = Field(default_factory=list, description="Detected product trends")
    point_forecast: float = Field(..., description="Projected 7-day revenue (INR)")
    uncertainty_std: float = Field(..., description="Empirical residual std from backtest")
    backtested_mape: float = Field(..., description="Honest backtested model MAPE percentage")
    demand_forecast: Dict[str, float] = Field(
        default_factory=dict,
        description="Category → predicted demand index (0–100)",
    )
    campaign_copy: List[str] = Field(
        default_factory=list,
        description="Ready-to-use campaign text lines",
    )
    campaign_en: Optional[Dict[str, Any]] = Field(
        None,
        description="English campaign headline, body, and CTA",
    )
    campaign_vernacular: Optional[Dict[str, Any]] = Field(
        None,
        description="Vernacular localized campaign headline, body, and CTA",
    )
    banner_briefs: List[str] = Field(
        default_factory=list,
        description="Visual banner creative briefs for each campaign",
    )
    budget_allocation: Dict[str, float] = Field(
        default_factory=dict,
        description="Channel → recommended budget fraction (sums to 1.0)",
    )
    budget_amounts_inr: Dict[str, float] = Field(
        default_factory=dict,
        description="Channel → allocated budget in INR",
    )
    catalog_gaps: List[str] = Field(
        default_factory=list,
        description="Product categories with supply gaps vs. detected demand",
    )
    weather_signal: Optional[str] = Field(None, description="Current weather context used by agents")
    explanation: str = Field("", description="Plain-language explanation of all recommendations")
    sources: Dict[str, str] = Field(
        default_factory=lambda: {
            "demand_forecast": "model",
            "budget_allocation": "heuristic_optimization",
            "campaign_copy": "llm_explanation",
            "explanation": "llm_explanation",
        },
        description="Attribution source per numeric and generative claim",
    )


class BannerBrief(BaseModel):
    """Structured brief for a single marketing banner."""

    headline: str = Field(..., description="Primary banner headline (max 10 words)")
    subtext: str = Field(..., description="Supporting copy (max 20 words)")
    cta: str = Field(..., description="Call-to-action button text")
    visual_style: str = Field(..., description="Suggested colour palette and imagery style")
    target_segment: Optional[str] = None
