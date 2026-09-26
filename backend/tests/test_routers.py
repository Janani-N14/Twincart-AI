"""Integration tests for FastAPI routers.

The orchestrator (LangGraph pipeline) is patched so no live LLM calls
are made during CI.  The simulation and twins endpoints are tested against
real logic (deterministic, no LLM dependency).
"""
import pytest
from unittest.mock import AsyncMock, patch

from app.graph.state import TwinAIState


# ── Helpers ───────────────────────────────────────────────────────────────────

def _mock_state() -> TwinAIState:
    return TwinAIState(
        region_id="TN-01",
        segment_id=None,
        trends=["cotton kurtas", "LED diyas"],
        demand_forecast={"apparel": 85.0, "kitchenware": 62.0},
        campaign_copy=["Shop the Aadi Sale!", "Pongal specials await."],
        banner_briefs=["Festival Fashion | Kurtas | Shop Now | Yellow tones"],
        budget_allocation={"social_media": 0.4, "search_ads": 0.3, "push_notifications": 0.2, "email": 0.07, "influencer": 0.03},
        catalog_gaps=["ethnic footwear"],
        weather_signal="Temp 29°C | Upcoming: Pongal",
        simulation_result=None,
        explanation_log=["Trend Detection (TN-01): cotton kurtas, LED diyas", "Summary generated."],
    )


# ── Health check ──────────────────────────────────────────────────────────────

def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# ── Twins router ──────────────────────────────────────────────────────────────

def test_list_regions(client):
    resp = client.get("/api/twins/regions")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 15


def test_get_known_region(client):
    resp = client.get("/api/twins/regions/TN-01")
    assert resp.status_code == 200
    assert resp.json()["state"] == "Tamil Nadu"


def test_get_unknown_region_returns_404(client):
    resp = client.get("/api/twins/regions/XX-99")
    assert resp.status_code == 404


def test_list_segments(client):
    resp = client.get("/api/twins/segments")
    assert resp.status_code == 200
    assert len(resp.json()) == 4


def test_get_segment(client):
    resp = client.get("/api/twins/segments/students")
    assert resp.status_code == 200
    assert resp.json()["label"] == "Students"


def test_get_unknown_segment_returns_404(client):
    resp = client.get("/api/twins/segments/unicorn")
    assert resp.status_code == 404


# ── Simulation router ─────────────────────────────────────────────────────────

def test_simulation_baseline(client):
    resp = client.post("/api/simulation/run", json={"region_id": "TN-01"})
    assert resp.status_code == 200
    data = resp.json()
    assert 0.0 <= data["predicted_conversion_rate"] <= 1.0
    assert "interpretation" in data


def test_simulation_festival_boost(client):
    base = client.post("/api/simulation/run", json={"region_id": "TN-01"}).json()
    boosted = client.post("/api/simulation/run", json={
        "region_id": "TN-01", "festival_next_week": True
    }).json()
    assert boosted["predicted_conversion_rate"] > base["predicted_conversion_rate"]


def test_simulation_unknown_region(client):
    resp = client.post("/api/simulation/run", json={"region_id": "XX-99"})
    assert resp.status_code == 404


# ── Campaigns router (orchestrator mocked) ────────────────────────────────────

def test_generate_campaign(client):
    mock_state = _mock_state()
    with patch(
        "app.routers.campaigns.run_campaign_pipeline",
        new=AsyncMock(return_value=mock_state),
    ):
        resp = client.post(
            "/api/campaigns/generate",
            json={"region_id": "TN-01", "segment_id": None},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["region_id"] == "TN-01"
    assert len(data["trends"]) > 0
    assert len(data["campaign_copy"]) > 0
    assert isinstance(data["budget_allocation"], dict)


def test_generate_campaign_missing_region(client):
    with patch(
        "app.routers.campaigns.run_campaign_pipeline",
        new=AsyncMock(side_effect=Exception("Region not found")),
    ):
        resp = client.post(
            "/api/campaigns/generate",
            json={"region_id": "XX-99"},
        )
    assert resp.status_code == 502


# ── Sellers router (agent mocked) ─────────────────────────────────────────────

def test_ask_seller_agent(client):
    fake_answer = {
        "answer": "Stock up on ethnic wear and puja essentials before Diwali.",
        "supporting_data": {"top_category": "apparel"},
        "confidence": "high",
        "from_cache": False,
    }
    with patch("app.routers.sellers.seller_intelligence.answer", return_value=fake_answer):
        resp = client.post(
            "/api/sellers/ask",
            json={"question": "What should I stock before Diwali?", "region_id": "TN-01"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert data["confidence"] == "high"


def test_ask_seller_agent_short_question(client):
    """Questions under 5 chars should fail Pydantic validation."""
    resp = client.post(
        "/api/sellers/ask",
        json={"question": "Hi"},
    )
    assert resp.status_code == 422
