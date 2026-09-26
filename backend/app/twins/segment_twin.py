"""Customer Segment Digital Twin store.

Four canonical segments are seeded in-memory; extend the list or load from
a JSON file using the same pattern as RegionalTwinStore.
"""
import logging

from app.models.segment import CustomerSegmentTwin
from app.core.exceptions import SegmentNotFoundError

logger = logging.getLogger(__name__)

_SEED_SEGMENTS: list[dict] = [
    {
        "segment_id": "students",
        "label": "Students",
        "age_range": "16-24",
        "income_bracket": "0-15,000 INR/month",
        "preferred_categories": ["mobile accessories", "apparel", "stationery", "earphones"],
        "platform_behaviour": "Highly deal-driven; browses extensively before converting; active during late-night sale windows.",
        "price_sensitivity": 0.85,
        "region_ids": ["TN-01", "MH-01", "KA-01", "UP-01", "WB-01"],
    },
    {
        "segment_id": "working_professionals",
        "label": "Working Professionals",
        "age_range": "25-40",
        "income_bracket": "30,000-1,00,000 INR/month",
        "preferred_categories": ["electronics accessories", "apparel", "beauty", "footwear"],
        "platform_behaviour": "Values quality and quick delivery; converts on weekend mornings; responsive to festival offers.",
        "price_sensitivity": 0.50,
        "region_ids": ["MH-01", "KA-01", "GJ-01", "PB-01", "TS-01"],
    },
    {
        "segment_id": "homemakers",
        "label": "Homemakers",
        "age_range": "28-50",
        "income_bracket": "0-20,000 INR/month household spend",
        "preferred_categories": ["kitchenware", "home textiles", "home decor", "apparel"],
        "platform_behaviour": "Category-loyal; builds wishlists before festivals; influenced by vernacular language content.",
        "price_sensitivity": 0.70,
        "region_ids": ["TN-01", "BR-01", "UP-01", "RJ-01", "OD-01"],
    },
    {
        "segment_id": "budget_shoppers",
        "label": "Budget-Conscious Shoppers",
        "age_range": "18-55",
        "income_bracket": "5,000-25,000 INR/month",
        "preferred_categories": ["apparel", "footwear", "mobile accessories", "kitchenware"],
        "platform_behaviour": "Waits for sales and coupon drops; very high cart-abandonment rate; responds strongly to free-shipping offers.",
        "price_sensitivity": 0.90,
        "region_ids": ["BR-01", "UP-01", "MP-01", "OD-01", "AS-01"],
    },
]


import json
from pathlib import Path

_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "segments.json"


class SegmentTwinStore:
    """In-memory store for Customer Segment Digital Twins, backed by segments.json."""

    def __init__(self, data_path: Path = _DATA_PATH) -> None:
        self._data_path = data_path
        self._segments: dict[str, CustomerSegmentTwin] = self._load()
        logger.info("SegmentTwinStore loaded %d segments", len(self._segments))

    def _load(self) -> dict[str, CustomerSegmentTwin]:
        if self._data_path.exists():
            try:
                raw: list[dict] = json.loads(self._data_path.read_text(encoding="utf-8"))
                return {s["segment_id"]: CustomerSegmentTwin(**s) for s in raw}
            except Exception as e:
                logger.warning("Could not read %s, falling back to seed: %s", self._data_path, e)
        return {s["segment_id"]: CustomerSegmentTwin(**s) for s in _SEED_SEGMENTS}


    def get(self, segment_id: str) -> CustomerSegmentTwin:
        seg = self._segments.get(segment_id)
        if seg is None:
            raise SegmentNotFoundError(segment_id)
        return seg

    def get_or_none(self, segment_id: str) -> CustomerSegmentTwin | None:
        return self._segments.get(segment_id)

    def list_all(self) -> list[CustomerSegmentTwin]:
        return list(self._segments.values())

    def segment_ids(self) -> list[str]:
        return list(self._segments.keys())

    def update(self, segment: CustomerSegmentTwin) -> None:
        self._segments[segment.segment_id] = segment
        logger.debug("SegmentTwinStore updated segment %s", segment.segment_id)


# Module-level singleton
segment_twin_store = SegmentTwinStore()
