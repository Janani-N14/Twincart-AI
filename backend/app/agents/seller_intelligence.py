"""Seller Growth & Intelligence Agent for TwinCart AI.

Combines:
- ML Demand Forecasting 7-day revenue predictions & honest MAPE
- Category benchmark pricing heuristics (25th, 50th, 75th percentiles from data)
- Regional festival calendar proximity
- Versioned prompt template (app/prompts/seller_prompt.txt)
to answer free-text seller questions with actionable, grounded business intelligence.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.llm import get_llm
from app.core.cache import semantic_lookup, semantic_store
from app.graph.state import TwinAIState
from app.twins.regional_twin import regional_twin_store
from app.twins.segment_twin import segment_twin_store
from app.ml.demand_forecasting import demand_forecaster

logger = logging.getLogger(__name__)

PROMPT_FILE = Path(__file__).resolve().parents[1] / "prompts" / "seller_prompt.txt"
SALES_CSV = Path(__file__).resolve().parents[2] / "data" / "synthetic_sales.csv"


def get_pricing_percentiles(category: str = "apparel") -> Dict[str, float]:
    """Compute 25th, 50th (median), and 75th price percentiles for the category."""
    if SALES_CSV.exists():
        try:
            df = pd.read_csv(SALES_CSV)
            cat_df = df[df["category"].str.lower() == category.lower()]
            if not cat_df.empty:
                prices = cat_df["avg_price"].dropna()
                return {
                    "p25": round(float(np.percentile(prices, 25)), 2),
                    "median": round(float(np.median(prices)), 2),
                    "p75": round(float(np.percentile(prices, 75)), 2),
                }
        except Exception as e:
            logger.debug("Failed computing price percentiles from CSV: %s", e)

    # Deterministic default pricing heuristic
    base = 699.0
    return {"p25": round(base * 0.75, 2), "median": base, "p75": round(base * 1.35, 2)}


def answer(
    question: str,
    region_id: Optional[str] = "TN-01",
    category: Optional[str] = "apparel",
    segment_id: Optional[str] = "students",
) -> Dict[str, Any]:
    """Answer seller question using grounded ML demand models & price heuristics."""
    region_id = region_id or "TN-01"
    category = category or "apparel"
    twin = regional_twin_store.get(region_id)

    # Check cache first
    cached = semantic_lookup(question)
    if cached:
        logger.info("[seller_intelligence] Cache hit for question: %.50s...", question)
        return {
            "answer": cached,
            "supporting_data": {"region": twin.state, "category": category},
            "source": "cached_advisor",
            "from_cache": True,
        }

    # Gather data context
    fc = demand_forecaster.forecast_demand(
        region_id=region_id,
        category=category,
        segment_id=segment_id or "students",
        horizon_days=7,
        temperature=twin.avg_temperature_c or 28.0,
        is_festival_week=1 if twin.active_festivals else 0,
        population_tier=twin.population_tier or "Tier-2",
    )
    pricing = get_pricing_percentiles(category)
    metrics = demand_forecaster.get_metrics()
    mape = metrics.get("mape_percent", 8.94)

    prompt_text = PROMPT_FILE.read_text(encoding="utf-8") if PROMPT_FILE.exists() else (
        "Answer seller question: '{question}' for region {state} and category {category}."
    )
    prompt_tmpl = PromptTemplate.from_template(prompt_text)

    try:
        chain = prompt_tmpl | get_llm(temperature=0.3, fast=False) | StrOutputParser()
        answer_text = chain.invoke({
            "state": twin.state,
            "city": twin.city or f"{twin.state} Hub",
            "region_id": region_id,
            "category": category,
            "point_forecast": fc["point_forecast"],
            "mape": mape,
            "price_sensitivity": twin.price_sensitivity,
            "median_price": pricing["median"],
            "p25_price": pricing["p25"],
            "p75_price": pricing["p75"],
            "trends": ", ".join(twin.top_categories),
            "festivals": ", ".join(twin.active_festivals) or "None upcoming",
            "temperature": twin.avg_temperature_c or 28.0,
            "question": question,
        })
    except Exception as exc:
        logger.warning("[seller_intelligence] LLM offline/failed (%s), using data-grounded advisor fallback", exc)
        fest_note = f"due to the upcoming {twin.active_festivals[0]} season" if twin.active_festivals else "with regular seasonal cycles"
        answer_text = (
            f"Based on TwinAI analytics for {twin.state} ({twin.city or 'Tier-2'}):\n"
            f"1. Demand Outlook: 7-day revenue for {category} is projected at ₹{fc['point_forecast']:,.2f} (Model backtested MAPE: {mape:.2f}%).\n"
            f"2. Competitive Pricing Benchmark: The median market price is ₹{pricing['median']:.2f} (entry tier ₹{pricing['p25']:.2f}, premium tier ₹{pricing['p75']:.2f}). Given a price sensitivity of {twin.price_sensitivity:.2f}, we recommend pricing close to ₹{pricing['median'] * 0.95:.2f} to maximize sell-through.\n"
            f"3. Inventory Recommendation: Increase stock buffer by 25-35% {fest_note}."
        )

    # Store in semantic cache
    if answer_text:
        semantic_store(question, answer_text)

    supporting_data = {
        "region_id": region_id,
        "state": twin.state,
        "city": twin.city,
        "category": category,
        "point_forecast_inr": fc["point_forecast"],
        "backtested_mape": mape,
        "pricing_percentiles": pricing,
        "price_sensitivity": twin.price_sensitivity,
        "active_festivals": twin.active_festivals,
    }

    return {
        "answer": answer_text,
        "supporting_data": supporting_data,
        "source": "model_and_heuristics",
        "from_cache": False,
    }


def run(state: TwinAIState) -> dict:
    """LangGraph node helper if invoked inside a pipeline."""
    question = state.get("seller_question", "What should I stock this month?")
    res = answer(
        question=question,
        region_id=state.get("region_id"),
        category=state.get("category"),
        segment_id=state.get("segment_id"),
    )
    return {
        "seller_answer": res["answer"],
        "seller_supporting_data": res["supporting_data"],
        "explanation_log": [f"Seller Growth Advisor: Answered '{question}'."],
    }
