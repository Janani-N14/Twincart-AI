"""Phase 4 Integration Tests: FastAPI Routers & Endpoints.

Tests verify all required MVP endpoints:
- GET  /health
- GET  /api/twins/regions
- GET  /api/twins/regions/{id}
- GET  /api/twins/segments
- GET  /api/twins/segments/{id}
- POST /api/campaigns/generate (with source attribution fields)
- GET  /api/campaigns/{campaign_id}
- POST /api/simulation/run (with explicit elasticity multipliers)
- GET  /api/simulation/{sim_id}
- POST /api/sellers/ask (with benchmark percentiles)
- GET  /api/training/metrics
"""

import pytest


# ── Health check ──────────────────────────────────────────────────────────────

def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


# ── Regional Twins ────────────────────────────────────────────────────────────

def test_list_regions(client):
    resp = client.get("/api/twins/regions")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 15
    first = data[0]
    assert "region_id" in first
    assert "state" in first
    assert "city" in first
    assert "avg_temp_by_month" in first
    assert "price_sensitivity" in first


def test_get_known_region(client):
    resp = client.get("/api/twins/regions/TN-01")
    assert resp.status_code == 200
    data = resp.json()
    assert data["region_id"] == "TN-01"
    assert data["state"] == "Tamil Nadu"
    assert data["city"] == "Madurai"


def test_get_unknown_region_returns_404(client):
    resp = client.get("/api/twins/regions/XX-99")
    assert resp.status_code == 404


# ── Segment Twins ─────────────────────────────────────────────────────────────

def test_list_segments(client):
    resp = client.get("/api/twins/segments")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 4
    ids = [s["segment_id"] for s in data]
    assert "students" in ids
    assert "working_professionals" in ids


def test_get_known_segment(client):
    resp = client.get("/api/twins/segments/students")
    assert resp.status_code == 200
    data = resp.json()
    assert data["segment_id"] == "students"
    assert "preferred_categories" in data
    assert "price_sensitivity" in data


def test_get_unknown_segment_returns_404(client):
    resp = client.get("/api/twins/segments/unknown_segment_xyz")
    assert resp.status_code == 404


# ── Simulation Engine ─────────────────────────────────────────────────────────

def test_simulation_festival_scenario(client):
    payload = {
        "region_id": "TN-01",
        "category": "apparel",
        "scenario": "festival",
        "magnitude": 40.0,
    }
    resp = client.post("/api/simulation/run", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["region_id"] == "TN-01"
    assert data["category"] == "apparel"
    assert data["sim_id"].startswith("sim_")
    assert data["baseline_forecast"] > 0
    assert data["simulated_forecast"] > data["baseline_forecast"]
    assert data["delta_percent"] > 0
    assert "elasticity_factors" in data
    assert "interpretation" in data
    assert data["source"] == "model_simulation"


def test_simulation_weather_scenario(client):
    payload = {
        "region_id": "PB-01",
        "category": "apparel",
        "scenario": "weather",
        "magnitude": 5.0,
    }
    resp = client.post("/api/simulation/run", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["sim_id"].startswith("sim_")
    assert data["simulated_forecast"] > 0
    assert "elasticity_factors" in data


def test_get_simulation_run_by_id(client):
    run_resp = client.post("/api/simulation/run", json={
        "region_id": "KA-01",
        "category": "ethnic_wear",
        "scenario": "budget",
        "magnitude": 25.0,
    })
    assert run_resp.status_code == 200
    sim_id = run_resp.json()["sim_id"]

    get_resp = client.get(f"/api/simulation/{sim_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["sim_id"] == sim_id


def test_get_unknown_simulation_returns_404(client):
    resp = client.get("/api/simulation/sim_nonexistent123")
    assert resp.status_code == 404


def test_simulation_unknown_region(client):
    resp = client.post("/api/simulation/run", json={
        "region_id": "XX-99",
        "category": "apparel",
        "scenario": "festival",
        "magnitude": 30.0,
    })
    assert resp.status_code == 404


# ── Campaign Generation ───────────────────────────────────────────────────────

def test_generate_campaign(client):
    payload = {
        "region_id": "TN-01",
        "segment_id": "students",
        "category": "apparel",
        "total_budget_inr": 100000.0,
    }
    resp = client.post("/api/campaigns/generate", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["campaign_id"].startswith("cmp_")
    assert data["region_id"] == "TN-01"
    assert data["category"] == "apparel"
    assert len(data["campaign_copy"]) > 0
    assert "budget_allocation" in data
    assert "point_forecast" in data
    assert "uncertainty_std" in data
    assert "backtested_mape" in data
    assert "sources" in data
    assert data["sources"]["point_forecast"] == "model"


def test_get_campaign_by_id(client):
    gen_resp = client.post("/api/campaigns/generate", json={
        "region_id": "MH-01",
        "category": "beauty",
        "total_budget_inr": 50000.0,
    })
    assert gen_resp.status_code == 200
    cid = gen_resp.json()["campaign_id"]

    get_resp = client.get(f"/api/campaigns/{cid}")
    assert get_resp.status_code == 200
    assert get_resp.json()["campaign_id"] == cid


def test_get_unknown_campaign_returns_404(client):
    resp = client.get("/api/campaigns/cmp_unknown999")
    assert resp.status_code == 404


# ── Seller Intelligence ───────────────────────────────────────────────────────

def test_ask_seller_agent(client):
    payload = {
        "question": "What is the demand forecast and pricing strategy for kurtas in Madurai?",
        "region_id": "TN-01",
        "category": "apparel",
    }
    resp = client.post("/api/sellers/ask", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert "answer" in data
    assert len(data["answer"]) > 10
    assert "supporting_data" in data
    assert "sources" in data
    assert data["sources"]["pricing_benchmark"] == "heuristic"
    assert data["sources"]["point_forecast"] == "model"


def test_ask_seller_agent_short_question_fails_validation(client):
    resp = client.post(
        "/api/sellers/ask",
        json={"question": "Hi", "region_id": "TN-01"},
    )
    assert resp.status_code == 422


# ── Training & ML Metrics ─────────────────────────────────────────────────────

def test_get_training_metrics(client):
    resp = client.get("/api/training/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "mape_percent" in data
    assert "r2_score" in data
    assert data["mape_percent"] < 35.0
