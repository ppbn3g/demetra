"""Shared pytest fixtures."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from demetra.config.settings import demetraSettings


@pytest.fixture()
def settings() -> demetraSettings:
    """Default settings instance for tests."""
    return demetraSettings()


@pytest.fixture()
def sample_yield_df() -> pd.DataFrame:
    """Small synthetic yield DataFrame in UTM coordinates."""
    rng = np.random.default_rng(42)
    n = 200
    return pd.DataFrame({
        "x": rng.uniform(500_000, 500_500, n),
        "y": rng.uniform(4_300_000, 4_300_500, n),
        "yield_bu_ac": rng.uniform(100, 300, n),
        "farm": "TestFarm",
        "field": "TestField",
    })


@pytest.fixture()
def sample_acre_df() -> pd.DataFrame:
    """Small synthetic acre-level dataset matching expected output columns."""
    rng = np.random.default_rng(42)
    n = 20
    return pd.DataFrame({
        "acre_id": [f"{i:05d}" for i in range(n)],
        "x_min": np.arange(500_000, 500_000 + n * 63.6, 63.6)[:n],
        "x_max": np.arange(500_000 + 63.6, 500_000 + (n + 1) * 63.6, 63.6)[:n],
        "y_min": np.full(n, 4_300_000.0),
        "y_max": np.full(n, 4_300_063.6),
        "x_center": np.arange(500_000 + 31.8, 500_000 + n * 63.6 + 31.8, 63.6)[:n],
        "y_center": np.full(n, 4_300_031.8),
        "mean_yield_bu_ac": rng.uniform(150, 280, n),
        "n_points": rng.integers(10, 60, n),
        "mean_nitrogen_lb_ac": rng.uniform(80, 200, n),
        "rainfall_in": np.full(n, 18.5),
        "lat": rng.uniform(38.9, 39.0, n),
        "lon": rng.uniform(-92.4, -92.3, n),
        "soil_musym": rng.choice(["A", "B", "C"], n),
        "soil_muname": rng.choice(["Loam", "Clay", "Sand"], n),
        "farm": "TestFarm",
        "field": "TestField",
        "units": "meters",
    })
