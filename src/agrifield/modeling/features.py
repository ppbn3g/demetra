"""Feature matrix construction for ML models."""

from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def build_feature_matrix(
    df: pd.DataFrame,
    use_coords: bool = True,
) -> tuple[pd.DataFrame, pd.Series]:
    """Build the standard feature matrix (X) and target vector (y).

    Automatically includes nitrogen, irrigation, rainfall, optional
    lat/lon, and dummy-coded soil type.
    """
    df = df.dropna(subset=["mean_yield_bu_ac"]).copy()

    feature_cols: list[str] = []
    for col in ("mean_nitrogen_lb_ac", "mean_irrigation_in", "rainfall_in"):
        if col in df.columns:
            feature_cols.append(col)

    if use_coords:
        for col in ("lat", "lon"):
            if col in df.columns:
                feature_cols.append(col)

    X = df[feature_cols].copy()

    # Dummy-code soil if present
    if "soil_musym" in df.columns:
        df["soil_musym"] = df["soil_musym"].fillna("UNK")
        X = pd.get_dummies(
            X.join(df["soil_musym"]),
            columns=["soil_musym"],
            drop_first=True,
        )

    # Drop columns that are entirely NaN
    all_nan_cols = [c for c in X.columns if X[c].isna().all()]
    if all_nan_cols:
        logger.info("Dropping all-NaN feature columns: %s", all_nan_cols)
        X = X.drop(columns=all_nan_cols)

    # Drop rows with remaining NaN features
    valid_mask = ~X.isna().any(axis=1)
    dropped = (~valid_mask).sum()
    if dropped:
        logger.info("Dropping %d rows with remaining NaN features.", dropped)
    X = X[valid_mask].copy()

    y = df.loc[X.index, "mean_yield_bu_ac"]

    logger.info("Model matrix shapes — X: %s, y: %s", X.shape, y.shape)
    return X, y


def build_quadratic_n_soil_matrix(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    """Build a quadratic N + soil dummy feature matrix for baseline comparison."""
    df = df.dropna(subset=["mean_yield_bu_ac", "mean_nitrogen_lb_ac"]).copy()

    Xq = pd.DataFrame({
        "N": df["mean_nitrogen_lb_ac"].values,
        "N2": (df["mean_nitrogen_lb_ac"].values ** 2),
    })

    if "soil_musym" in df.columns:
        df["soil_musym"] = df["soil_musym"].fillna("UNK")
        Xq = pd.get_dummies(
            Xq.join(df["soil_musym"].reset_index(drop=True)),
            columns=["soil_musym"],
            drop_first=True,
        )

    yq = df["mean_yield_bu_ac"].reset_index(drop=True)

    logger.info("Quadratic N+Soil matrix — X: %s, y: %s", Xq.shape, yq.shape)
    return Xq, yq
