"""Quadratic nitrogen response curve fitting."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

logger = logging.getLogger(__name__)


def fit_quadratic_nitrogen(
    df: pd.DataFrame,
) -> tuple[float, float, float, LinearRegression] | None:
    """Fit yield = b0 + b1*N + b2*N^2 and return (b0, b1, b2, model).

    Returns ``None`` if the required columns are missing.
    """
    if "mean_nitrogen_lb_ac" not in df.columns:
        logger.warning("No nitrogen column found.")
        return None

    clean = df.dropna(subset=["mean_yield_bu_ac", "mean_nitrogen_lb_ac"])
    N = clean["mean_nitrogen_lb_ac"].values
    y = clean["mean_yield_bu_ac"].values

    Xq = np.column_stack([N, N ** 2])
    model = LinearRegression()
    model.fit(Xq, y)

    b0 = float(model.intercept_)
    b1 = float(model.coef_[0])
    b2 = float(model.coef_[1])

    logger.info("Quadratic model: yield = %.3f + %.3f*N + %.5f*N^2", b0, b1, b2)
    return b0, b1, b2, model


def compute_optimal_n_rate(b0: float, b1: float, b2: float) -> float | None:
    """Compute the optimal N rate (vertex of the downward parabola).

    Returns ``None`` when the parabola opens upward (b2 >= 0).
    """
    if b2 >= 0:
        logger.warning("b2 >= 0; curve does not bend down — no clear optimum.")
        return None

    n_opt = -b1 / (2.0 * b2)
    logger.info("Optimal N rate (vertex) = %.1f lb/ac", n_opt)
    return n_opt
