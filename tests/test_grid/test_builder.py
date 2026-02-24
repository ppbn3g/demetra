"""Tests for grid builder."""

from __future__ import annotations

import numpy as np
import pandas as pd

from agrifield.grid.builder import build_acre_grid, assign_points_to_grid


def test_grid_dimensions(sample_yield_df: pd.DataFrame) -> None:
    cell_size = 63.6
    grid = build_acre_grid(sample_yield_df, cell_size, "meters")

    x_range = sample_yield_df["x"].max() - sample_yield_df["x"].min()
    y_range = sample_yield_df["y"].max() - sample_yield_df["y"].min()
    expected_cols = int(np.ceil(x_range / cell_size))
    expected_rows = int(np.ceil(y_range / cell_size))

    # Grid should have roughly expected_rows * expected_cols cells
    assert len(grid) == expected_rows * expected_cols


def test_grid_has_required_columns(sample_yield_df: pd.DataFrame) -> None:
    grid = build_acre_grid(sample_yield_df, 63.6, "meters")
    for col in ("x_min", "x_max", "y_min", "y_max", "x_center", "y_center", "acre_id"):
        assert col in grid.columns


def test_assign_points_adds_yield(sample_yield_df: pd.DataFrame) -> None:
    grid = build_acre_grid(sample_yield_df, 63.6, "meters")
    result = assign_points_to_grid(sample_yield_df, grid)
    assert "mean_yield_bu_ac" in result.columns
    assert "n_points" in result.columns
    assert result["n_points"].sum() > 0
