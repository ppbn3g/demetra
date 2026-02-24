"""Tests for model evaluation."""

from __future__ import annotations

import pandas as pd
from sklearn.linear_model import LinearRegression

from agrifield.modeling.evaluation import fit_and_evaluate


def test_metrics_keys(sample_acre_df: pd.DataFrame) -> None:
    from agrifield.modeling.features import build_feature_matrix

    X, y = build_feature_matrix(sample_acre_df, use_coords=True)
    model = LinearRegression()
    result = fit_and_evaluate(X, y, model, "LinearRegression")

    expected_keys = {"model", "train_r2", "test_r2", "cv_r2", "train_rmse", "test_rmse"}
    assert set(result.keys()) == expected_keys
    assert result["model"] == "LinearRegression"


def test_rmse_is_positive(sample_acre_df: pd.DataFrame) -> None:
    from agrifield.modeling.features import build_feature_matrix

    X, y = build_feature_matrix(sample_acre_df, use_coords=True)
    model = LinearRegression()
    result = fit_and_evaluate(X, y, model, "LR")

    assert result["train_rmse"] >= 0
    assert result["test_rmse"] >= 0
