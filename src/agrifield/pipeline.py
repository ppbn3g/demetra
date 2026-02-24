"""End-to-end data preparation orchestrator."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from agrifield.config.field_config import FieldConfig
from agrifield.config.settings import AgrifieldSettings
from agrifield.external.soil import add_soil_to_grid
from agrifield.external.weather import add_rainfall_to_grid
from agrifield.geo.transforms import add_latlon_to_grid
from agrifield.grid.builder import build_field_grid
from agrifield.grid.operations import filter_phantom_acres, merge_nitrogen_into_grid
from agrifield.ingest.nitrogen_loader import combine_multiple_n_files

logger = logging.getLogger(__name__)


def build_field_dataset(
    config: FieldConfig,
    settings: AgrifieldSettings | None = None,
) -> pd.DataFrame:
    """Run the full data-preparation pipeline for one field.

    Steps: load yield → build grid → filter → add rainfall → add lat/lon
    → add soil → merge nitrogen → save CSV.
    """
    settings = settings or AgrifieldSettings()

    # 1. Build acre grid from yield shapefile
    logger.info("Building acre grid from %s", config.harvest_shapefile)
    grid = build_field_grid(
        str(config.harvest_shapefile),
        config.farm_name,
        config.field_name,
        config.cell_size_meters,
        config.units,
        settings,
    )

    # 2. Remove phantom / edge acres
    grid = filter_phantom_acres(grid, settings.phantom_density)

    # 3. Add rainfall (single value for the whole field)
    grid = add_rainfall_to_grid(
        grid,
        str(config.harvest_shapefile),
        config.growing_season_start,
        config.growing_season_end,
        settings,
    )

    # 4. Add lat/lon from UTM centres
    grid = add_latlon_to_grid(grid, settings)

    # 5. Add SSURGO soil attributes
    grid = add_soil_to_grid(grid, settings)

    # 6. Merge nitrogen if shapefiles provided
    if config.nitrogen_shapefiles:
        n_paths = [str(p) for p in config.nitrogen_shapefiles]
        nitrogen_df = combine_multiple_n_files(n_paths, settings)
        if nitrogen_df is not None:
            grid = merge_nitrogen_into_grid(grid, nitrogen_df)
    else:
        logger.info("No nitrogen shapefiles provided — skipping nitrogen merge.")

    # 7. Save output CSV
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "acre_dataset.csv"
    grid.to_csv(output_path, index=False)
    logger.info("Saved acre-level dataset to %s (%d rows)", output_path, len(grid))

    return grid
