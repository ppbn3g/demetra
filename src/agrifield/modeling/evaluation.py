"""Model training, evaluation, and K-fold cross-validation."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import KFold, train_test_split

logger = logging.getLogger(__name__)


def fit_and_evaluate(
    X: pd.DataFrame,
    y: pd.Series | np.ndarray,
    model: object,
    name: str,
    test_size: float = 0.2,
    random_state: int = 0,
    n_splits: int = 5,
) -> dict[str, object]:
    """Fit *model* on a train/test split, then run K-fold CV.

    Returns a dict with keys: model, train_r2, test_r2, cv_r2,
    train_rmse, test_rmse.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state,
    )

    model.fit(X_train, y_train)  # type: ignore[union-attr]

    y_pred_train = model.predict(X_train)  # type: ignore[union-attr]
    y_pred_test = model.predict(X_test)  # type: ignore[union-attr]

    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    train_rmse = float(np.sqrt(mean_squared_error(y_train, y_pred_train)))
    test_rmse = float(np.sqrt(mean_squared_error(y_test, y_pred_test)))

    # K-fold cross-validation
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    cv_r2_values: list[float] = []

    for train_idx, val_idx in kf.split(X):
        X_tr = X.iloc[train_idx]
        X_val = X.iloc[val_idx]
        y_tr = np.asarray(y)[train_idx]
        y_val = np.asarray(y)[val_idx]

        fold_model = type(model)(**model.get_params())  # type: ignore[union-attr]
        fold_model.fit(X_tr, y_tr)
        cv_r2_values.append(r2_score(y_val, fold_model.predict(X_val)))

    cv_r2_mean = float(np.mean(cv_r2_values))

    return {
        "model": name,
        "train_r2": train_r2,
        "test_r2": test_r2,
        "cv_r2": cv_r2_mean,
        "train_rmse": train_rmse,
        "test_rmse": test_rmse,
    }
