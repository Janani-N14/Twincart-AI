"""Budget Optimization Agent for TwinCart AI.

Implements mathematical constrained allocation (linear programming / proportional ROI optimization)
across marketing channels and regional hubs, rather than LLM guesswork.

Channel Efficiency Coefficients:
- WhatsApp Channels: High conversion in Tier-2/3, low CAC
- Regional Social / Reels: High engagement for Gen-Z / students
- Search Ads: High intent, moderate cost
- In-App Push: Zero marginal cost, high retargeting conversion
- Micro-Influencers: High trust for apparel/jewelry

Solves: Maximize Expected ROI subject to sum(weights) = 1.0 and minimum channel floors.
"""

import logging
from typing import Any, Dict

import numpy as np
from scipy.optimize import linprog

from app.graph.state import TwinAIState
from app.twins.regional_twin import regional_twin_store
from app.twins.segment_twin import segment_twin_store

logger = logging.getLogger(__name__)

CHANNELS = ["social_reels", "whatsapp_community", "search_ads", "in_app_push", "regional_influencers"]

# Base expected ROI multiplier per channel (₹ return per ₹1 spent)
BASE_CHANNEL_ROI = {
    "social_reels": 3.4,
    "whatsapp_community": 4.2,
    "search_ads": 2.8,
    "in_app_push": 4.8,
    "regional_influencers": 3.1,
}


def optimize_channel_allocation(
    price_sensitivity: float = 0.65,
    is_festival: bool = True,
    segment_id: str = "students",
    total_budget_inr: float = 50000.0,
) -> Dict[str, Any]:
    """Solve constrained linear optimization for marketing budget allocation."""
    # Adjust expected ROI per channel based on audience and festival context
    roi_scores = BASE_CHANNEL_ROI.copy()

    if segment_id == "students":
        roi_scores["social_reels"] *= 1.35
        roi_scores["in_app_push"] *= 1.20
    elif segment_id == "homemakers":
        roi_scores["whatsapp_community"] *= 1.40
        roi_scores["regional_influencers"] *= 1.25
    elif segment_id == "budget_shoppers":
        roi_scores["whatsapp_community"] *= 1.30
        roi_scores["in_app_push"] *= 1.35

    if is_festival:
        roi_scores["social_reels"] *= 1.25
        roi_scores["whatsapp_community"] *= 1.20

    # Sensitivity penalty: high price sensitivity favors direct low-CAC channels (WhatsApp, push)
    if price_sensitivity > 0.7:
        roi_scores["whatsapp_community"] *= 1.2
        roi_scores["in_app_push"] *= 1.2
        roi_scores["search_ads"] *= 0.85

    # Linear program to maximize sum(roi_i * w_i) subject to:
    # 1. sum(w_i) = 1.0
    # 2. 0.08 <= w_i <= 0.45 (diversification bounds)
    c = [-roi_scores[ch] for ch in CHANNELS]  # minimize negative ROI
    A_eq = [[1.0] * len(CHANNELS)]
    b_eq = [1.0]
    bounds = [(0.08, 0.45) for _ in CHANNELS]

    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")

    if res.success:
        weights = res.x
    else:
        # Fallback proportional softmax
        exp_roi = np.exp([roi_scores[ch] for ch in CHANNELS])
        weights = exp_roi / np.sum(exp_roi)

    allocation_pct = {ch: round(float(w), 3) for ch, w in zip(CHANNELS, weights)}
    allocation_inr = {ch: round(float(w * total_budget_inr), 2) for ch, w in zip(CHANNELS, weights)}
    expected_blended_roi = round(sum(roi_scores[ch] * w for ch, w in zip(CHANNELS, weights)), 2)

    return {
        "channel_shares": allocation_pct,
        "channel_amounts_inr": allocation_inr,
        "total_budget_inr": total_budget_inr,
        "expected_blended_roi": expected_blended_roi,
        "optimization_method": "Highs Linear Programming (Constrained ROI Maximization)",
        "source": "heuristic_optimization",
    }


def run(state: TwinAIState) -> dict:
    """LangGraph node: optimize budget allocation."""
    region_id = state.get("region_id", "TN-01")
    twin = regional_twin_store.get(region_id)
    segment_id = state.get("segment_id", "students")
    total_budget = float(state.get("total_budget_inr", 50000.0))
    is_fest = bool(twin.active_festivals)

    result = optimize_channel_allocation(
        price_sensitivity=twin.price_sensitivity,
        is_festival=is_fest,
        segment_id=segment_id,
        total_budget_inr=total_budget,
    )

    top_ch = max(result["channel_shares"], key=result["channel_shares"].get)

    logger.info("[budget_optimizer] %s → Top channel %s (%s)", region_id, top_ch, result["channel_shares"][top_ch])

    return {
        "budget_allocation": result["channel_shares"],
        "budget_amounts_inr": result["channel_amounts_inr"],
        "budget_optimization_result": result,
        "explanation_log": [
            f"Budget Optimization ({region_id}): Optimal allocation allocates {result['channel_shares'][top_ch]:.1%} "
            f"(₹{result['channel_amounts_inr'][top_ch]:,.2f}) to {top_ch.replace('_', ' ').title()} "
            f"with projected {result['expected_blended_roi']}x blended ROI."
        ],
    }
