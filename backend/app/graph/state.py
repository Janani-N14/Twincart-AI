"""Shared LangGraph state for the TwinAI agent pipeline."""

import operator
from typing import Annotated, Any, Dict, List, Optional, TypedDict


class TwinAIState(TypedDict, total=False):
    # --- Inputs -------------------------------------------------------
    region_id: str
    segment_id: Optional[str]
    category: Optional[str]
    total_budget_inr: Optional[float]
    horizon_days: Optional[int]
    seller_question: Optional[str]

    # --- Trend & Signal outputs ---------------------------------------
    trends: List[str]
    trend_details: List[Dict[str, Any]]
    trend_growth_rate: Optional[float]
    catalog_gaps: List[str]
    weather_signal: Optional[str]

    # --- Demand Forecasting outputs (grounded in ML model) -----------
    demand_forecast: Dict[str, float]          # category → demand index
    point_forecast: Optional[float]            # primary category 7-day revenue (INR)
    uncertainty_lower: Optional[float]
    uncertainty_upper: Optional[float]
    uncertainty_std: Optional[float]           # backtested empirical std
    backtested_mape: Optional[float]           # honest MAPE %
    forecast_details: Optional[Dict[str, Any]]
    forecast_source: Optional[str]

    # --- Campaign Studio outputs --------------------------------------
    campaign_copy: List[str]
    campaign_result: Optional[Dict[str, Any]]
    campaign_en: Optional[Dict[str, Any]]
    campaign_vernacular: Optional[Dict[str, Any]]
    banner_briefs: List[str]

    # --- Budget Optimization outputs (Linear Programming) -------------
    budget_allocation: Dict[str, float]        # channel → fraction
    budget_amounts_inr: Optional[Dict[str, float]]
    budget_optimization_result: Optional[Dict[str, Any]]

    # --- Simulation outputs (What-If engine) --------------------------
    simulation_result: Optional[Dict[str, Any]]
    simulated_forecast: Optional[float]
    delta_amount: Optional[float]
    delta_percent: Optional[float]
    scenario_type: Optional[str]
    magnitude: Optional[float]

    # --- Explainable AI & Audit trail --------------------------------
    explanation: Optional[str]
    explanation_source: Optional[str]
    grounded_factors: Optional[Dict[str, Any]]
    explanation_log: Annotated[List[str], operator.add]
