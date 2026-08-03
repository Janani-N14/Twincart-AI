"""What-If Simulation Engine.

A transparent, rule-based model that predicts conversion rate and a
relative revenue index when a seller perturbs one or more scenario
variables (festival timing, temperature, budget, inventory).

Design intent: keep this fully deterministic and explainable so the
platform is demo-able without training data.  When real historical order
data becomes available, swap the arithmetic model for a trained regressor
while keeping the same run() interface.
"""
import logging
from dataclasses import dataclass

from app.models.simulation import SimulationRequest, SimulationResponse
from app.twins.regional_twin import regional_twin_store
from app.core.exceptions import RegionNotFoundError, SimulationError

logger = logging.getLogger(__name__)


class SimulationEngine:
    """Stateless simulation engine — all state lives in the RegionalTwinStore."""

    def __init__(self) -> None:
        self._store = regional_twin_store

    def run(self, request: SimulationRequest) -> SimulationResponse:
        """Run a what-if scenario and return predicted KPIs.

        Args:
            request: SimulationRequest with region_id and scenario variables.

        Returns:
            SimulationResponse with predicted_conversion_rate and
            predicted_revenue_index.

        Raises:
            RegionNotFoundError: if region_id is not in the twin store.
            SimulationError: if the scenario parameters are internally inconsistent.
        """
        twin = self._store.get(request.region_id)  # raises RegionNotFoundError if missing

        # --- Base conversion rate: inversely proportional to price sensitivity
        base_conversion = 1.0 - twin.price_sensitivity   # e.g. 0.38 for TN-01 (sensitivity 0.62)

        # --- Scenario adjustments (additive deltas on base_conversion) --------
        festival_boost      = 0.25  if request.festival_next_week          else 0.0
        weather_penalty     = -0.01 * abs(request.temperature_delta_c)
        budget_effect       =  0.15 * (request.budget_multiplier - 1.0)
        inventory_penalty   = -0.50 * request.inventory_shortfall_pct

        raw_conversion = (
            base_conversion
            + festival_boost
            + weather_penalty
            + budget_effect
            + inventory_penalty
        )
        predicted_conversion = max(0.0, min(1.0, raw_conversion))

        # --- Revenue index: scaled by budget multiplier ----------------------
        predicted_revenue_index = round(
            predicted_conversion * request.budget_multiplier * 100, 1
        )

        # --- Plain-language interpretation -----------------------------------
        drivers: list[str] = []
        if festival_boost > 0:
            drivers.append("a nearby festival boosts conversions by +25 pp")
        if weather_penalty < -0.05:
            drivers.append(f"large temperature deviation cuts conversions by {weather_penalty:.0%}")
        if budget_effect > 0:
            drivers.append(f"increased budget lifts conversions by {budget_effect:.0%}")
        elif budget_effect < 0:
            drivers.append(f"reduced budget lowers conversions by {abs(budget_effect):.0%}")
        if inventory_penalty < 0:
            drivers.append(f"inventory shortfall reduces conversions by {abs(inventory_penalty):.0%}")

        if drivers:
            interpretation = (
                f"For {twin.state}, predicted conversion is {predicted_conversion:.1%}. "
                f"Key drivers: {'; '.join(drivers)}. "
                f"Revenue index: {predicted_revenue_index}."
            )
        else:
            interpretation = (
                f"For {twin.state}, baseline scenario. "
                f"Predicted conversion: {predicted_conversion:.1%}, "
                f"revenue index: {predicted_revenue_index}."
            )

        logger.info(
            "[simulation] %s → conversion=%.3f, revenue_index=%.1f",
            request.region_id, predicted_conversion, predicted_revenue_index,
        )

        return SimulationResponse(
            region_id=request.region_id,
            scenario=request,
            predicted_conversion_rate=round(predicted_conversion, 3),
            predicted_revenue_index=predicted_revenue_index,
            interpretation=interpretation,
        )


# Module-level singleton
simulation_engine = SimulationEngine()
