"""Tests for yield loading and cleaning."""

from __future__ import annotations

import numpy as np
import pandas as pd

from demetra.config.settings import demetraSettings
from demetra.ingest.yield_loader import clean_jd_yield_dataframe


def test_clean_removes_low_yield(settings: demetraSettings) -> None:
    df = pd.DataFrame({"yield_bu_ac": [10, 49, 50, 200, 350, 400]})
    result = clean_jd_yield_dataframe(df, settings)
    assert result["yield_bu_ac"].min() >= settings.yield_min
    assert result["yield_bu_ac"].max() <= settings.yield_max


def test_clean_removes_slow_speed(settings: demetraSettings) -> None:
    df = pd.DataFrame({
        "yield_bu_ac": [200, 200, 200],
        "VEHICLSPEED": [0.0, 0.1, 0.5],
    })
    result = clean_jd_yield_dataframe(df, settings)
    assert len(result) == 1
    assert result.iloc[0]["VEHICLSPEED"] == 0.5


def test_clean_preserves_valid_rows() -> None:
    df = pd.DataFrame({"yield_bu_ac": [100, 200, 300]})
    result = clean_jd_yield_dataframe(df)
    assert len(result) == 3
