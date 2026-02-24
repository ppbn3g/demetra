"""Per-field YAML configuration dataclass."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class FieldConfig:
    """Configuration for a single farm/field/season run."""

    farm_name: str
    field_name: str
    season: int
    crop: str
    harvest_shapefile: Path
    nitrogen_shapefiles: list[Path]
    growing_season_start: str
    growing_season_end: str
    cell_size_meters: float = 63.6
    units: str = "meters"
    output_dir: Path = field(default_factory=lambda: Path("data/processed"))

    @classmethod
    def from_yaml(cls, path: str | Path) -> FieldConfig:
        """Load a FieldConfig from a YAML file."""
        path = Path(path)
        with open(path) as f:
            raw = yaml.safe_load(f)

        return cls(
            farm_name=raw["farm_name"],
            field_name=raw["field_name"],
            season=int(raw["season"]),
            crop=raw["crop"],
            harvest_shapefile=Path(raw["harvest_shapefile"]),
            nitrogen_shapefiles=[Path(p) for p in raw.get("nitrogen_shapefiles", [])],
            growing_season_start=raw["growing_season_start"],
            growing_season_end=raw["growing_season_end"],
            cell_size_meters=float(raw.get("cell_size_meters", 63.6)),
            units=raw.get("units", "meters"),
            output_dir=Path(raw.get("output_dir", f"data/processed/{raw['farm_name'].lower()}_{raw['field_name'].lower()}_{raw['season']}")),
        )
