# AgriField

Acre-level crop yield prediction using machine learning. Integrates John Deere yield
monitor data, nitrogen application records, Open-Meteo weather data, and USDA SSURGO
soil data.

## Install

```bash
pip install -e ".[all]"
```

## Quickstart

1. Place raw shapefiles in `data/raw/{farm}_{field}_{season}/harvest/` and `.../nitrogen/`.
2. Create a field config in `configs/`:

```yaml
farm_name: Bob
field_name: Mueller
season: 2025
crop: corn
harvest_shapefile: data/raw/bob_mueller_2025/harvest/Blackburn_Bob_Mueller_Harvest_2025-09-03_00.shp
nitrogen_shapefiles:
  - data/raw/bob_mueller_2025/nitrogen/Blackburn_Bob_Mueller_Application_2024-11-25_00.shp
  - data/raw/bob_mueller_2025/nitrogen/Blackburn_Bob_Mueller_Application_2024-12-10_00.shp
growing_season_start: "2025-04-15"
growing_season_end: "2025-10-01"
```

3. Run the data preparation pipeline:

```bash
agrifield prepare configs/bob_mueller_2025.yaml
```

4. Run model comparison:

```bash
agrifield model data/processed/bob_mueller_2025/acre_dataset.csv
```

5. Generate plots:

```bash
agrifield plot data/processed/bob_mueller_2025/acre_dataset.csv --type satellite
```

## Development

```bash
pip install -e ".[dev]"
pytest tests/
```
