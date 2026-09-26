"""Phase 3 Unit Tests: Agent Network & Orchestration.

Tests all agents with deterministic offline execution:
1. Trend Detection Agent
2. Demand Forecasting Agent
3. Scenario Simulation Engine
4. Campaign Generation Agent
5. Budget Optimization Agent
6. Explainable AI Agent
7. Seller Growth Agent
"""

import pytest
from app.graph.state import TwinAIState
from app.agents import (
    trend_detection,
    demand_forecasting,
    campaign_generator,
    budget_optimizer,
    explainability,
    seller_intelligence,
)
from app.simulation.engine import simulation_engine
from app.models.simulation import SimulationRunRequest


def _base_state(region_id: str = "TN-01") -> TwinAIState:
    return {
        "region_id": region_id,
        "segment_id": "students",
        "category": "apparel",
        "total_budget_inr": 50000.0,
        "trends": [],
        "demand_forecast": {},
        "campaign_copy": [],
        "banner_briefs": [],
        "budget_allocation": {},
        "catalog_gaps": [],
        "weather_signal": None,
        "simulation_result": None,
        "explanation_log": [],
    }


class TestTrendDetectionAgent:
    def test_run_computes_growth_and_trends(self):
        state = _base_state("TN-01")
        res = trend_detection.run(state)
        assert "trends" in res
        assert len(res["trends"]) >= 3
        assert "trend_growth_rate" in res
        assert isinstance(res["trend_growth_rate"], float)
        assert len(res["explanation_log"]) == 1


class TestDemandForecastingAgent:
    def test_run_produces_point_forecast_and_uncertainty_band(self):
        state = _base_state("TN-01")
        res = demand_forecasting.run(state)
        assert "point_forecast" in res
        assert res["point_forecast"] > 0
        assert "uncertainty_lower" in res
        assert "uncertainty_upper" in res
        assert "uncertainty_std" in res
        assert res["uncertainty_std"] > 0
        assert res["uncertainty_upper"] >= res["point_forecast"]
        assert "backtested_mape" in res
        assert res["backtested_mape"] < 35.0
        assert res["forecast_source"] == "model"


class TestCampaignGeneratorAgent:
    def test_run_generates_bilingual_campaign(self):
        state = _base_state("TN-01")
        state["point_forecast"] = 48000.0
        state["trends"] = ["cotton kurtas", "silver oxidized jhumkas"]
        res = campaign_generator.run(state)
        assert "campaign_en" in res
        assert "campaign_vernacular" in res
        assert res["campaign_vernacular"]["language"] == "Tamil"
        assert res["campaign_en"]["headline"] is not None
        assert res["campaign_vernacular"]["headline"] is not None
        assert len(res["campaign_copy"]) >= 2


class TestBudgetOptimizerAgent:
    def test_linear_programming_allocation(self):
        state = _base_state("TN-01")
        state["total_budget_inr"] = 60000.0
        res = budget_optimizer.run(state)
        shares = res["budget_allocation"]
        amounts = res["budget_amounts_inr"]

        assert abs(sum(shares.values()) - 1.0) < 0.02
        assert abs(sum(amounts.values()) - 60000.0) < 5.0
        assert res["budget_optimization_result"]["source"] == "heuristic_optimization"
        assert "social_reels" in shares
        assert "whatsapp_community" in shares


class TestExplainabilityAgent:
    def test_grounded_factors_and_no_hallucinations(self):
        state = _base_state("TN-01")
        state["point_forecast"] = 52000.0
        state["simulated_forecast"] = 68000.0
        state["delta_amount"] = 16000.0
        state["delta_percent"] = 30.77
        res = explainability.run(state)

        assert "explanation" in res
        assert len(res["explanation"]) > 50
        assert "grounded_factors" in res
        assert res["grounded_factors"]["point_forecast_inr"] == 52000.0
        assert res["grounded_factors"]["simulated_forecast_inr"] == 68000.0
        assert res["explanation_source"] == "llm_explanation"


class TestSellerGrowthAgent:
    def test_answer_uses_benchmarks_and_forecasts(self):
        res = seller_intelligence.answer(
            question="What is the best pricing strategy for cotton kurtas in Tamil Nadu?",
            region_id="TN-01",
            category="apparel",
        )
        assert "answer" in res
        assert len(res["answer"]) > 50
        assert "supporting_data" in res
        assert "pricing_percentiles" in res["supporting_data"]
        assert res["supporting_data"]["pricing_percentiles"]["median"] > 0
        assert res["supporting_data"]["point_forecast_inr"] > 0
        assert res["source"] == "model_and_heuristics"


class TestSimulationEngine:
    def test_festival_simulation(self):
        req = SimulationRunRequest(
            region_id="TN-01",
            category="apparel",
            scenario="festival",
            magnitude=25.0,
        )
        res = simulation_engine.run(req)
        assert res.sim_id is not None
        assert res.delta_percent > 0
        assert res.simulated_forecast > res.baseline_forecast
        assert res.source == "model_simulation"
        assert "festival_uptick_rate" in res.elasticity_factors

        # Verify run retrieval
        retrieved = simulation_engine.get_run(res.sim_id)
        assert retrieved is not None
        assert retrieved.sim_id == res.sim_id

    def test_weather_simulation(self):
        req = SimulationRunRequest(
            region_id="TN-01",
            category="apparel",
            scenario="weather",
            magnitude=5.0,
        )
        res = simulation_engine.run(req)
        assert res.delta_amount != 0
        assert "temp_delta_c" in res.elasticity_factors

    def test_budget_simulation(self):
        req = SimulationRunRequest(
            region_id="MH-01",
            category="footwear",
            scenario="budget",
            magnitude=50.0,
        )
        res = simulation_engine.run(req)
        assert res.simulated_forecast > res.baseline_forecast
        assert "budget_multiplier" in res.elasticity_factors

    def test_inventory_shortfall_simulation(self):
        req = SimulationRunRequest(
            region_id="BR-01",
            category="kitchenware",
            scenario="inventory",
            magnitude=30.0,
        )
        res = simulation_engine.run(req)
        assert res.simulated_forecast < res.baseline_forecast
        assert res.delta_percent < 0
        assert "inventory_shortfall_pct" in res.elasticity_factors
