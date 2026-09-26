"""Unit tests for agent nodes — LLM is mocked, no Groq calls.

Each agent node is tested with a patched chain so tests run offline,
cost nothing, and are deterministic.
"""
import pytest
from unittest.mock import patch, MagicMock

from app.graph.state import TwinAIState


# ── Helpers ───────────────────────────────────────────────────────────────────

def _base_state(region_id: str = "TN-01") -> TwinAIState:
    return TwinAIState(
        region_id=region_id,
        segment_id=None,
        trends=[],
        demand_forecast={},
        campaign_copy=[],
        banner_briefs=[],
        budget_allocation={},
        catalog_gaps=[],
        weather_signal=None,
        simulation_result=None,
        explanation_log=[],
    )


# ── Trend Detection ───────────────────────────────────────────────────────────

class TestTrendDetectionAgent:
    def test_run_returns_trends(self):
        state = _base_state()
        fake_trends = ["cotton kurtas", "LED diyas", "steel bottles"]
        with patch("app.agents.trend_detection._chain") as mock_chain:
            mock_chain.invoke.return_value = fake_trends
            from app.agents.trend_detection import run
            result = run(state)
        assert result["trends"] == fake_trends
        assert len(result["explanation_log"]) == 1
        assert "TN-01" in result["explanation_log"][0]

    def test_run_wraps_non_list(self):
        state = _base_state()
        with patch("app.agents.trend_detection._chain") as mock_chain:
            mock_chain.invoke.return_value = "single trend"
            from app.agents.trend_detection import run
            result = run(state)
        assert isinstance(result["trends"], list)


# ── Catalog Gap ───────────────────────────────────────────────────────────────

class TestCatalogGapAgent:
    def test_run_returns_gaps(self):
        state = _base_state()
        state["trends"] = ["ethnic footwear", "brass puja items"]
        fake_gaps = ["ethnic footwear", "brass puja items"]
        with patch("app.agents.catalog_gap._chain") as mock_chain:
            mock_chain.invoke.return_value = fake_gaps
            from app.agents.catalog_gap import run
            result = run(state)
        assert result["catalog_gaps"] == fake_gaps
        assert "explanation_log" in result


# ── Demand Forecasting ────────────────────────────────────────────────────────

class TestDemandForecastingAgent:
    def test_run_returns_forecast_dict(self):
        state = _base_state()
        state["trends"] = ["cotton kurtas"]
        state["weather_signal"] = "Temp 29°C | Upcoming: Pongal"
        state["catalog_gaps"] = []
        fake_forecast = {"apparel": 85.0, "kitchenware": 60.0}
        with patch("app.agents.demand_forecasting._chain") as mock_chain:
            mock_chain.invoke.return_value = fake_forecast
            from app.agents.demand_forecasting import run
            result = run(state)
        assert result["demand_forecast"] == fake_forecast

    def test_run_handles_non_dict(self):
        state = _base_state()
        with patch("app.agents.demand_forecasting._chain") as mock_chain:
            mock_chain.invoke.return_value = "not a dict"
            from app.agents.demand_forecasting import run
            result = run(state)
        assert isinstance(result["demand_forecast"], dict)


# ── Campaign Generator ────────────────────────────────────────────────────────

class TestCampaignGeneratorAgent:
    def test_run_returns_copy_lines(self):
        state = _base_state()
        state["demand_forecast"] = {"apparel": 80.0}
        state["trends"] = ["cotton kurtas"]
        state["weather_signal"] = "Temp 29°C"
        fake_copy = ["Celebrate Pongal with fresh cotton kurtas!", "Shop the Aadi Sale now."]
        with patch("app.agents.campaign_generator._chain") as mock_chain:
            mock_chain.invoke.return_value = fake_copy
            from app.agents.campaign_generator import run
            result = run(state)
        assert result["campaign_copy"] == fake_copy


# ── Budget Optimizer ──────────────────────────────────────────────────────────

class TestBudgetOptimizerAgent:
    def test_allocation_sums_to_one(self):
        state = _base_state()
        state["demand_forecast"] = {"apparel": 80.0}
        state["campaign_copy"] = ["line 1"]
        fake_alloc = {
            "social_media": 0.40, "search_ads": 0.30,
            "push_notifications": 0.15, "email": 0.10, "influencer": 0.05
        }
        with patch("app.agents.budget_optimizer._chain") as mock_chain:
            mock_chain.invoke.return_value = fake_alloc
            from app.agents.budget_optimizer import run
            result = run(state)
        total = sum(result["budget_allocation"].values())
        assert abs(total - 1.0) < 0.01

    def test_normalises_bad_allocation(self):
        state = _base_state()
        state["demand_forecast"] = {}
        state["campaign_copy"] = []
        # Intentionally sums to 2 — engine should normalise
        bad_alloc = {"social_media": 1.0, "search_ads": 1.0}
        with patch("app.agents.budget_optimizer._chain") as mock_chain:
            mock_chain.invoke.return_value = bad_alloc
            from app.agents.budget_optimizer import run
            result = run(state)
        total = sum(result["budget_allocation"].values())
        assert abs(total - 1.0) < 0.01


# ── Simulation Engine (no mock needed — fully deterministic) ──────────────────

class TestSimulationEngine:
    def test_baseline_conversion(self):
        from app.simulation.engine import SimulationEngine
        from app.models.simulation import SimulationRequest
        engine = SimulationEngine()
        req = SimulationRequest(region_id="TN-01")   # sensitivity=0.62 → base=0.38
        result = engine.run(req)
        assert abs(result.predicted_conversion_rate - 0.38) < 0.01

    def test_festival_boost(self):
        from app.simulation.engine import SimulationEngine
        from app.models.simulation import SimulationRequest
        engine = SimulationEngine()
        req = SimulationRequest(region_id="TN-01", festival_next_week=True)
        result = engine.run(req)
        assert result.predicted_conversion_rate > 0.38 + 0.20  # at least 0.58

    def test_inventory_shortfall_lowers_conversion(self):
        from app.simulation.engine import SimulationEngine
        from app.models.simulation import SimulationRequest
        engine = SimulationEngine()
        base = SimulationEngine().run(SimulationRequest(region_id="BR-01"))
        worse = engine.run(SimulationRequest(region_id="BR-01", inventory_shortfall_pct=0.5))
        assert worse.predicted_conversion_rate < base.predicted_conversion_rate

    def test_unknown_region_raises(self):
        from app.simulation.engine import SimulationEngine
        from app.models.simulation import SimulationRequest
        from app.core.exceptions import RegionNotFoundError
        engine = SimulationEngine()
        with pytest.raises(RegionNotFoundError):
            engine.run(SimulationRequest(region_id="XX-99"))

    def test_conversion_bounded_zero_to_one(self):
        from app.simulation.engine import SimulationEngine
        from app.models.simulation import SimulationRequest
        engine = SimulationEngine()
        # Extreme downside scenario
        req = SimulationRequest(
            region_id="BR-01",
            inventory_shortfall_pct=1.0,
            budget_multiplier=0.1,
            temperature_delta_c=15.0,
        )
        result = engine.run(req)
        assert 0.0 <= result.predicted_conversion_rate <= 1.0
