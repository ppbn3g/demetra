"""Global settings for AgriField, overridable via AGRIFIELD_* env vars."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class AgrifieldSettings(BaseSettings):
    """Centralized configuration for the agrifield package."""

    model_config = {"env_prefix": "AGRIFIELD_"}

    # --- CRS codes ---
    source_crs: str = "EPSG:4326"
    target_crs: str = "EPSG:32615"
    web_mercator_crs: str = "EPSG:3857"

    # --- Yield cleaning thresholds ---
    yield_min: float = 50.0
    yield_max: float = 350.0
    speed_threshold: float = 0.2235  # 0.5 mph in m/s
    dry_matter_max: float = 100.0
    moisture_max: float = 40.0

    # --- Grid defaults ---
    acre_side_meters: float = 63.6
    phantom_density: float = 0.15

    # --- Open-Meteo API ---
    open_meteo_url: str = "https://archive-api.open-meteo.com/v1/era5"
    open_meteo_timeout: int = 30
    open_meteo_max_retries: int = 3
    open_meteo_backoff: float = 2.0

    # --- SSURGO API ---
    ssurgo_url: str = "https://SDMDataAccess.sc.egov.usda.gov/Tabular/post.rest"
    ssurgo_timeout: int = 30
    ssurgo_rate_limit: float = 0.5
    ssurgo_max_retries: int = 3
    ssurgo_backoff: float = 2.0
