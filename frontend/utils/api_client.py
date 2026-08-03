"""Thin wrapper around the TwinCart AI FastAPI backend.

All frontend pages import from here so the base URL is configured in
one place via the TwinCart AI_API_URL environment variable (defaults to
http://localhost:8000/api for local development).
"""
import os
import requests

BASE_URL = os.getenv("TwinCart AI_API_URL", "http://localhost:8000/api")
_TIMEOUT = 90  # seconds — LLM calls can take a moment on free tier


# ── Digital Twins ─────────────────────────────────────────────────────────────

def list_regions() -> list[dict]:
    """Return all regional digital twins."""
    resp = requests.get(f"{BASE_URL}/twins/regions", timeout=_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def get_region(region_id: str) -> dict:
    resp = requests.get(f"{BASE_URL}/twins/regions/{region_id}", timeout=_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def list_segments() -> list[dict]:
    """Return all customer segment twins."""
    resp = requests.get(f"{BASE_URL}/twins/segments", timeout=_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def get_segment(segment_id: str) -> dict:
    resp = requests.get(f"{BASE_URL}/twins/segments/{segment_id}", timeout=_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


# ── Campaigns ─────────────────────────────────────────────────────────────────

def generate_campaign(region_id: str, segment_id: str | None = None) -> dict:
    """Run the full TwinCart AI agent pipeline and return campaign results."""
    resp = requests.post(
        f"{BASE_URL}/campaigns/generate",
        json={"region_id": region_id, "segment_id": segment_id},
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


# ── Sellers ───────────────────────────────────────────────────────────────────

def ask_seller_agent(
    question: str,
    region_id: str | None = None,
    segment_id: str | None = None,
) -> dict:
    resp = requests.post(
        f"{BASE_URL}/sellers/ask",
        json={"question": question, "region_id": region_id, "segment_id": segment_id},
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


# ── Simulation ────────────────────────────────────────────────────────────────

def run_simulation(
    region_id: str,
    festival_next_week: bool = False,
    temperature_delta_c: float = 0.0,
    budget_multiplier: float = 1.0,
    inventory_shortfall_pct: float = 0.0,
) -> dict:
    resp = requests.post(
        f"{BASE_URL}/simulation/run",
        json={
            "region_id": region_id,
            "festival_next_week": festival_next_week,
            "temperature_delta_c": temperature_delta_c,
            "budget_multiplier": budget_multiplier,
            "inventory_shortfall_pct": inventory_shortfall_pct,
        },
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


# ── Health ────────────────────────────────────────────────────────────────────

def health_check() -> dict:
    resp = requests.get(f"{BASE_URL.replace('/api', '')}/health", timeout=10)
    resp.raise_for_status()
    return resp.json()
