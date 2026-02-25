# :round_pushpin: Six-Month Development Roadmap

## Demetra: Acre-Level Yield Prediction and Risk Intelligence Platform

---

### Strategic Objective

Over the next six months, Demetra will evolve from a structured acre-level ML pipeline
into a fully integrated, **commercial-grade agricultural intelligence system** incorporating:

- Multi-temporal drone imagery (RGB / NDVI / NIR)
- Probabilistic weather modeling
- Spatially robust yield prediction
- Acre-level risk quantification
- AI-assisted agronomic insights
- A guided, production-ready application interface

The objective is not merely model improvement, but the development of a **deployable,
scalable decision-support platform**.

---

## Phase I — Data Standardization & Alignment Infrastructure

> **Month 1** | Foundation layer for all downstream learning

### 1.1 Drone Data Audit and Inventory

- Catalog all historical drone imagery by farm, field, season, date, sensor type,
  resolution, and coverage.
- Confirm availability of multi-week and multi-year imagery for cross-season modeling.
- Identify data gaps to be filled during summer collection.

**Deliverables**

| Artifact | Description |
|----------|-------------|
| Drone metadata schema | Standardized format for all imagery metadata |
| Centralized inventory dataset | Single source of truth for available imagery |
| Naming & folder conventions | Documented file organization rules |

### 1.2 Acre-to-Imagery Alignment Engine

Develop a reproducible pipeline that:

1. Reprojects imagery into a standardized CRS
2. Aligns orthomosaics to the existing acre grid
3. Extracts per-acre raster windows or patches
4. Links imagery-derived features to corresponding yield targets

**Deliverables**

| Artifact | Description |
|----------|-------------|
| Imagery extraction module | `ingest/imagery_loader.py` |
| Acre-patch generation utilities | `grid/patch_extraction.py` |
| Persisted structured imagery datasets | Git-ignored, under `data/imagery/` |

> This stage establishes the **technical backbone** required for all downstream learning.

---

## Phase II — Controlled Summer Data Collection & Baseline Imagery Features

> **Month 2** | Incremental model lift before architectural complexity increases

### 2.1 Drone Collection Protocol (SOP)

Establish a standardized flight protocol:

- Fixed altitude and overlap
- Consistent time-of-day
- Defined growth-stage windows (e.g., V6, VT, R3, R5)
- Documented sensor calibration procedure

**Deliverable** — Formal drone data collection playbook

### 2.2 Engineered Imagery Features (Baseline Model)

Before deep learning, extract and integrate tabular imagery features:

| Feature Category | Examples |
|-----------------|----------|
| Vegetation indices | NDVI mean, variance, quantiles |
| Coverage metrics | Vegetation fraction, canopy coverage |
| Texture measures | GLCM entropy, contrast, homogeneity |
| Structural metrics | Edge density, row uniformity |

Integrate these into the current tabular ML pipeline
(`modeling/features.py` &rarr; `modeling/comparison.py`).

**Deliverables**

| Artifact | Description |
|----------|-------------|
| Imagery-enhanced baseline model | Tabular model with imagery features added |
| Comparative performance report | Side-by-side vs. non-imagery baseline |

> This phase ensures **incremental model lift** before architectural complexity increases.

---

## Phase III — Deep Learning Integration

> **Month 3** | Transition to hybrid tabular + vision modeling architecture

### 3.1 Patch-Based Acre Modeling

Develop a patch-level **CNN or Vision Transformer** model to predict:

- **Continuous yield** (regression)
- **Yield class** (classification, optional)

### 3.2 Spatially Robust Validation

Adopt deployment-consistent validation strategies:

| Strategy | Purpose |
|----------|---------|
| Leave-one-field-out | Tests generalization across fields |
| Leave-one-year-out | Tests temporal generalization |
| Spatial blocking | Prevents leakage from spatial autocorrelation |

**Deliverables**

| Artifact | Description |
|----------|-------------|
| Imagery model training pipeline | `modeling/vision.py` |
| Field-robust validation framework | `modeling/spatial_cv.py` |
| Versioned model artifacts | Stored under `models/` (git-ignored) |

> This phase transitions Demetra into a **hybrid tabular + vision modeling** architecture.

---

## Phase IV — Probabilistic Weather Integration & Risk Modeling

> **Month 4** | Differentiates Demetra as a risk intelligence system

### 4.1 Weather Distribution Features

Integrate probabilistic outputs from weather models:

| Feature | Description |
|---------|-------------|
| Window-specific rainfall quantiles | q10, q50, q90 per growth stage |
| Heat stress probabilities | P(daily max > threshold) |
| Dry spell likelihood metrics | Consecutive days below threshold |
| Scenario-aggregated risk scores | Composite weather risk index |

Replace deterministic weather inputs with **distribution-aware features**.

### 4.2 Yield Distribution Modeling

Shift from point prediction to:

- **Per-acre yield quantiles** (q10, q25, q50, q75, q90)
- **Downside probability metrics** (e.g., P(yield < breakeven))
- **Scenario-conditioned maps** (best-case, expected, worst-case)

**Deliverables**

| Artifact | Description |
|----------|-------------|
| Risk modeling module | `modeling/risk.py` |
| Scenario simulation utilities | `modeling/scenarios.py` |
| Acre-level uncertainty maps | `viz/risk_plots.py` |

> This stage differentiates Demetra as a **risk intelligence system** rather than
> a deterministic predictor.

---

## Phase V — Application Backend & Service Layer

> **Month 5** | Formalizes Demetra as a deployable product

### 5.1 API Layer

Implement a **FastAPI** service to:

- Upload field configurations
- Run preparation, modeling, and risk pipelines asynchronously
- Serve results programmatically

### 5.2 Standardized Output Artifacts

Define a consistent output contract:

| Artifact | Format | Description |
|----------|--------|-------------|
| Acre dataset | CSV / Parquet | Full feature table per acre |
| Risk summary | JSON | Aggregated risk metrics |
| Map layers | GeoJSON / PNG | Spatial visualizations |
| Insights report | Markdown | Human-readable summary |

**Deliverables**

| Artifact | Description |
|----------|-------------|
| Service wrapper | FastAPI application wrapping Demetra |
| Job execution system | Async task queue for pipeline runs |
| Artifact specification | Stable output schema documentation |

> This stage formalizes Demetra as a **deployable product**.

---

## Phase VI — AI Insight Layer & User Experience

> **Month 6** | Production-ready release with guided workflow

### 6.1 AI-Generated Insights (Grounded)

Use LLM systems **exclusively** for:

- Summarizing computed risk outputs
- Translating quantitative risk metrics into readable insights
- Highlighting key drivers using model metadata

> All recommendations **must reference concrete computed metrics**. No hallucinated advice.

### 6.2 Guided User Interface

Develop a simplified workflow:

```
Select field / season  -->  Upload datasets  -->  Run pipeline  -->  Review results
```

- Maps, risk metrics, and AI-generated insights in one view
- Maintain backend sophistication while exposing a **minimal, intuitive frontend**

### 6.3 Release Readiness

- [ ] Example configurations
- [ ] Demo dataset
- [ ] Documentation walkthrough
- [ ] Tagged release (`v1.0.0`)

---

## Success Criteria

| Criterion | Validation Method |
|-----------|-------------------|
| Acre-level imagery aligned across multiple seasons | Visual QA + alignment metrics |
| Performance lift from imagery + probabilistic weather | A/B comparison on holdout fields |
| Spatially robust validation performance | Leave-one-field-out R² and RMSE |
| Operational risk maps with stable downside identification | Backtested against historical outcomes |
| End-to-end application workflow without manual intervention | Full pipeline smoke test |

---

*Demetra &mdash; from structured prediction to agricultural intelligence.*
