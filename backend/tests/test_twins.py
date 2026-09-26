"""Unit tests for RegionalTwinStore and SegmentTwinStore.

No LLM calls — fully deterministic.
"""
import pytest
from app.twins.regional_twin import RegionalTwinStore
from app.twins.segment_twin import SegmentTwinStore
from app.core.exceptions import RegionNotFoundError, SegmentNotFoundError


class TestRegionalTwinStore:
    def setup_method(self):
        self.store = RegionalTwinStore()

    def test_loads_all_regions(self):
        twins = self.store.list_all()
        assert len(twins) == 15

    def test_get_known_region(self):
        twin = self.store.get("TN-01")
        assert twin.region_id == "TN-01"
        assert twin.state == "Tamil Nadu"

    def test_price_sensitivity_in_range(self):
        for twin in self.store.list_all():
            assert 0.0 <= twin.price_sensitivity <= 1.0, (
                f"{twin.region_id} has out-of-range price_sensitivity: {twin.price_sensitivity}"
            )

    def test_all_regions_have_categories(self):
        for twin in self.store.list_all():
            assert twin.top_categories, f"{twin.region_id} has no top_categories"

    def test_get_missing_region_raises(self):
        with pytest.raises(RegionNotFoundError):
            self.store.get("XX-99")

    def test_get_or_none_returns_none(self):
        assert self.store.get_or_none("XX-99") is None

    def test_update_twin(self):
        twin = self.store.get("KL-01")
        updated = twin.model_copy(update={"avg_temperature_c": 30.0})
        self.store.update(updated)
        assert self.store.get("KL-01").avg_temperature_c == 30.0

    def test_region_ids_sorted(self):
        ids = self.store.region_ids()
        assert ids == sorted(ids)


class TestSegmentTwinStore:
    def setup_method(self):
        self.store = SegmentTwinStore()

    def test_loads_four_segments(self):
        assert len(self.store.list_all()) == 4

    def test_get_students_segment(self):
        seg = self.store.get("students")
        assert seg.segment_id == "students"
        assert seg.price_sensitivity > 0.5

    def test_get_missing_segment_raises(self):
        with pytest.raises(SegmentNotFoundError):
            self.store.get("unicorn_segment")

    def test_all_segments_have_preferred_categories(self):
        for seg in self.store.list_all():
            assert seg.preferred_categories, f"{seg.segment_id} has no preferred_categories"

    def test_price_sensitivity_in_range(self):
        for seg in self.store.list_all():
            assert 0.0 <= seg.price_sensitivity <= 1.0
