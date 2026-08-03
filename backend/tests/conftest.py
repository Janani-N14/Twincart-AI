"""Shared pytest fixtures for TwinCart AI backend tests."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from app.main import app
from app.graph.state import TwinAIState


@pytest.fixture(scope="session")
def client():
    """Synchronous FastAPI TestClient — no live LLM calls needed for router tests."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_state() -> TwinAIState:
    """A minimal TwinAIState populated with realistic values for unit tests."""
    return TwinAIState(
        region_id="TN-01",
        segment_id=None,
        trends=["cotton kurtas", "LED diyas", "steel water bottles"],
        demand_forecast={"apparel": 85.0, "kitchenware": 62.0, "home textiles": 55.0},
        campaign_copy=[
            "Celebrate Pongal with fresh cotton kurtas — shop now!",
            "Light up your home this festival season with LED diyas.",
        ],
        banner_briefs=[
            "Festival Fashion | Kurtas from ₹299 | Shop Now | Warm yellows, ethnic motifs",
        ],
        budget_allocation={
            "social_media": 0.35,
            "search_ads": 0.25,
            "push_notifications": 0.20,
            "email": 0.12,
            "influencer": 0.08,
        },
        catalog_gaps=["ethnic footwear", "brass puja items"],
        weather_signal="Temp 29.5°C, Precip 0mm | Upcoming festivals: Pongal",
        simulation_result=None,
        explanation_log=["Trend Detection (TN-01): cotton kurtas, LED diyas"],
    )


@pytest.fixture
def mock_pipeline_result(sample_state) -> TwinAIState:
    """Alias — used when patching the orchestrator in router tests."""
    return sample_state
