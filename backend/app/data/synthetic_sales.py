"""Synthetic Sales Dataset Generator for TwinCart AI.

Generates realistic, reproducible daily retail sales for Indian Tier-2/3
digital twins, incorporating:
- Regional population tiers & baseline demand
- Customer segment purchasing power & affinities
- Weekly day-of-week seasonality (weekend shopping boosts)
- Regional festival surges derived from festivals.json
- Weather & temperature sensitivity (summer cotton wear vs winter wear)
- Price sensitivity elasticities
- Real-world stochastic noise & occasional supply stockouts

Output: backend/app/data/synthetic_sales.csv
"""

import json
import logging
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent
REGIONS_FILE = DATA_DIR / "regions.json"
SEGMENTS_FILE = DATA_DIR / "segments.json"
FESTIVALS_FILE = DATA_DIR / "festivals.json"
OUTPUT_CSV = DATA_DIR / "synthetic_sales.csv"

# Category baseline pricing in INR
CATEGORY_BASE_PRICES = {
    "apparel": 799.0,
    "footwear": 999.0,
    "jewelry (imitation)": 499.0,
    "gold jewelry (imitation)": 699.0,
    "silver jewelry (imitation)": 599.0,
    "home decor": 649.0,
    "home textiles": 549.0,
    "kitchenware": 849.0,
    "electronics accessories": 450.0,
    "mobile accessories": 299.0,
    "beauty": 399.0,
    "monsoon apparel": 899.0,
}

# Base units per segment per day for Tier-2 market
SEGMENT_AFFINITY_WEIGHTS = {
    "students": {
        "apparel": 1.4,
        "footwear": 1.2,
        "mobile accessories": 2.2,
        "electronics accessories": 1.5,
        "beauty": 1.3,
        "jewelry (imitation)": 0.9,
        "home decor": 0.4,
        "home textiles": 0.3,
        "kitchenware": 0.2,
    },
    "working_professionals": {
        "apparel": 1.6,
        "footwear": 1.5,
        "electronics accessories": 1.8,
        "beauty": 1.4,
        "jewelry (imitation)": 1.2,
        "gold jewelry (imitation)": 1.3,
        "home decor": 1.1,
        "home textiles": 0.9,
        "kitchenware": 0.8,
    },
    "homemakers": {
        "kitchenware": 2.2,
        "home textiles": 2.0,
        "home decor": 1.8,
        "apparel": 1.5,
        "jewelry (imitation)": 1.4,
        "silver jewelry (imitation)": 1.6,
        "gold jewelry (imitation)": 1.5,
        "beauty": 0.8,
        "mobile accessories": 0.5,
    },
    "budget_shoppers": {
        "apparel": 1.3,
        "footwear": 1.2,
        "mobile accessories": 1.6,
        "kitchenware": 1.2,
        "home textiles": 1.1,
        "home decor": 0.6,
        "beauty": 0.7,
        "electronics accessories": 0.8,
    },
    "young_parents": {
        "apparel": 2.0,
        "footwear": 1.4,
        "home textiles": 1.6,
        "beauty": 1.1,
        "kitchenware": 1.3,
        "home decor": 1.0,
        "electronics accessories": 0.9,
        "mobile accessories": 0.9,
    },
}


def load_seed_data():
    """Load regional, segment, and festival configuration files."""
    with open(REGIONS_FILE, "r", encoding="utf-8") as f:
        regions = json.load(f)
    with open(SEGMENTS_FILE, "r", encoding="utf-8") as f:
        segments = json.load(f)
    with open(FESTIVALS_FILE, "r", encoding="utf-8") as f:
        festivals = json.load(f)
    return regions, segments, festivals


def generate_synthetic_sales(
    start_date: str = "2023-01-01",
    end_date: str = "2025-12-31",
    seed: int = 42,
    output_path: Optional[Path] = OUTPUT_CSV,
) -> pd.DataFrame:
    """Generate synthetic sales time-series dataset.

    Args:
        start_date: ISO format start date (YYYY-MM-DD)
        end_date: ISO format end date (YYYY-MM-DD)
        seed: Random seed for 100% reproducible data
        output_path: Path to save the resulting CSV file

    Returns:
        pd.DataFrame containing the generated sales data
    """
    np.random.seed(seed)
    regions, segments, festivals = load_seed_data()

    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    logger.info("Generating synthetic sales from %s to %s (%d days)...", start_date, end_date, len(dates))

    records: List[Dict[str, Any]] = []

    # Pre-parse festival dates across each year in range
    years_in_range = sorted(list({d.year for d in dates}))
    festival_lookup = []

    for year in years_in_range:
        for fest in festivals:
            month = fest.get("month", 10)
            day = fest.get("day", 15)
            try:
                fest_date = date(year, month, min(day, 28))
            except ValueError:
                fest_date = date(year, month, 28)

            festival_lookup.append({
                "festival": fest["festival"],
                "date": fest_date,
                "regions": fest.get("region", ["All India"]),
                "upticks": fest.get("category_upticks", {}),
            })

    for r in regions:
        r_id = r["region_id"]
        state = r["state"]
        city = r.get("city", f"{state} Hub")
        pop_tier = r.get("population_tier", "Tier-2")
        tier_multiplier = 1.3 if pop_tier == "Tier-2" else 0.9
        monthly_temps = r.get("avg_temp_by_month", [27.0] * 12)
        top_cats = r["top_categories"]

        # Filter segments active in this region
        active_segments = [s for s in segments if r_id in s.get("region_ids", []) or not s.get("region_ids")]
        if not active_segments:
            active_segments = segments

        for cur_dt in dates:
            d_obj = cur_dt.date()
            month_idx = cur_dt.month - 1
            day_of_week = cur_dt.dayofweek  # 0=Monday, 6=Sunday
            is_weekend = int(day_of_week in [4, 5, 6])  # Fri-Sun retail peak
            weekend_boost = 1.25 if is_weekend else 1.0

            # Base regional temperature for this month with realistic daily variation
            base_temp = monthly_temps[month_idx]
            day_temp = round(base_temp + np.random.normal(0, 1.5), 1)

            # Check festival proximity
            is_festival_week = 0
            active_festival_name = "None"
            active_upticks: Dict[str, float] = {}
            min_days_to_fest = 999

            for fest in festival_lookup:
                is_relevant_region = ("All India" in fest["regions"]) or (r_id in fest["regions"])
                if not is_relevant_region:
                    continue

                diff = (fest["date"] - d_obj).days
                if abs(diff) < abs(min_days_to_fest):
                    min_days_to_fest = diff

                # Peak window: 7 days before festival to 1 day after
                if -1 <= diff <= 7:
                    is_festival_week = 1
                    active_festival_name = fest["festival"]
                    active_upticks = fest["upticks"]

            # Generate row per active segment and top categories
            for seg in active_segments:
                seg_id = seg["segment_id"]
                price_sens = seg.get("price_sensitivity", 0.7)
                affinities = SEGMENT_AFFINITY_WEIGHTS.get(seg_id, {})

                for cat in top_cats:
                    cat_base_price = CATEGORY_BASE_PRICES.get(cat, 599.0)
                    affinity = affinities.get(cat, 1.0)

                    # 1. Base unit volume
                    base_units = 18.0 * tier_multiplier * affinity

                    # 2. Seasonality & Day of week
                    units = base_units * weekend_boost

                    # 3. Weather correlation
                    if cat in ["apparel", "monsoon apparel", "home textiles"]:
                        if day_temp > 30.0:
                            # Hot weather promotes breathable cotton apparel
                            units *= 1.18
                        elif day_temp < 20.0:
                            # Cool weather boosts heavier apparel
                            units *= 1.22

                    # 4. Festival surge multiplier
                    if is_festival_week and cat in active_upticks:
                        surge = active_upticks[cat]
                        units *= (1.0 + surge)

                    # 5. Price discount / sensitivity effect
                    effective_price = cat_base_price
                    if is_festival_week or is_weekend:
                        discount = 0.12 * price_sens
                        effective_price = round(cat_base_price * (1.0 - discount), 2)
                        units *= (1.0 + discount * 1.4)  # Price elasticity demand boost

                    # 6. Occasional stockout dip (3% chance)
                    stockout_flag = int(np.random.random() < 0.03)
                    if stockout_flag:
                        units *= np.random.uniform(0.3, 0.6)

                    # 7. Stochastic noise
                    noise = np.random.normal(1.0, 0.08)
                    final_units = max(1, int(round(units * noise)))
                    total_sales = round(final_units * effective_price, 2)

                    records.append({
                        "date": cur_dt.strftime("%Y-%m-%d"),
                        "region_id": r_id,
                        "city": city,
                        "state": state,
                        "population_tier": pop_tier,
                        "segment_id": seg_id,
                        "category": cat,
                        "daily_sales": total_sales,
                        "units_sold": final_units,
                        "avg_price": effective_price,
                        "temperature": day_temp,
                        "is_weekend": is_weekend,
                        "is_festival_week": is_festival_week,
                        "active_festival": active_festival_name,
                        "days_to_next_festival": min_days_to_fest,
                        "stockout_flag": stockout_flag,
                    })

    df = pd.DataFrame(records)
    logger.info("Generated %d synthetic sales records.", len(df))

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        logger.info("Saved dataset to %s (Size: %.2f MB)", output_path, output_path.stat().st_size / (1024 * 1024))

    return df


if __name__ == "__main__":
    generate_synthetic_sales()
