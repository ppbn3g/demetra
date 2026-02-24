"""Open-Meteo ERA5 rainfall API client with retry logic."""

from __future__ import annotations

import logging
import time

import numpy as np
import pandas as pd
import requests

from agrifield.config.settings import AgrifieldSettings
from agrifield.geo.transforms import get_field_centroid_latlon

logger = logging.getLogger(__name__)


def _request_with_retry(
    method: str,
    url: str,
    max_retries: int = 3,
    backoff: float = 2.0,
    **kwargs: object,
) -> requests.Response | None:
    """Execute an HTTP request with exponential backoff retries."""
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.request(method, url, **kwargs)
            if resp.status_code == 200:
                return resp
            logger.warning(
                "HTTP %d from %s (attempt %d/%d)",
                resp.status_code, url, attempt, max_retries,
            )
        except requests.RequestException as exc:
            logger.warning("Request error (attempt %d/%d): %s", attempt, max_retries, exc)

        if attempt < max_retries:
            wait = backoff ** attempt
            logger.info("Retrying in %.1f seconds...", wait)
            time.sleep(wait)

    logger.error("All %d attempts to %s failed.", max_retries, url)
    return None


def fetch_rainfall(
    lat: float,
    lon: float,
    start: str,
    end: str,
    settings: AgrifieldSettings | None = None,
) -> float:
    """Fetch total growing-season rainfall (inches) from Open-Meteo ERA5."""
    settings = settings or AgrifieldSettings()

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": "precipitation_sum",
        "timezone": "auto",
    }

    logger.info("Requesting rainfall: lat=%.4f lon=%.4f, %s to %s", lat, lon, start, end)

    resp = _request_with_retry(
        "GET",
        settings.open_meteo_url,
        max_retries=settings.open_meteo_max_retries,
        backoff=settings.open_meteo_backoff,
        params=params,
        timeout=settings.open_meteo_timeout,
    )

    if resp is None:
        return float("nan")

    data = resp.json()
    daily = data.get("daily", {})
    precip_list = daily.get("precipitation_sum")

    if precip_list is None:
        logger.warning("No precipitation_sum in Open-Meteo response.")
        return float("nan")

    # Vectorized sum, skipping None values
    arr = np.array(precip_list, dtype=float)
    total_rain_mm = float(np.nansum(arr))
    total_rain_in = total_rain_mm / 25.4

    logger.info("Total rainfall %s to %s = %.2f inches", start, end, total_rain_in)
    return total_rain_in


def add_rainfall_to_grid(
    grid_df: pd.DataFrame,
    shp_path: str,
    start: str,
    end: str,
    settings: AgrifieldSettings | None = None,
) -> pd.DataFrame:
    """Add a single rainfall value to all rows based on field centroid."""
    settings = settings or AgrifieldSettings()

    lat, lon = get_field_centroid_latlon(shp_path, settings)
    total_rain_in = fetch_rainfall(lat, lon, start, end, settings)

    df = grid_df.copy()
    df["rainfall_in"] = total_rain_in

    logger.info("Assigned rainfall_in = %.2f to %d acre rows.", total_rain_in, len(df))
    return df
