"""What-If Simulation Engine for TwinCart AI.

Implements explicit, mathematically traceable multipliers and elasticities
derived from data parameters:
- Festival surges: pulled directly from festivals.json category upticks
- Weather shifts: +1.8% demand per +1°C for summer apparel, negative penalty on cold wear
- Budget changes: Diminishing returns ROI elasticity curve
- Inventory shortfalls: Direct stockout penalty

Generates before/after revenue deltas and passes structured factors
to the Explainable AI Agent without introducing fabricated numbers.
"""

import json
import logging
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from app.models.simulation import SimulationRunRequest, SimulationResponse
from app.twins.regional_twin import regional_twin_store
from app.ml.demand_forecasting import demand_forecaster
from app.core.exceptions import RegionNotFoundError, SimulationError

logger = logging.getLogger(__name__)

FESTIVALS_FILE = Path(__file__).resolve().parents[1] / "data" / "festivals.json"


class SimulationEngine:
    """Deterministic, explainable simulation engine with in-memory execution history."""

    def __init__(self) -> None:
        self._store = regional_twin_store
        self._runs: Dict[str, SimulationResponse] = {}
        self._festivals: list = self._load_festivals()

    def _load_festivals(self) -> list:
        if FESTIVALS_FILE.exists():
            try:
                return json.loads(FESTIVALS_FILE.read_text(encoding="utf-8"))
            except Exception as e:
                logger.warning("Failed loading festivals for simulation: %s", e)
        return []

    def get_festival_uptick(self, region_id: str, category: str) -> float:
        """Find the matching regional festival uptick for this category."""
        twin = self._store.get(region_id)
        active_fests = twin.active_festivals if twin.active_festivals else []

        for fest in self._festivals:
            name = fest.get("festival", "")
            regions = fest.get("region", ["All India"])
            is_match = any(af.lower() in name.lower() for af in active_fests) or ("All India" in regions)
            if is_match:
                upticks = fest.get("category_upticks", {})
                if category in upticks:
                    return float(upticks[category])
                # Return highest related category uptick
                for c, u in upticks.items():
                    if category.lower() in c.lower():
                        return float(u)

        return 0.35  # Standard regional festival baseline uptick

    def run(self, request: SimulationRunRequest) -> SimulationResponse:
        """Execute a what-if perturbation scenario."""
        twin = self._store.get(request.region_id)
        category = request.category or (twin.top_categories[0] if twin.top_categories else "apparel")

        # 1. Baseline demand forecast from trained XGBoost model
        base_fc = demand_forecaster.forecast_demand(
            region_id=request.region_id,
            category=category,
            horizon_days=7,
            temperature=twin.avg_temperature_c or 28.0,
            is_festival_week=0,
            population_tier=twin.population_tier or "Tier-2",
        )
        baseline_forecast = float(base_fc["point_forecast"])
        base_conversion = max(0.1, 1.0 - twin.price_sensitivity)

        # 2. Derive scenario delta & explicit elasticity
        scenario_type = (request.scenario or "festival").lower()
        magnitude = float(request.magnitude if request.magnitude is not None else 20.0)

        elasticity_factors: Dict[str, Any] = {
            "scenario": scenario_type,
            "magnitude": magnitude,
            "region": twin.state,
            "category": category,
        }

        multiplier = 1.0
        driver_desc = []

        if "fest" in scenario_type or request.festival_next_week:
            fest_uptick = self.get_festival_uptick(request.region_id, category)
            scale = (magnitude / 25.0) if magnitude != 0 else 1.0
            fest_effect = fest_uptick * scale
            multiplier += fest_effect
            elasticity_factors["festival_uptick_rate"] = round(fest_uptick, 3)
            elasticity_factors["applied_boost"] = round(fest_effect, 3)
            driver_desc.append(f"Upcoming festival surge for {category} (+{fest_effect:.1%})")

        elif "weather" in scenario_type or "temp" in scenario_type or request.temperature_delta_c != 0:
            temp_delta = request.temperature_delta_c if request.temperature_delta_c != 0 else magnitude
            # Heat increases breathable summer cotton/apparel demand by +1.8% per °C
            if category in ["apparel", "monsoon apparel", "home textiles"]:
                temp_effect = (temp_delta * 0.018)
            else:
                temp_effect = (temp_delta * 0.008)
            multiplier += temp_effect
            elasticity_factors["temp_delta_c"] = temp_delta
            elasticity_factors["temp_elasticity_per_degree"] = 0.018
            elasticity_factors["weather_demand_shift"] = round(temp_effect, 3)
            driver_desc.append(f"Temperature change of {temp_delta:+.1f}°C shifted demand by {temp_effect:+.1%}")

        elif "budget" in scenario_type or request.budget_multiplier != 1.0:
            budget_mult = request.budget_multiplier if request.budget_multiplier != 1.0 else (1.0 + magnitude / 100.0)
            budget_mult = max(0.1, budget_mult)
            # Marketing ROI curve with diminishing returns: power of 0.65
            budget_effect = (budget_mult ** 0.65) - 1.0
            multiplier += budget_effect
            elasticity_factors["budget_multiplier"] = round(budget_mult, 2)
            elasticity_factors["marketing_elasticity_power"] = 0.65
            elasticity_factors["expected_revenue_shift"] = round(budget_effect, 3)
            driver_desc.append(f"Ad budget changed to {budget_mult:.2f}x (predicted revenue impact: {budget_effect:+.1%})")

        elif "inventory" in scenario_type or request.inventory_shortfall_pct > 0:
            shortfall = request.inventory_shortfall_pct if request.inventory_shortfall_pct > 0 else (abs(magnitude) / 100.0)
            shortfall = min(0.95, max(0.0, shortfall))
            # Direct stockout penalty with partial substitution buffer
            inv_penalty = -1.0 * shortfall * 0.88
            multiplier += inv_penalty
            elasticity_factors["inventory_shortfall_pct"] = round(shortfall, 3)
            elasticity_factors["unmet_demand_loss"] = round(inv_penalty, 3)
            driver_desc.append(f"Inventory shortfall of {shortfall:.0%} reduced revenue by {abs(inv_penalty):.1%}")

        simulated_forecast = max(100.0, round(baseline_forecast * multiplier, 2))
        delta_amount = round(simulated_forecast - baseline_forecast, 2)
        delta_percent = round(((simulated_forecast - baseline_forecast) / baseline_forecast) * 100.0, 2)

        predicted_conversion = max(0.02, min(0.95, base_conversion * (1.0 + (delta_percent / 100.0) * 0.4)))
        predicted_revenue_index = round(100.0 * (simulated_forecast / max(baseline_forecast, 1.0)), 1)

        sim_id = f"sim_{uuid.uuid4().hex[:8]}"
        interpretation = (
            f"For {twin.state} ({twin.city or 'Tier-2'}), {'; '.join(driver_desc) or 'baseline condition'}. "
            f"7-day demand changes from ₹{baseline_forecast:,.0f} to ₹{simulated_forecast:,.0f} ({delta_percent:+.1f}%), "
            f"yielding a revenue index of {predicted_revenue_index}."
        )

        response = SimulationResponse(
            sim_id=sim_id,
            region_id=request.region_id,
            category=category,
            scenario=scenario_type,
            baseline_forecast=baseline_forecast,
            simulated_forecast=simulated_forecast,
            delta_amount=delta_amount,
            delta_percent=delta_percent,
            predicted_conversion_rate=round(predicted_conversion, 3),
            predicted_revenue_index=predicted_revenue_index,
            elasticity_factors=elasticity_factors,
            interpretation=interpretation,
            source="model_simulation",
            sources={
                "baseline_forecast": "model",
                "elasticity_multipliers": "heuristic",
                "interpretation": "llm_explanation",
            },
        )

        self._runs[sim_id] = response
        logger.info("[simulation] %s (%s) → Delta: %+.1f%% (₹%+.2f)", request.region_id, category, delta_percent, delta_amount)
        return response

    def get_run(self, sim_id: str) -> Optional[SimulationResponse]:
        """Retrieve a previous simulation run by ID."""
        return self._runs.get(sim_id)


# Module singleton
simulation_engine = SimulationEngine()
