"""Simulation Pydantic schemas for TwinCart AI."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SimulationRunRequest(BaseModel):
    """Direct scenario perturbation request body."""

    region_id: str = Field("TN-01", description="Target region code, e.g. TN-01")
    category: str = Field("apparel", description="Product category to simulate")
    scenario: str = Field("festival", description="Scenario type: festival | weather | budget | inventory")
    magnitude: float = Field(25.0, description="Perturbation magnitude (e.g. +25% budget, +5°C temp, -20% stock)")
    festival_next_week: bool = Field(False, description="Whether a major festival is starting")
    temperature_delta_c: float = Field(0.0, description="Temperature deviation in Celsius")
    budget_multiplier: float = Field(1.0, description="Budget multiple (1.0 = baseline)")
    inventory_shortfall_pct: float = Field(0.0, description="Inventory out of stock fraction 0.0-1.0")


class SimulationRequest(SimulationRunRequest):
    """Backwards-compatible alias for simulation request."""
    pass


class SimulationResponse(BaseModel):
    """Predicted outcomes for the given What-If scenario."""

    sim_id: Optional[str] = Field(None, description="Unique simulation run identifier")
    region_id: str
    category: str = "apparel"
    scenario: str = Field("festival", description="The scenario type simulated")
    baseline_forecast: float = Field(..., description="Baseline 7-day revenue (INR)")
    simulated_forecast: float = Field(..., description="Simulated 7-day revenue (INR)")
    delta_amount: float = Field(..., description="Absolute change in INR revenue")
    delta_percent: float = Field(..., description="Percentage change in revenue")
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
    elasticity_factors: Dict[str, Any] = Field(
        default_factory=dict,
        description="Exact parameter multipliers applied during simulation",
    )
    interpretation: str = Field(
        "",
        description="Plain-language summary of what the scenario implies",
    )
    source: str = Field("model_simulation", description="Data source origin")
    sources: Dict[str, str] = Field(
        default_factory=lambda: {
            "baseline_forecast": "model",
            "elasticity_multipliers": "heuristic",
            "interpretation": "llm_explanation",
        },
        description="Per-claim data source provenance",
    )
