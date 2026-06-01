"""Tests for CONUS bounding box helpers."""

import pytest

from flightsearch_mcp.region import US_BBOX, resolve_bbox


def test_resolve_bbox_defaults_to_conus() -> None:
    assert resolve_bbox(None, None, None, None) == US_BBOX


def test_resolve_bbox_intersects_viewport() -> None:
    bbox = resolve_bbox(30.0, -100.0, 40.0, -90.0)
    assert bbox is not None
    assert bbox["lamin"] == 30.0
    assert bbox["lomax"] == -90.0


def test_resolve_bbox_rejects_partial_params() -> None:
    with pytest.raises(ValueError, match="Provide all bounding box"):
        resolve_bbox(30.0, None, None, None)


def test_resolve_bbox_returns_none_when_no_overlap() -> None:
    assert resolve_bbox(50.0, -100.0, 55.0, -90.0) is None
