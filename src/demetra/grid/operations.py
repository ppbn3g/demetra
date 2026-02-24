"""Grid post-processing: phantom acre filtering and nitrogen merging."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def filter_phantom_acres(
    df: pd.DataFrame,
    min_density_percent: float = 0.15,
) -> pd.DataFrame:
    """Remove grid cells with very few yield points (edge/phantom acres)."""
    if len(df) == 0:
        return df

    median_points = df["n_points"].median()
    cutoff = median_points * min_density_percent

    logger.info("Median points per acre: %.1f", median_points)
    logger.info("Removing acres with fewer than %.1f points.", cutoff)

    original_count = len(df)
    df_clean = df[df["n_points"] >= cutoff].copy().reset_index(drop=True)
    dropped = original_count - len(df_clean)

    logger.info("Dropped %d phantom acres. New field size: %d acres.", dropped, len(df_clean))
    return df_clean


def merge_nitrogen_into_grid(
    grid_df: pd.DataFrame,
    nitrogen_df: pd.DataFrame,
) -> pd.DataFrame:
    """Compute mean nitrogen rate per acre cell via vectorized bin assignment."""
    df = grid_df.copy()
    cell_size = df["x_max"].iloc[0] - df["x_min"].iloc[0]
    x_origin = df["x_min"].min()
    y_origin = df["y_min"].min()

    # Bin nitrogen points into grid cells
    n_col_idx = np.floor((nitrogen_df["x"].values - x_origin) / cell_size).astype(int)
    n_row_idx = np.floor((nitrogen_df["y"].values - y_origin) / cell_size).astype(int)
    num_cols = int(np.round((df["x_min"].max() - x_origin) / cell_size)) + 1
    n_key = n_row_idx * num_cols + n_col_idx

    n_pts = pd.DataFrame({"key": n_key, "nitrogen_lb_ac": nitrogen_df["nitrogen_lb_ac"].values})
    n_agg = n_pts.groupby("key")["nitrogen_lb_ac"].mean().rename("mean_nitrogen_lb_ac")

    # Build the same key for grid cells
    grid_col = np.round((df["x_min"].values - x_origin) / cell_size).astype(int)
    grid_row = np.round((df["y_min"].values - y_origin) / cell_size).astype(int)
    df["_key"] = grid_row * num_cols + grid_col

    df = df.merge(n_agg, left_on="_key", right_index=True, how="left")
    df = df.drop(columns=["_key"])

    logger.info(
        "Merged nitrogen into grid (non-NA rows): %d",
        df["mean_nitrogen_lb_ac"].notna().sum(),
    )
    return df
