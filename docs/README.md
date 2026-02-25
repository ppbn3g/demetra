# Demetra

Acre-level crop yield prediction using machine learning. Integrates John Deere yield
monitor data, nitrogen application records, Open-Meteo weather data, and USDA SSURGO
soil data.

## Setup (New Machine)

### Prerequisites

- Python 3.10+
- Git
- GitHub access to this repo

### 1. Clone and install

```bash
git clone https://github.com/ppbn3g/demetra.git
cd demetra
pip install -e ".[all]"
```

### 2. Add Python Scripts to PATH

The `demetra` CLI won't work until the Python Scripts directory is on your PATH.

**Windows (PowerShell — run once, persists across reboots):**

```powershell
$scripts = python -c "import sysconfig; print(sysconfig.get_path('scripts', 'nt_user'))"
$current = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($current -notlike "*$scripts*") {
    [Environment]::SetEnvironmentVariable('Path', "$current;$scripts", 'User')
    Write-Host "Added $scripts to PATH. Restart your terminal."
}
```

Then restart your terminal and verify:

```bash
demetra --help
```

### 3. Copy data files

Data is git-ignored — copy it from OneDrive, USB, etc. into this structure:

```
data/
├── raw/
│   └── bob_mueller_2025/
│       ├── harvest/          # Yield shapefiles (.shp, .dbf, .shx, .prj, .cpg)
│       └── nitrogen/         # N application shapefiles
└── processed/
    └── bob_mueller_2025/
        └── acre_dataset.csv  # Pre-built dataset (optional)
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
demetra prepare configs/bob_mueller_2025.yaml
```

4. Run model comparison:

```bash
demetra model data/processed/bob_mueller_2025/acre_dataset.csv
```

5. Generate plots:

```bash
demetra plot data/processed/bob_mueller_2025/acre_dataset.csv --type satellite
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `demetra prepare <config.yaml>` | Run full data prep pipeline |
| `demetra model <dataset.csv>` | Run model comparison |
| `demetra inspect <dataset.csv>` | Print predictor summaries |
| `demetra plot <dataset.csv> --type <type>` | Generate plots (satellite, grid, soil, nitrogen) |

## Development

```bash
pip install -e ".[dev]"
pytest tests/
```

## 6-Month Roadmap

Demetra is evolving into a commercial-grade agricultural intelligence platform integrating
drone imagery, probabilistic weather modeling, and acre-level risk analytics.

**Phase 1 — Data Infrastructure**
- Standardize historical drone imagery
- Build acre-to-imagery alignment engine

**Phase 2 — Baseline Imagery Modeling**
- Integrate NDVI and texture features
- Quantify performance lift vs. tabular-only models

**Phase 3 — Deep Learning**
- Train patch-based CNN/ViT models
- Implement spatially robust validation

**Phase 4 — Probabilistic Weather & Risk**
- Replace deterministic weather with distribution-based features
- Generate yield quantiles and downside risk maps

**Phase 5 — Application Backend**
- Deploy FastAPI service layer
- Standardize result artifacts and job management

**Phase 6 — AI Insights & UI**
- Generate grounded AI summaries from computed metrics
- Release simplified frontend with guided workflow

**Goal:** Deliver a deployable, acre-level yield and risk intelligence system with
vision + weather uncertainty + commercial usability.

See [ROADMAP.md](ROADMAP.md) for the full detailed roadmap.
