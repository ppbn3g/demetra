"""Build acre-level grids and assign yield points — fully vectorized."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from demetra.config.settings import demetraSettings
from demetra.ingest.yield_loader import load_yield_points

logger = logging.getLogger(__name__)


def build_acre_grid(
    yield_df: pd.DataFrame,
    cell_size: float,
    units: str,
) -> pd.DataFrame:
    """Create a rectangular acre grid covering the extent of *yield_df*.

    Uses ``np.arange`` / ``np.meshgrid`` instead of nested while loops.
    """
    min_x, max_x = yield_df["x"].min(), yield_df["x"].max()
    min_y, max_y = yield_df["y"].min(), yield_df["y"].max()
    logger.info("Field extent: x [%.1f, %.1f], y [%.1f, %.1f]", min_x, max_x, min_y, max_y)

    x_edges = np.arange(min_x, max_x, cell_size)
    y_edges = np.arange(min_y, max_y, cell_size)
    num_cols, num_rows = len(x_edges), len(y_edges)
    logger.info("Grid will be %d rows by %d columns", num_rows, num_cols)

    # Meshgrid to create all cell origins at once
    xx, yy = np.meshgrid(x_edges, y_edges)
    x_min_flat = xx.ravel()
    y_min_flat = yy.ravel()

    grid_df = pd.DataFrame({
        "farm": yield_df["farm"].iloc[0],
        "field": yield_df["field"].iloc[0],
        "acre_id": [f"{i:05d}" for i in range(len(x_min_flat))],
        "x_min": x_min_flat,
        "x_max": x_min_flat + cell_size,
        "y_min": y_min_flat,
        "y_max": y_min_flat + cell_size,
        "x_center": x_min_flat + cell_size / 2.0,
        "y_center": y_min_flat + cell_size / 2.0,
        "units": units,
    })

    logger.info("Built %d grid cells.", len(grid_df))
    return grid_df


def assign_points_to_grid(
    yield_df: pd.DataFrame,
    grid_df: pd.DataFrame,
) -> pd.DataFrame:
    """Assign yield points to grid cells via vectorized bin lookup."""
    grid = grid_df.copy()

    cell_size = grid["x_max"].iloc[0] - grid["x_min"].iloc[0]
    x_origin = grid["x_min"].min()
    y_origin = grid["y_min"].min()

    # Compute grid column/row indices for every yield point
    col_idx = np.floor((yield_df["x"].values - x_origin) / cell_size).astype(int)
    row_idx = np.floor((yield_df["y"].values - y_origin) / cell_size).astype(int)

    # Same for grid cells — derive their col/row from x_min/y_min
    grid_col = np.round((grid["x_min"].values - x_origin) / cell_size).astype(int)
    grid_row = np.round((grid["y_min"].values - y_origin) / cell_size).astype(int)

    # Build a lookup: (col, row) → grid index
    num_cols = grid_col.max() + 1
    grid_key = grid_row * num_cols + grid_col
    point_key = row_idx * num_cols + col_idx

    # Use pandas groupby on the point keys
    pts = pd.DataFrame({"key": point_key, "yield_bu_ac": yield_df["yield_bu_ac"].values})
    agg = pts.groupby("key")["yield_bu_ac"].agg(["mean", "count"]).rename(
        columns={"mean": "mean_yield_bu_ac", "count": "n_points"},
    )

    grid["_key"] = grid_key
    grid = grid.merge(agg, left_on="_key", right_index=True, how="left")
    grid["mean_yield_bu_ac"] = grid["mean_yield_bu_ac"].astype(float)
    grid["n_points"] = grid["n_points"].fillna(0).astype(int)
    grid = grid.drop(columns=["_key"])

    logger.info("Finished assigning yield points to grid cells.")
    return grid


def build_field_grid(
    shp_path: str,
    farm: str,
    field: str,
    cell_size: float,
    units: str,
    settings: demetraSettings | None = None,
) -> pd.DataFrame:
    """End-to-end: load yield shapefile → build grid → assign points."""
    settings = settings or demetraSettings()

    yield_df = load_yield_points(shp_path, farm, field, settings)
    grid_df = build_acre_grid(yield_df, cell_size, units)
    grid_with_yield = assign_points_to_grid(yield_df, grid_df)

    # Keep only cells that actually received yield data
    cleaned = grid_with_yield[grid_with_yield["n_points"] > 0].reset_index(drop=True)
    logger.info("Final field grid has %d rows.", len(cleaned))
    return cleaned
