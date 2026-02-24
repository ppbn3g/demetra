"""Click CLI entry points for agrifield."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import click

logger = logging.getLogger(__name__)


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Enable debug logging.")
def main(verbose: bool) -> None:
    """AgriField — agricultural field data analytics CLI."""
    _configure_logging(verbose)


# ---------------------------------------------------------------------------
# prepare
# ---------------------------------------------------------------------------

@main.command()
@click.argument("config_yaml", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), default=None, help="Override output CSV path.")
def prepare(config_yaml: str, output: str | None) -> None:
    """Run the data preparation pipeline for a field config."""
    from agrifield.config.field_config import FieldConfig
    from agrifield.config.settings import AgrifieldSettings
    from agrifield.pipeline import build_field_dataset

    config = FieldConfig.from_yaml(config_yaml)
    if output is not None:
        config.output_dir = Path(output).parent
    settings = AgrifieldSettings()

    df = build_field_dataset(config, settings)
    click.echo(f"Done. {len(df)} acres written to {config.output_dir / 'acre_dataset.csv'}")


# ---------------------------------------------------------------------------
# model
# ---------------------------------------------------------------------------

@main.command()
@click.argument("dataset_csv", type=click.Path(exists=True))
@click.option("--coords/--no-coords", default=True, help="Include lat/lon features.")
@click.option("-o", "--output-dir", type=click.Path(), default=None, help="Directory for output.")
def model(dataset_csv: str, coords: bool, output_dir: str | None) -> None:
    """Run model comparison on a prepared dataset."""
    from agrifield.modeling.comparison import run_model_comparison
    from agrifield.modeling.data import load_dataset

    df = load_dataset(dataset_csv)
    results_df, _fitted = run_model_comparison(df, use_coords=coords)

    click.echo("\n=== MODEL COMPARISON (use_coords={}) ===".format(coords))
    click.echo(results_df.sort_values("test_r2", ascending=False).reset_index(drop=True).to_string())

    if output_dir is not None:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        results_df.to_csv(out / "model_comparison.csv", index=False)
        click.echo(f"Saved results to {out / 'model_comparison.csv'}")


# ---------------------------------------------------------------------------
# inspect
# ---------------------------------------------------------------------------

@main.command()
@click.argument("dataset_csv", type=click.Path(exists=True))
def inspect(dataset_csv: str) -> None:
    """Print predictor summaries for a dataset."""
    from agrifield.modeling.data import inspect_predictors, load_dataset

    df = load_dataset(dataset_csv)
    stats = inspect_predictors(df)
    for col, info in stats.items():
        click.echo(f"\n======== {col} ========")
        for k, v in info["describe"].items():  # type: ignore[union-attr]
            click.echo(f"  {k}: {v}")
        click.echo(f"  missing: {info['missing']}")


# ---------------------------------------------------------------------------
# plot
# ---------------------------------------------------------------------------

@main.command()
@click.argument("dataset_csv", type=click.Path(exists=True))
@click.option("--type", "plot_type", required=True,
              type=click.Choice(["satellite", "grid", "soil", "nitrogen"]),
              help="Type of plot to generate.")
@click.option("-s", "--save", type=click.Path(), default=None, help="Save plot to file.")
def plot(dataset_csv: str, plot_type: str, save: str | None) -> None:
    """Generate plots from a prepared dataset."""
    import matplotlib.pyplot as plt

    from agrifield.modeling.data import load_dataset

    df = load_dataset(dataset_csv)
    save_path = Path(save) if save else None

    if plot_type == "satellite":
        from agrifield.viz.geo_plots import plot_yield_satellite

        fig = plot_yield_satellite(df, save_path=save_path)

    elif plot_type == "grid":
        from agrifield.viz.geo_plots import plot_yield_grid

        fig = plot_yield_grid(df, save_path=save_path)

    elif plot_type == "soil":
        from agrifield.viz.model_plots import plot_yield_by_soil

        fig = plot_yield_by_soil(df, save_path=save_path)

    elif plot_type == "nitrogen":
        import numpy as np

        from agrifield.modeling.nitrogen import compute_optimal_n_rate, fit_quadratic_nitrogen
        from agrifield.viz.model_plots import plot_nitrogen_response

        result = fit_quadratic_nitrogen(df)
        if result is None:
            click.echo("Cannot fit nitrogen response — missing data.")
            sys.exit(1)

        b0, b1, b2, quad_model = result
        N_opt = compute_optimal_n_rate(b0, b1, b2)
        clean = df.dropna(subset=["mean_yield_bu_ac", "mean_nitrogen_lb_ac"])
        N = clean["mean_nitrogen_lb_ac"].values
        y = clean["mean_yield_bu_ac"].values
        fig = plot_nitrogen_response(N, y, quad_model, N_opt, save_path=save_path)

    if save is None:
        plt.show()
    else:
        click.echo(f"Plot saved to {save}")
