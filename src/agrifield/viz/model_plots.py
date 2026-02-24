"""Model result visualizations."""

from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from agrifield.modeling.features import build_feature_matrix

logger = logging.getLogger(__name__)


def plot_yield_by_soil(
    df: pd.DataFrame,
    min_count: int = 3,
    save_path: Path | None = None,
) -> Figure | None:
    """Bar chart of mean yield by soil map unit."""
    if "soil_musym" not in df.columns:
        logger.warning("No 'soil_musym' column; cannot plot yield by soil.")
        return None

    clean = df.dropna(subset=["mean_yield_bu_ac", "soil_musym"])
    group = clean.groupby("soil_musym")["mean_yield_bu_ac"].agg(["mean", "count"]).reset_index()
    group = group[group["count"] >= min_count]

    if group.empty:
        logger.warning("No soil types with at least %d acres.", min_count)
        return None

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(group["soil_musym"].astype(str), group["mean"])
    ax.set_xlabel("Soil map unit (musym)")
    ax.set_ylabel("Mean yield (bu/ac)")
    ax.set_title("Mean Yield by Soil Map Unit")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()

    if save_path is not None:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        logger.info("Saved soil plot to %s", save_path)

    return fig


def plot_spatial_predictions(
    df: pd.DataFrame,
    model: object,
    use_coords: bool = True,
    save_path: Path | None = None,
) -> Figure | None:
    """Scatter plot of predicted yield coloured by value."""
    if "lat" not in df.columns or "lon" not in df.columns:
        logger.warning("No lat/lon in dataset; cannot plot spatial predictions.")
        return None

    X, _y = build_feature_matrix(df, use_coords=use_coords)
    aligned = df.loc[X.index].copy()
    preds = model.predict(X)  # type: ignore[union-attr]

    fig, ax = plt.subplots(figsize=(7, 6))
    sc = ax.scatter(aligned["lon"], aligned["lat"], c=preds, s=40, cmap="RdYlGn")
    fig.colorbar(sc, ax=ax, label="Predicted yield (bu/ac)")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Spatial Pattern of Predicted Yield")
    fig.tight_layout()

    if save_path is not None:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        logger.info("Saved spatial predictions plot to %s", save_path)

    return fig


def plot_nitrogen_response(
    N: np.ndarray,
    y: np.ndarray,
    model: object,
    N_opt: float | None = None,
    save_path: Path | None = None,
) -> Figure:
    """Plot observed data points and fitted quadratic nitrogen response curve."""
    b0 = model.intercept_  # type: ignore[union-attr]
    b1 = model.coef_[0]  # type: ignore[union-attr]
    b2 = model.coef_[1]  # type: ignore[union-attr]

    N_grid = np.linspace(N.min(), N.max(), 50)
    y_grid = b0 + b1 * N_grid + b2 * N_grid ** 2

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(N, y, alpha=0.5, label="Observed acres")
    ax.plot(N_grid, y_grid, color="black", label="Quadratic fit")

    if N_opt is not None:
        y_opt = b0 + b1 * N_opt + b2 * N_opt ** 2
        ax.axvline(N_opt, color="red", linestyle="--", label="Optimum N")
        ax.scatter([N_opt], [y_opt], color="red", zorder=5)

    ax.set_xlabel("Nitrogen rate (lb/ac)")
    ax.set_ylabel("Yield (bu/ac)")
    ax.set_title("Quadratic Nitrogen Response Curve")
    ax.legend()
    fig.tight_layout()

    if save_path is not None:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        logger.info("Saved nitrogen response plot to %s", save_path)

    return fig
