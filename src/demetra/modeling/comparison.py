"""Model registry and multi-model comparison runner."""

from __future__ import annotations

import logging

import pandas as pd
from sklearn.ensemble import (
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import ElasticNet, Lasso, LinearRegression, Ridge

from demetra.modeling.evaluation import fit_and_evaluate
from demetra.modeling.features import build_feature_matrix, build_quadratic_n_soil_matrix

logger = logging.getLogger(__name__)


def get_model_registry() -> list[tuple[str, object]]:
    """Return the list of (name, model) tuples to evaluate.

    CatBoost is included only when installed.
    """
    models: list[tuple[str, object]] = [
        ("GradientBoosting", GradientBoostingRegressor(random_state=0)),
        ("ExtraTrees", ExtraTreesRegressor(n_estimators=300, random_state=0, n_jobs=-1)),
        ("RandomForest", RandomForestRegressor(n_estimators=300, random_state=0, n_jobs=-1)),
        ("LinearRegression", LinearRegression()),
        ("Ridge(alpha=1.0)", Ridge(alpha=1.0)),
        ("Lasso(alpha=0.1)", Lasso(alpha=0.1)),
        ("ElasticNet(0.1,0.5)", ElasticNet(alpha=0.1, l1_ratio=0.5)),
    ]

    try:
        from catboost import CatBoostRegressor

        models.append((
            "CatBoost",
            CatBoostRegressor(
                depth=6,
                learning_rate=0.05,
                iterations=500,
                loss_function="RMSE",
                verbose=False,
                random_state=0,
            ),
        ))
    except ImportError:
        logger.info("CatBoost not installed; skipping.")

    return models


def run_model_comparison(
    df: pd.DataFrame,
    use_coords: bool = True,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Run all registered models plus a quadratic baseline.

    Returns (results_df, fitted_models_dict).
    """
    X, y = build_feature_matrix(df, use_coords=use_coords)
    Xq, yq = build_quadratic_n_soil_matrix(df)

    results_rows: list[dict[str, object]] = []
    fitted_models: dict[str, object] = {}

    # Quadratic baseline
    quad_model = LinearRegression()
    res_quad = fit_and_evaluate(Xq, yq, quad_model, "Quadratic_N+Soil")
    results_rows.append(res_quad)
    fitted_models["Quadratic_N+Soil"] = quad_model

    # Standard models
    for name, mdl in get_model_registry():
        res = fit_and_evaluate(X, y, mdl, name)
        results_rows.append(res)
        fitted_models[name] = mdl

    results_df = pd.DataFrame(results_rows)[
        ["model", "train_r2", "test_r2", "cv_r2", "train_rmse", "test_rmse"]
    ]

    logger.info(
        "Model comparison (use_coords=%s):\n%s",
        use_coords,
        results_df.sort_values("test_r2", ascending=False).reset_index(drop=True),
    )

    return results_df, fitted_models
