"""FastAPI router — What-If Simulation Engine."""
import logging

from fastapi import APIRouter, HTTPException

from app.models.simulation import SimulationRequest, SimulationResponse
from app.simulation.engine import simulation_engine
from app.core.exceptions import RegionNotFoundError, SimulationError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/run", response_model=SimulationResponse, summary="Run a what-if scenario")
def run_simulation(payload: SimulationRequest) -> SimulationResponse:
    """Run the rule-based what-if simulation for the given region and scenario.

    Returns predicted conversion rate, revenue index, and a plain-language
    interpretation of what the scenario implies.
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
