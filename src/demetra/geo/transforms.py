"""Coordinate transformation utilities — fully vectorized."""

from __future__ import annotations

import logging
from functools import lru_cache

import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import Transformer

from demetra.config.settings import demetraSettings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=16)
def get_transformer(src: str, dst: str) -> Transformer:
    """Return a cached pyproj Transformer for *src* → *dst* CRS codes."""
    return Transformer.from_crs(src, dst, always_xy=True)


def transform_points(
    xs: np.ndarray,
    ys: np.ndarray,
    src: str,
    dst: str,
) -> tuple[np.ndarray, np.ndarray]:
    """Batch-transform coordinate arrays from *src* to *dst* CRS.

    Parameters
    ----------
    xs, ys : array-like
        Input coordinates (e.g. longitude, latitude).
    src, dst : str
        EPSG codes such as ``"EPSG:4326"`` or ``"EPSG:32615"``.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Transformed (x, y) arrays.
    """
    transformer = get_transformer(src, dst)
    xs_out, ys_out = transformer.transform(np.asarray(xs, dtype=float), np.asarray(ys, dtype=float))
    return np.asarray(xs_out), np.asarray(ys_out)


def get_field_centroid_latlon(
    shp_path: str,
    settings: demetraSettings | None = None,
) -> tuple[float, float]:
    """Return (lat, lon) of the centroid of all geometries in *shp_path*."""
    settings = settings or demetraSettings()
    gdf = gpd.read_file(shp_path)
    if gdf.crs is None:
        gdf = gdf.set_crs(settings.source_crs)
    centroid = gdf.geometry.union_all().centroid
    lat, lon = centroid.y, centroid.x
    logger.info("Field centroid (lat, lon): %.6f, %.6f", lat, lon)
    return lat, lon


def add_latlon_to_grid(
    grid_df: pd.DataFrame,
    settings: demetraSettings | None = None,
) -> pd.DataFrame:
    """Add ``lat`` and ``lon`` columns to *grid_df* from UTM cell centres."""
    settings = settings or demetraSettings()
    df = grid_df.copy()
    cx = ((df["x_min"] + df["x_max"]) / 2.0).values
    cy = ((df["y_min"] + df["y_max"]) / 2.0).values
    lons, lats = transform_points(cx, cy, settings.target_crs, settings.source_crs)
    df["lat"] = lats
    df["lon"] = lons
    return df
