"""Phase 1 Unit Tests: Data Architecture and Synthetic Dataset Generator.

Verifies:
- Schema and validity of regions.json (15-20 Tier-2/3 Indian regions)
- Schema and validity of segments.json (5 customer personas)
- Schema and validity of festivals.json (festival timings and category upticks)
- Deterministic synthetic sales generation and data integrity
"""

import json
from pathlib import Path
import pandas as pd
import pytest

DATA_DIR = Path(__file__).resolve().parents[1] / "app" / "data"
REGIONS_FILE = DATA_DIR / "regions.json"
SEGMENTS_FILE = DATA_DIR / "segments.json"
FESTIVALS_FILE = DATA_DIR / "festivals.json"
SYNTHETIC_SALES_FILE = DATA_DIR / "synthetic_sales.csv"


def test_regions_json_structure():
    """Verify regions.json contains >= 15 Indian regions with required fields."""
    assert REGIONS_FILE.exists(), "regions.json not found"
    regions = json.loads(REGIONS_FILE.read_text(encoding="utf-8"))
    assert len(regions) >= 15, f"Expected >= 15 regions, found {len(regions)}"

    required_keys = {
        "region_id", "state", "city", "languages",
        "top_categories", "price_sensitivity", "active_festivals",
        "avg_temperature_c", "avg_temp_by_month", "population_tier"
    }

    for region in regions:
        missing = required_keys - set(region.keys())
        assert not missing, f"Region {region.get('region_id')} is missing keys: {missing}"
        assert 0.0 <= region["price_sensitivity"] <= 1.0
        assert len(region["avg_temp_by_month"]) == 12
        assert len(region["languages"]) >= 1
        assert len(region["top_categories"]) >= 1
        assert region["population_tier"] in ["Tier-2", "Tier-3"]


def test_segments_json_structure():
    """Verify segments.json contains 4-6 personas with required fields."""
    assert SEGMENTS_FILE.exists(), "segments.json not found"
    segments = json.loads(SEGMENTS_FILE.read_text(encoding="utf-8"))
    assert 4 <= len(segments) <= 6, f"Expected 4-6 segments, found {len(segments)}"

    required_keys = {
        "segment_id", "label", "age_range", "budget_range",
        "income_bracket", "preferred_categories", "languages",
        "purchase_trigger", "platform_behaviour", "price_sensitivity"
    }

    for seg in segments:
        missing = required_keys - set(seg.keys())
        assert not missing, f"Segment {seg.get('segment_id')} is missing keys: {missing}"
        assert 0.0 <= seg["price_sensitivity"] <= 1.0
        assert len(seg["preferred_categories"]) >= 1


def test_festivals_json_structure():
    """Verify festivals.json contains major festivals and category upticks."""
    assert FESTIVALS_FILE.exists(), "festivals.json not found"
    festivals = json.loads(FESTIVALS_FILE.read_text(encoding="utf-8"))
    assert len(festivals) >= 10, f"Expected >= 10 festivals, found {len(festivals)}"

    for fest in festivals:
        assert "festival" in fest
        assert "approx_date_2026" in fest
        assert "category_upticks" in fest
        assert isinstance(fest["category_upticks"], dict)
        for cat, uptick in fest["category_upticks"].items():
            assert uptick > 0.0, f"Uptick for {cat} in {fest['festival']} should be > 0"


def test_synthetic_sales_data_integrity():
    """Verify generated synthetic_sales.csv has expected columns, positive sales, and realistic distributions."""
    assert SYNTHETIC_SALES_FILE.exists(), "synthetic_sales.csv not found"
    df = pd.read_csv(SYNTHETIC_SALES_FILE)

    required_cols = [
        "date", "region_id", "city", "state", "segment_id",
        "category", "daily_sales", "units_sold", "avg_price",
        "temperature", "is_weekend", "is_festival_week",
        "active_festival", "days_to_next_festival", "stockout_flag"
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing column: {col}"

    assert len(df) > 50000, f"Expected > 50,000 records, found {len(df)}"
    assert (df["daily_sales"] >= 0).all(), "Found negative sales"
    assert (df["units_sold"] >= 1).all(), "Found units_sold < 1"
    assert (df["avg_price"] > 0).all(), "Found avg_price <= 0"

    # Verify festival week boost
    festival_mean = df[df["is_festival_week"] == 1]["units_sold"].mean()
    non_festival_mean = df[df["is_festival_week"] == 0]["units_sold"].mean()
    assert festival_mean > non_festival_mean, (
        f"Festival units mean ({festival_mean:.2f}) should exceed non-festival mean ({non_festival_mean:.2f})"
    )
