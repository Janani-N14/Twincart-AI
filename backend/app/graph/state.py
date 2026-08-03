"""Shared LangGraph state for the TwinAI agent pipeline.

Every agent node receives the full TwinAIState and returns a *partial*
dict — LangGraph merges the returned keys back into the state, leaving
all other keys unchanged.  The Annotated[list, operator.add] on
explanation_log means each node's log entries are *appended* rather
than replaced, giving a running audit trail across the whole pipeline.
"""
import operator
from typing import Annotated, TypedDict


class TwinAIState(TypedDict):
    # --- Inputs -------------------------------------------------------
    region_id: str
    segment_id: str | None

    # --- Intermediate agent outputs -----------------------------------
    trends: list[str]
    demand_forecast: dict[str, float]          # category → demand index 0-100
    catalog_gaps: list[str]
    weather_signal: str | None

    # --- Campaign outputs ---------------------------------------------
    campaign_copy: list[str]
    banner_briefs: list[str]
    budget_allocation: dict[str, float]        # channel → budget fraction

    # --- Simulation output (optional, populated only via sim router) --
    simulation_result: dict[str, float] | None

    # --- Audit log (append-only across all nodes) ---------------------
    explanation_log: Annotated[list[str], operator.add]
