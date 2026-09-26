"""FastAPI router — Digital Twins (read-only)."""
import logging

from fastapi import APIRouter, HTTPException

from app.models.region import RegionalTwin, RegionInsightRequest, RegionInsightResponse
from app.models.segment import CustomerSegmentTwin, SegmentInsightRequest, SegmentInsightResponse
from app.twins.regional_twin import regional_twin_store
from app.twins.segment_twin import segment_twin_store
from app.core.exceptions import RegionNotFoundError, SegmentNotFoundError

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Regional twins ────────────────────────────────────────────────────────────

@router.get("/regions", response_model=list[RegionalTwin], summary="List all regional twins")
def list_regional_twins() -> list[RegionalTwin]:
    """Return all 15 regional digital twins sorted by region_id."""
    return regional_twin_store.list_all()


@router.get("/regions/{region_id}", response_model=RegionalTwin, summary="Get one regional twin")
def get_regional_twin(region_id: str) -> RegionalTwin:
    """Return the digital twin for a specific region."""
    try:
        return regional_twin_store.get(region_id)
    except RegionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# ── Segment twins ─────────────────────────────────────────────────────────────

@router.get("/segments", response_model=list[CustomerSegmentTwin], summary="List all segment twins")
def list_segment_twins() -> list[CustomerSegmentTwin]:
    """Return all customer segment digital twins."""
    return segment_twin_store.list_all()


@router.get("/segments/{segment_id}", response_model=CustomerSegmentTwin, summary="Get one segment twin")
def get_segment_twin(segment_id: str) -> CustomerSegmentTwin:
    """Return the digital twin for a specific customer segment."""
    try:
        return segment_twin_store.get(segment_id)
    except SegmentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
