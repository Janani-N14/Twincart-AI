"""FastAPI router — What-If Simulation Engine."""

import logging
from fastapi import APIRouter, HTTPException

from app.models.simulation import SimulationRunRequest, SimulationResponse
from app.simulation.engine import simulation_engine
from app.core.exceptions import RegionNotFoundError, SimulationError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/run", response_model=SimulationResponse, summary="Run a what-if scenario")
def run_simulation(payload: SimulationRunRequest) -> SimulationResponse:
    """Run the mathematically explainable what-if simulation for the given region and scenario.

    Returns baseline forecast, simulated forecast, revenue delta (INR and %),
    predicted conversion rate, revenue index, and explicit elasticity factors.
    """
    try:
        return simulation_engine.run(payload)
    except RegionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SimulationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Simulation failed for region=%s", payload.region_id)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{sim_id}", response_model=SimulationResponse, summary="Get simulation run by ID")
def get_simulation_run(sim_id: str) -> SimulationResponse:
    """Retrieve a previously executed simulation result by its ID."""
    run = simulation_engine.get_run(sim_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Simulation run '{sim_id}' not found.")
    return run
