# AgriField — Project Instructions for Claude Code

## Project Overview
Agricultural field data analytics package. Predicts crop yield at acre-level resolution
using machine learning, integrating John Deere yield monitor data, nitrogen application
records, Open-Meteo weather data, and USDA SSURGO soil data.

## Architecture
- `src/agrifield/` — pip-installable package (src layout)
- `configs/` — per-field YAML configs (one per farm/field/season)
- `data/` — git-ignored, raw shapefiles + processed CSVs
- `tests/` — pytest test suite

### Module Map
| Module | Responsibility |
|--------|---------------|
| `config/settings.py` | Pydantic-settings: thresholds, API URLs, CRS codes |
| `config/field_config.py` | Per-field YAML config dataclass |
| `ingest/yield_loader.py` | Load + clean John Deere yield shapefiles |
| `ingest/nitrogen_loader.py` | Load + combine nitrogen application shapefiles |
| `geo/transforms.py` | Coordinate transformations (WGS84 ↔ UTM) |
| `geo/constants.py` | CRS codes, acre dimensions |
| `grid/builder.py` | Build acre grid, assign yield points |
| `grid/operations.py` | Filter phantom acres, merge nitrogen |
| `external/weather.py` | Open-Meteo ERA5 rainfall API |
| `external/soil.py` | USDA SSURGO soil API |
| `modeling/features.py` | Feature matrix construction |
| `modeling/evaluation.py` | Train/test + K-fold CV evaluation |
| `modeling/comparison.py` | Multi-model comparison runner |
| `modeling/nitrogen.py` | Quadratic nitrogen response curve |
| `viz/geo_plots.py` | Spatial/satellite yield visualizations |
| `viz/model_plots.py` | Model result plots |
| `pipeline.py` | End-to-end data preparation orchestrator |
| `cli.py` | Click CLI entry points |

## Coding Conventions — ALWAYS follow these

### Logging, not printing
- NEVER use `print()` in library code. Use `logging.getLogger(__name__)`.
- `logger.info()` for progress, `logger.warning()` for recoverable issues, `logger.error()` for failures.

### Type hints
- Every function MUST have full type annotations on parameters and return type.
- Use `from __future__ import annotations` at top of every module.

### Vectorized operations
- NEVER use `while i < len(...)` loops for data processing. Use pandas/numpy vectorized ops.
- Use `for item in iterable` when iteration is necessary.
- Coordinate transforms use batch `transformer.transform(xs, ys)`, not one-at-a-time loops.

### Settings injection
- Functions that use configurable values accept `settings: AgrifieldSettings | None = None`.
- Default to `AgrifieldSettings()` when None is passed.
- NEVER hardcode API URLs, thresholds, or CRS codes inside functions.

### Plot functions
- NEVER call `plt.show()` inside library code. Return the `Figure` object.
- Accept optional `save_path: Path | None = None` parameter.
- The caller (CLI or notebook) decides to show or save.

### Imports
- Use absolute imports: `from agrifield.geo.transforms import transform_points`
- Group: stdlib → third-party → local, separated by blank lines.

### Naming
- Use "grid" not "block2" in all function/variable names.
- Use "field" not "block" for field-level concepts.
- Snake_case for functions and variables. PascalCase for classes.

## Data Rules
- `data/` is git-ignored. NEVER commit shapefiles, CSVs, or model artifacts.
- Raw data goes in `data/raw/{farm}_{field}_{season}/harvest/` and `.../nitrogen/`.
- Processed output goes in `data/processed/{farm}_{field}_{season}/`.
- Output CSV column names MUST match: mean_yield_bu_ac, mean_nitrogen_lb_ac, soil_musym, soil_muname, rainfall_in, lat, lon.

## Git Rules
- Commit messages: imperative mood, 50-char subject line.
- NEVER commit to main directly — use feature branches.
- NEVER force-push.
- Run `pytest tests/` before committing.

## Testing
- Every new function gets a test in the corresponding `tests/test_{module}/` directory.
- Use `pytest` with fixtures from `conftest.py`.
- Mock external API calls (Open-Meteo, SSURGO) — never hit real APIs in tests.

## Dependencies
- Manage via `pyproject.toml` optional groups: `[catboost]`, `[dev]`, `[all]`.
- CatBoost is optional — code MUST handle its absence gracefully.

## CLI
- Entry point: `agrifield` (defined in pyproject.toml).
- Commands: `prepare`, `model`, `inspect`, `plot`.
