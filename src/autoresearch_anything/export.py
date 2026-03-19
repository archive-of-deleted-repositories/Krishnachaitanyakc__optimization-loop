"""Export results to JSON, CSV, or TSV formats."""
from __future__ import annotations

import csv
import json

from .results import parse_results


def export_results(results_path: str, output_path: str, fmt: str) -> None:
    """Export results.tsv to the specified format.

    Args:
        results_path: Path to the results.tsv file.
        output_path: Path to write the exported file.
        fmt: One of 'json', 'csv', 'tsv'.
    """
    data = parse_results(results_path)

    if fmt == "json":
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
    elif fmt == "csv":
        _write_delimited(data, output_path, ",")
    elif fmt == "tsv":
        _write_delimited(data, output_path, "\t")
    else:
        raise ValueError(f"Unsupported format: {fmt}")


def _write_delimited(data: list[dict], path: str, delimiter: str) -> None:
    if not data:
        with open(path, "w") as f:
            f.write("")
        return
    fieldnames = list(data[0].keys())
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(data)
