from pydantic import BaseModel, Field


class RegionalTwin(BaseModel):
    """Represents a Regional Digital Twin for one Indian state/zone."""

    region_id: str = Field(..., description="Unique region code, e.g. TN-01")
    state: str = Field(..., description="Full state name")
    languages: list[str] = Field(..., description="Primary languages spoken in the region")
    top_categories: list[str] = Field(..., description="Top retail product categories")
    price_sensitivity: float = Field(..., ge=0.0, le=1.0, description="0 = low sensitivity, 1 = high")
    active_festivals: list[str] = Field(default_factory=list, description="Key festivals in this region")
    avg_temperature_c: float | None = Field(None, description="Average annual temperature in Celsius")


class RegionInsightRequest(BaseModel):
    """Request body for generating insights for a specific region."""

    region_id: str = Field(..., description="Target region code")
    segment_id: str | None = Field(None, description="Optional customer segment filter")


class RegionInsightResponse(BaseModel):
    """Full insight payload returned after running the agent pipeline."""

    region_id: str
    trending_products: list[str]
    demand_forecast: dict[str, float]
    recommended_campaigns: list[str]
    explanation: str
