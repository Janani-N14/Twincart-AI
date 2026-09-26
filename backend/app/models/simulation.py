from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    """What-If scenario parameters for the simulation engine."""

    region_id: str = Field(..., description="Target region code")
    festival_next_week: bool = Field(False, description="True if a major festival falls within the next 7 days")
    temperature_delta_c: float = Field(
        0.0,
        description="Deviation from the region's average temperature (positive = hotter)",
    )
    budget_multiplier: float = Field(
        1.0,
        ge=0.1,
        le=10.0,
        description="Marketing budget as a multiple of the baseline (1.0 = no change)",
    )
    inventory_shortfall_pct: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Fraction of top-category inventory that is out of stock (0–1)",
    )


class SimulationResponse(BaseModel):
    """Predicted outcomes for the given What-If scenario."""

    region_id: str
    scenario: SimulationRequest
    predicted_conversion_rate: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model-predicted order conversion rate for this scenario",
    )
    predicted_revenue_index: float = Field(
        ...,
        description="Relative revenue index (100 = baseline region performance)",
    )
    interpretation: str = Field(
        "",
        description="Plain-language summary of what the scenario implies",
    )
