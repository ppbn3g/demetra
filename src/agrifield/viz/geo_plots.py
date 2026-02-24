"""Spatial / satellite yield visualizations."""

from __future__ import annotations

import logging
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure
from shapely.geometry import box

logger = logging.getLogger(__name__)


def grid_to_geodataframe(grid_df: pd.DataFrame) -> gpd.GeoDataFrame:
    """Convert an acre grid DataFrame to a GeoDataFrame with polygon geometries."""
    geometries = [
        box(row.x_min, row.y_min, row.x_max, row.y_max)
        for row in grid_df.itertuples()
    ]
    gdf = gpd.GeoDataFrame(grid_df.copy(), geometry=geometries, crs="EPSG:32615")
    return gdf


def plot_yield_satellite(
    grid_df: pd.DataFrame,
    title: str = "Acre-Level Yield on Satellite Imagery",
    save_path: Path | None = None,
) -> Figure:
    """Plot yield as coloured acre polygons on a satellite basemap."""
    import contextily as ctx

    gdf_utm = grid_to_geodataframe(grid_df)
    gdf_web = gdf_utm.to_crs(epsg=3857)

    fig, ax = plt.subplots(figsize=(10, 10))
    gdf_web.plot(
        column="mean_yield_bu_ac",
        ax=ax,
        cmap="RdYlGn",
        edgecolor="black",
        linewidth=0.5,
        legend=True,
        alpha=0.6,
    )
    ctx.add_basemap(ax, crs=gdf_web.crs.to_string(), source=ctx.providers.Esri.WorldImagery)
    ax.set_axis_off()
    ax.set_title(title, fontsize=14)

    if save_path is not None:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        logger.info("Saved satellite plot to %s", save_path)

    return fig


def plot_yield_grid(
    grid_df: pd.DataFrame,
    title: str = "Acre-Level Yield (Axes in Acres)",
    save_path: Path | None = None,
) -> Figure:
    """Plot yield as a colour-coded grid in acre-index coordinates."""
    import matplotlib.patches as patches

    df = grid_df.copy()
    x_vals = sorted(df["x_min"].unique())
    y_vals = sorted(df["y_min"].unique())

    x_map = {v: i for i, v in enumerate(x_vals)}
    y_map = {v: i for i, v in enumerate(y_vals)}
    df["grid_x"] = df["x_min"].map(x_map)
    df["grid_y"] = df["y_min"].map(y_map)

    fig, ax = plt.subplots(figsize=(10, 10))
    cmap = plt.colormaps["RdYlGn"]
    min_yield = df["mean_yield_bu_ac"].min()
    max_yield = df["mean_yield_bu_ac"].max()
    rng = max_yield - min_yield if max_yield > min_yield else 1.0

    for row in df.itertuples():
        norm = (row.mean_yield_bu_ac - min_yield) / rng
        rect = patches.Rectangle(
            (row.grid_x, row.grid_y), 1, 1,
            linewidth=0.5, edgecolor="black", facecolor=cmap(norm),
        )
        ax.add_patch(rect)
        ax.text(row.grid_x + 0.5, row.grid_y + 0.5, str(int(row.mean_yield_bu_ac)),
                ha="center", va="center", fontsize=8)

    ax.set_aspect("equal")
    ax.set_xlabel("Acre Column Index")
    ax.set_ylabel("Acre Row Index")
    ax.set_title(title)
    ax.set_xlim(0, len(x_vals))
    ax.set_ylim(0, len(y_vals))

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=min_yield, vmax=max_yield))
    sm._A = []  # noqa: SLF001
    fig.colorbar(sm, ax=ax, label="Yield (bu/ac)")

    if save_path is not None:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        logger.info("Saved grid plot to %s", save_path)

    return fig
