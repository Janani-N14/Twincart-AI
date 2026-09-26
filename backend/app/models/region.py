from pydantic import BaseModel, Field


class RegionalTwin(BaseModel):
    """Represents a Regional Digital Twin for one Indian state/zone."""

    region_id: str = Field(..., description="Unique region code, e.g. TN-01")
    id: str | None = Field(None, description="Alternative ID field matching region_id")
    state: str = Field(..., description="Full state name")
    city: str | None = Field("Tier-2 Hub", description="Representative city or district hub")
    population_tier: str | None = Field("Tier-2", description="Population tier (Tier-2 / Tier-3)")
    languages: list[str] = Field(..., description="Primary languages spoken in the region")
    top_categories: list[str] = Field(..., description="Top retail product categories")
    price_sensitivity: float = Field(..., ge=0.0, le=1.0, description="0 = low sensitivity, 1 = high")
    active_festivals: list[str] = Field(default_factory=list, description="Key festivals in this region")
    avg_temperature_c: float | None = Field(None, description="Average annual temperature in Celsius")
    avg_temp_by_month: list[float] | None = Field(
        default_factory=lambda: [24.0, 26.0, 28.0, 31.0, 33.0, 32.0, 30.0, 29.0, 28.0, 27.0, 25.0, 24.0],
        description="Average monthly temperatures from Jan to Dec"
    )

    def model_post_init(self, __context) -> None:
        if not self.id:
            self.id = self.region_id



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
