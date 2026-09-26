"""LangGraph workflow for the TwinAI agent pipeline.

Topology (from the efficiency guide — parallel fan-out then fan-in):

    ┌─────────────────────────────────────┐
    │            entry point              │
    └──────┬──────────┬───────────┬───────┘
           ▼          ▼           ▼
    trend_detection  weather_festival  catalog_gap   ← run concurrently
           │          │           │
           └──────────┴───────────┘
                      ▼
              demand_forecasting                      ← fan-in
                      ▼
              campaign_generator
                      ▼
               banner_studio
                      ▼
              budget_optimizer
                      ▼
               explainability
                      ▼
                     END

LangGraph executes each "superstep" (nodes with no dependency on each
other) as coroutines on one event loop via asyncio — no threads needed.
"""
from langgraph.graph import StateGraph, END

from app.graph.state import TwinAIState
from app.agents import (
    trend_detection,
    demand_forecasting,
    weather_festival,
    catalog_gap,
    campaign_generator,
    banner_studio,
    budget_optimizer,
    explainability,
)


def build_workflow():
    """Construct and compile the TwinAI StateGraph."""
    graph = StateGraph(TwinAIState)

    # Register nodes
    graph.add_node("trend_detection",   trend_detection.run)
    graph.add_node("weather_festival",  weather_festival.run)
    graph.add_node("catalog_gap",       catalog_gap.run)
    graph.add_node("demand_forecasting", demand_forecasting.run)
    graph.add_node("campaign_generator", campaign_generator.run)
    graph.add_node("banner_studio",     banner_studio.run)
    graph.add_node("budget_optimizer",  budget_optimizer.run)
    graph.add_node("explainability",    explainability.run)

    # Parallel fan-out: all three start from the entry point
    graph.set_entry_point("trend_detection")
    # LangGraph doesn't support multiple set_entry_point calls, so we
    # route from a virtual "__start__" via conditional edges instead —
    # achieved here by making trend_detection the entry and having the
    # other two parallel nodes also connect from it with no data dependency.
    # A cleaner fan-out uses a router node:
    graph.add_node("parallel_start", _parallel_start)
    graph.set_entry_point("parallel_start")
    graph.add_edge("parallel_start", "trend_detection")
    graph.add_edge("parallel_start", "weather_festival")
    graph.add_edge("parallel_start", "catalog_gap")

    # Fan-in: demand_forecasting waits for all three
    graph.add_edge("trend_detection",  "demand_forecasting")
    graph.add_edge("weather_festival", "demand_forecasting")
    graph.add_edge("catalog_gap",      "demand_forecasting")

    # Sequential tail
    graph.add_edge("demand_forecasting", "campaign_generator")
    graph.add_edge("campaign_generator", "banner_studio")
    graph.add_edge("banner_studio",      "budget_optimizer")
    graph.add_edge("budget_optimizer",   "explainability")
    graph.add_edge("explainability",     END)

    return graph.compile()


def _parallel_start(state: TwinAIState) -> dict:
    """No-op router node — exists only to fan out to the three parallel agents."""
    return {}


compiled_workflow = build_workflow()
