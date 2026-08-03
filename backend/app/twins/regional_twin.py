"""Regional Digital Twin store.

Loads the 15 regional twins from the bundled JSON seed file and exposes
a simple CRUD-like interface that the agent pipeline, routers, and
simulation engine all share.  The store is intentionally in-memory so it
starts instantly without a database dependency; swap ``_load`` / ``update``
for SQLAlchemy or Redis calls when persistence is needed without changing
the public interface.
"""
import json
import logging
from pathlib import Path

from app.models.region import RegionalTwin
from app.core.exceptions import RegionNotFoundError

logger = logging.getLogger(__name__)

_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "regions.json"


class RegionalTwinStore:
    """In-memory store for Regional Digital Twins, backed by a JSON seed file."""

    def __init__(self, data_path: Path = _DATA_PATH) -> None:
        self._data_path = data_path
        self._twins: dict[str, RegionalTwin] = self._load()
        logger.info("RegionalTwinStore loaded %d twins", len(self._twins))

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------
    def _load(self) -> dict[str, RegionalTwin]:
        raw: list[dict] = json.loads(self._data_path.read_text(encoding="utf-8"))
        return {r["region_id"]: RegionalTwin(**r) for r in raw}

    # ------------------------------------------------------------------
    # Public read interface
    # ------------------------------------------------------------------
    def get(self, region_id: str) -> RegionalTwin:
        """Return the twin for *region_id*, raising RegionNotFoundError if missing."""
        twin = self._twins.get(region_id)
        if twin is None:
            raise RegionNotFoundError(region_id)
        return twin

    def get_or_none(self, region_id: str) -> RegionalTwin | None:
        """Return the twin or None without raising."""
        return self._twins.get(region_id)

    def list_all(self) -> list[RegionalTwin]:
        """Return all twins sorted by region_id."""
        return sorted(self._twins.values(), key=lambda t: t.region_id)

    def region_ids(self) -> list[str]:
        return sorted(self._twins.keys())

    # ------------------------------------------------------------------
    # Public write interface
    # ------------------------------------------------------------------
    def update(self, twin: RegionalTwin) -> None:
        """Persist new signals (sales, weather, campaign results) into the twin.

        Call this after an agent pipeline run to reflect the latest state.
        """
        self._twins[twin.region_id] = twin
        logger.debug("RegionalTwinStore updated twin for %s", twin.region_id)


# Module-level singleton — imported by routers, agents, and the simulation engine
regional_twin_store = RegionalTwinStore()
