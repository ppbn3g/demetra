"""USDA SSURGO soil data API client with retry logic and progress bar."""

from __future__ import annotations

import logging
import time

import pandas as pd
from tqdm import tqdm

from agrifield.config.settings import AgrifieldSettings
from agrifield.external.weather import _request_with_retry

logger = logging.getLogger(__name__)


def query_ssurgo(
    lat: float,
    lon: float,
    settings: AgrifieldSettings | None = None,
) -> tuple[str | None, str | None]:
    """Query SSURGO for the soil map unit at a single (lat, lon) point."""
    settings = settings or AgrifieldSettings()

    wkt_point = f"point ({lon} {lat})"
    sql = (
        "SELECT TOP 1 mu.musym, mu.muname "
        "FROM mapunit mu "
        "WHERE mu.mukey IN ("
        f"SELECT mukey FROM SDA_Get_Mukey_from_intersection_with_WktWgs84('{wkt_point}')"
        ")"
    )

    payload = {"QUERY": sql, "FORMAT": "JSON"}

    resp = _request_with_retry(
        "POST",
        settings.ssurgo_url,
        max_retries=settings.ssurgo_max_retries,
        backoff=settings.ssurgo_backoff,
        data=payload,
        timeout=settings.ssurgo_timeout,
    )

    if resp is None:
        return None, None

    if not resp.ok:
        logger.warning("SSURGO returned status %d", resp.status_code)
        return None, None

    try:
        data = resp.json()
    except Exception as exc:
        logger.warning("Error parsing SSURGO JSON: %s", exc)
        return None, None

    rows = data.get("Table", [])
    if not rows:
        return None, None

    row0 = rows[0]
    if isinstance(row0, dict):
        return row0.get("musym"), row0.get("muname")
    if isinstance(row0, list) and len(row0) >= 2:
        return row0[0], row0[1]

    logger.warning("Unexpected SSURGO row type: %s", type(row0))
    return None, None


def add_soil_to_grid(
    grid_df: pd.DataFrame,
    settings: AgrifieldSettings | None = None,
) -> pd.DataFrame:
    """Add ``soil_musym`` and ``soil_muname`` columns by querying SSURGO per acre."""
    settings = settings or AgrifieldSettings()
    df = grid_df.copy()

    musyms: list[str | None] = []
    munames: list[str | None] = []

    for idx in tqdm(range(len(df)), desc="Querying SSURGO"):
        lat = df.loc[idx, "lat"]
        lon = df.loc[idx, "lon"]
        musym, muname = query_ssurgo(lat, lon, settings)
        musyms.append(musym)
        munames.append(muname)
        time.sleep(settings.ssurgo_rate_limit)

    df["soil_musym"] = musyms
    df["soil_muname"] = munames
    return df
