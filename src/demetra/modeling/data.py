"""Dataset loading and inspection utilities."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

PREDICTOR_COLUMNS: list[str] = [
    "mean_nitrogen_lb_ac",
    "mean_irrigation_in",
    "rainfall_in",
    "lat",
    "lon",
    "soil_musym",
]


def load_dataset(csv_path: str | Path) -> pd.DataFrame:
    """Load an acre-level dataset CSV."""
    df = pd.read_csv(csv_path)
    logger.info("Loaded dataset. Shape: %s", df.shape)
    return df


def inspect_predictors(df: pd.DataFrame) -> dict[str, dict[str, object]]:
    """Return summary statistics for key predictor columns.

    Returns a dict keyed by column name → {describe: ..., missing: int}.
    """
    results: dict[str, dict[str, object]] = {}
    for col in PREDICTOR_COLUMNS:
        if col in df.columns:
            results[col] = {
                "describe": df[col].describe().to_dict(),
                "missing": int(df[col].isna().sum()),
            }
    return results
