"""Load and combine nitrogen application shapefiles."""

from __future__ import annotations

import logging

import geopandas as gpd
import pandas as pd

from demetra.config.settings import demetraSettings
from demetra.geo.transforms import transform_points

logger = logging.getLogger(__name__)

NITROGEN_RATE_COLUMNS: list[str] = [
    "AppliedRate",
    "AppliedRate_1",
    "APPRATE",
    "PRODUCT1RATE",
    "RATE_N",
    "Nrate",
    "RX_N",
    "VRSOURCE1RATE",
    "AMTRATE1",
    "ControlRate",
]


def load_nitrogen_shapefile(
    shp_path: str,
    settings: demetraSettings | None = None,
) -> pd.DataFrame | None:
    """Load a single nitrogen application shapefile.

    Returns a DataFrame with columns ``x``, ``y``, ``nitrogen_lb_ac``,
    or ``None`` if no recognised rate column is found.
    """
    settings = settings or demetraSettings()

    gdf = gpd.read_file(shp_path)
    logger.info("Nitrogen shapefile columns for %s: %s", shp_path, list(gdf.columns))

    # Find the first matching nitrogen rate column
    n_col: str | None = None
    for col in NITROGEN_RATE_COLUMNS:
        if col in gdf.columns:
            n_col = col
            break

    if n_col is None:
        logger.error("No nitrogen rate column found in: %s (columns: %s)", shp_path, list(gdf.columns))
        return None

    logger.info("Using nitrogen rate column: %s from %s", n_col, shp_path)

    # Vectorized coordinate transform
    lons = gdf.geometry.x.values
    lats = gdf.geometry.y.values
    xs, ys = transform_points(lons, lats, settings.source_crs, settings.target_crs)

    df = pd.DataFrame({"x": xs, "y": ys, "nitrogen_lb_ac": gdf[n_col].values})
    logger.info("Nitrogen rate summary from %s:\n%s", shp_path, df["nitrogen_lb_ac"].describe())
    return df


def combine_multiple_n_files(
    shp_list: list[str],
    settings: demetraSettings | None = None,
) -> pd.DataFrame | None:
    """Load and combine multiple nitrogen shapefiles.

    Where multiple passes overlap at the same rounded location the rates are
    summed.
    """
    settings = settings or demetraSettings()

    dfs: list[pd.DataFrame] = []
    for path in shp_list:
        df_i = load_nitrogen_shapefile(path, settings)
        if df_i is not None:
            dfs.append(df_i)

    if not dfs:
        logger.warning("No nitrogen data found.")
        return None

    df_all = pd.concat(dfs, ignore_index=True)

    # Round coordinates to reduce floating-point mismatch between passes
    df_all["x_round"] = df_all["x"].round(1)
    df_all["y_round"] = df_all["y"].round(1)

    df_sum = (
        df_all.groupby(["x_round", "y_round"])["nitrogen_lb_ac"]
        .sum()
        .reset_index()
        .rename(columns={"x_round": "x", "y_round": "y"})
    )

    logger.info("Combined nitrogen dataset rows: %d", len(df_sum))
    return df_sum
