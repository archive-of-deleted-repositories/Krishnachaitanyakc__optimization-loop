"""Hyperparameter sweep via grid search."""
from __future__ import annotations

import itertools
import os
import subprocess
import sys

from .loop import extract_metric


def build_sweep_grid(sweep_config: list[dict]) -> list[dict]:
    """Build a grid of all parameter combinations.

    Args:
        sweep_config: List of dicts with 'name' and 'values' keys.

    Returns:
        List of dicts, each mapping param name to a value.
    """
    if not sweep_config:
        return [{}]

    names = [p["name"] for p in sweep_config]
    value_lists = [p["values"] for p in sweep_config]
    combos = list(itertools.product(*value_lists))
    return [dict(zip(names, combo)) for combo in combos]


def run_sweep(
    config: dict,
    project_dir: str,
    sweep_config: list[dict],
    timeout: int | None = None,
) -> list[dict]:
    """Run a hyperparameter sweep over all parameter combinations.

    Parameters are injected as SWEEP_<name> environment variables.

    Args:
        config: Project config dict.
        project_dir: Project directory path.
        sweep_config: List of dicts with 'name' and 'values' keys.
        timeout: Per-run timeout in seconds.

    Returns:
        List of result dicts with params, metric, and status.
    """
    train_path = os.path.join(project_dir, config["train_script"])
    if timeout is None:
        timeout = int(config["time_budget_seconds"])

    grid = build_sweep_grid(sweep_config)
    results = []

    for params in grid:
        env = os.environ.copy()
        for name, value in params.items():
            env[f"SWEEP_{name}"] = str(value)

        try:
            proc = subprocess.run(
                [sys.executable, train_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=project_dir,
                env=env,
                check=True,
            )
            metric = extract_metric(proc.stdout)
            results.append({
                "params": params,
                "metric": metric,
                "status": "completed" if metric is not None else "no_metric",
                "output": proc.stdout,
            })
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            results.append({
                "params": params,
                "metric": None,
                "status": "error",
                "output": str(e)[:200],
            })

    return results
