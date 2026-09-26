"""Weather & Festival Intelligence Agent.

Queries Open-Meteo (no API key required) for current weather at the
region's representative coordinates, then combines that with the
festivals.json calendar to produce a single weather_signal string that
the downstream Demand Forecasting and Campaign Generator agents consume.
"""
import json
import logging
from datetime import date
from pathlib import Path

import httpx

from app.graph.state import TwinAIState
from app.twins.regional_twin import regional_twin_store
from app.core.exceptions import AgentExecutionError

logger = logging.getLogger(__name__)

# Representative lat/lon for each region_id (centre of state capital)
_REGION_COORDS: dict[str, tuple[float, float]] = {
    "TN-01": (13.08, 80.27),   # Chennai
    "BR-01": (25.60, 85.10),   # Patna
    "KL-01": (8.89, 76.61),    # Thiruvananthapuram
    "UP-01": (26.85, 80.95),   # Lucknow
    "MH-01": (19.08, 72.88),   # Mumbai
    "WB-01": (22.57, 88.36),   # Kolkata
    "RJ-01": (26.92, 75.79),   # Jaipur
    "GJ-01": (23.02, 72.57),   # Ahmedabad
    "PB-01": (30.73, 76.78),   # Chandigarh
    "AP-01": (13.68, 79.42),   # Amaravati
    "TS-01": (17.38, 78.49),   # Hyderabad
    "KA-01": (12.97, 77.59),   # Bengaluru
    "MP-01": (23.25, 77.41),   # Bhopal
    "OD-01": (20.27, 85.84),   # Bhubaneswar
    "AS-01": (26.14, 91.74),   # Guwahati
}

_FESTIVALS_PATH = Path(__file__).resolve().parents[1] / "data" / "festivals.json"
_festivals_cache: list[dict] | None = None


def _load_festivals() -> list[dict]:
    global _festivals_cache
    if _festivals_cache is None:
        _festivals_cache = json.loads(_FESTIVALS_PATH.read_text(encoding="utf-8"))
    return _festivals_cache


def _upcoming_festivals(region_id: str, within_days: int = 21) -> list[str]:
    """Return festival names applicable to this region within the next N days."""
    today = date.today()
    upcoming = []
    for f in _load_festivals():
        regions = f.get("region", [])
        if region_id not in regions and "All India" not in regions:
            continue
        try:
            fdate = date.fromisoformat(f["approx_date_2026"])
        except (KeyError, ValueError):
            continue
        delta = (fdate - today).days
        if 0 <= delta <= within_days:
            upcoming.append(f["festival"])
    return upcoming


def _fetch_weather(lat: float, lon: float) -> dict:
    """Fetch current weather from Open-Meteo (no API key, free tier)."""
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,precipitation,weather_code"
        f"&forecast_days=1"
    )
    try:
        resp = httpx.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json().get("current", {})
    except Exception as exc:
        logger.warning("[weather_festival] Open-Meteo call failed: %s", exc)
        return {}


def run(state: TwinAIState) -> dict:
    """LangGraph node: build a weather+festival signal string."""
    region_id = state["region_id"]
    try:
        twin = regional_twin_store.get(region_id)
        coords = _REGION_COORDS.get(region_id, (20.59, 78.96))  # India centroid fallback
        weather = _fetch_weather(*coords)
        festivals = _upcoming_festivals(region_id)

        temp = weather.get("temperature_2m", twin.avg_temperature_c)
        precip = weather.get("precipitation", 0)

        parts = [f"Temp {temp}°C, Precip {precip}mm"]
        if festivals:
            parts.append(f"Upcoming festivals: {', '.join(festivals)}")
        else:
            parts.append("No major festivals in the next 3 weeks")

        signal = " | ".join(parts)
        logger.info("[weather_festival] %s → %s", region_id, signal)
        return {
            "weather_signal": signal,
            "explanation_log": [f"Weather & Festival ({region_id}): {signal}"],
        }
    except Exception as exc:
        logger.error("[weather_festival] failed for %s: %s", region_id, exc)
        raise AgentExecutionError("weather_festival", str(exc)) from exc
