"""Generate metric-over-time plots from results."""
from __future__ import annotations

import os

from .results import parse_results


def generate_plot(
    results_path: str,
    output_path: str | None = None,
    metric_name: str = "metric",
) -> str:
    """Read results.tsv and generate a metric-over-time line chart as PNG.

    Args:
        results_path: Path to the results.tsv file.
        output_path: Path for the output PNG. Defaults to results_path with .png extension.
        metric_name: Label for the y-axis.

    Returns:
        The path to the generated PNG file.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    data = parse_results(results_path)
    if not data:
        raise ValueError("No results to plot")

    if output_path is None:
        output_path = os.path.splitext(results_path)[0] + ".png"

    iterations = list(range(len(data)))
    values = [r["metric_value"] for r in data]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(iterations, values, marker="o", linewidth=2)
    ax.set_xlabel("Iteration")
    ax.set_ylabel(metric_name)
    ax.set_title(f"{metric_name} over iterations")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    return output_path
