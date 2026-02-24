"""Tests for feature matrix construction."""

from __future__ import annotations

import pandas as pd

from agrifield.modeling.features import build_feature_matrix


def test_feature_matrix_shape(sample_acre_df: pd.DataFrame) -> None:
    X, y = build_feature_matrix(sample_acre_df, use_coords=True)
    assert len(X) == len(y)
    assert X.shape[0] > 0
    # Should include nitrogen, rainfall, lat, lon, plus soil dummies
    assert X.shape[1] >= 4


def test_feature_matrix_no_coords(sample_acre_df: pd.DataFrame) -> None:
    X, y = build_feature_matrix(sample_acre_df, use_coords=False)
    assert "lat" not in X.columns
    assert "lon" not in X.columns


def test_soil_dummy_coding(sample_acre_df: pd.DataFrame) -> None:
    X, _y = build_feature_matrix(sample_acre_df, use_coords=True)
    soil_cols = [c for c in X.columns if c.startswith("soil_musym_")]
    # With 3 unique soil types, drop_first=True → 2 dummy columns
    assert len(soil_cols) == 2
