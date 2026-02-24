"""Load and clean John Deere yield monitor shapefiles."""

from __future__ import annotations

import logging

import geopandas as gpd
import pandas as pd

from agrifield.config.settings import AgrifieldSettings
from agrifield.geo.transforms import transform_points

logger = logging.getLogger(__name__)


def clean_jd_yield_dataframe(
    df_raw: pd.DataFrame,
    settings: AgrifieldSettings | None = None,
) -> pd.DataFrame:
    """Apply cleaning rules to a raw John Deere yield DataFrame.

    Filters are driven by *settings* thresholds so nothing is hardcoded.
    """
    settings = settings or AgrifieldSettings()
    df = df_raw.copy()

    # Valid yield range
    df = df[df["yield_bu_ac"] > 0]
    df = df[df["yield_bu_ac"] >= settings.yield_min]
    df = df[df["yield_bu_ac"] <= settings.yield_max]

    # Vehicle speed filter
    if "VEHICLSPEED" in df.columns:
        df = df[df["VEHICLSPEED"] > settings.speed_threshold]

    # Dry matter sensor failure
    if "DRYMATTER" in df.columns:
        df = df[df["DRYMATTER"] < settings.dry_matter_max]

    # Moisture filter
    if "Moisture" in df.columns:
        df = df[df["Moisture"] <= settings.moisture_max]

    df = df.reset_index(drop=True)
    logger.info("After cleaning, remaining rows: %d", len(df))
    return df


def load_yield_points(
    shp_path: str,
    farm_name: str,
    field_name: str,
    settings: AgrifieldSettings | None = None,
) -> pd.DataFrame:
    """Load a yield shapefile and return cleaned points with UTM coordinates."""
    settings = settings or AgrifieldSettings()

    gdf = gpd.read_file(shp_path)
    logger.info("JD shapefile columns: %s", list(gdf.columns))

    # Vectorized coordinate extraction + batch transform
    lons = gdf.geometry.x.values
    lats = gdf.geometry.y.values
    xs, ys = transform_points(lons, lats, settings.source_crs, settings.target_crs)

    gdf["x"] = xs
    gdf["y"] = ys

    # Rename yield column
    if "VRYIELDVOL" in gdf.columns:
        gdf = gdf.rename(columns={"VRYIELDVOL": "yield_bu_ac"})
    else:
        logger.warning("VRYIELDVOL column not found. Available: %s", list(gdf.columns))

    df = gdf[["x", "y", "yield_bu_ac"]].copy()
    df["farm"] = farm_name
    df["field"] = field_name

    # Preserve extra columns needed for cleaning
    for col in ("VEHICLSPEED", "DRYMATTER", "Moisture"):
        if col in gdf.columns:
            df[col] = gdf[col].values

    df_clean = clean_jd_yield_dataframe(df, settings)

    # Drop helper columns after cleaning
    df_clean = df_clean.drop(
        columns=[c for c in ("VEHICLSPEED", "DRYMATTER", "Moisture") if c in df_clean.columns],
    )
    return df_clean
