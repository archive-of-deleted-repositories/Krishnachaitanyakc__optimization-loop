"""Parse and write results.tsv files."""
from __future__ import annotations

import os

HEADER = "commit\tmetric_value\tstatus\tdescription"


def write_result(path: str, commit: str, metric_value: float, status: str, description: str) -> None:
    """Append a result row to the results.tsv file."""
    file_exists = os.path.exists(path)
    with open(path, "a") as f:
        if not file_exists:
            f.write(HEADER + "\n")
        f.write(f"{commit}\t{metric_value}\t{status}\t{description}\n")


def parse_results(path: str) -> list[dict]:
    """Parse a results.tsv file into a list of dicts."""
    if not os.path.exists(path):
        return []

    results = []
    with open(path) as f:
        lines = f.readlines()

    if len(lines) <= 1:
        return []

    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) >= 4:
            results.append({
                "commit": parts[0],
                "metric_value": float(parts[1]),
                "status": parts[2],
                "description": parts[3],
            })

    return results


def format_results_table(results: list[dict]) -> str:
    """Format results as a readable table string."""
    if not results:
        return "No results yet."

    header = f"{'Commit':<12} {'Metric':>10} {'Status':<12} Description"
    sep = "-" * 60
    lines = [header, sep]

    for r in results:
        commit = r["commit"][:10]
        metric = f"{r['metric_value']:.4f}"
        lines.append(f"{commit:<12} {metric:>10} {r['status']:<12} {r['description']}")

    return "\n".join(lines)
