"""Main optimization loop: modify, run, eval, keep/discard."""
from __future__ import annotations

import os
import re
import subprocess
import sys


def extract_metric(output: str) -> float | None:
    """Extract the last METRIC value from script output."""
    matches = re.findall(r"^METRIC:\s*([+-]?\d+(?:\.\d+)?)", output, re.MULTILINE)
    if not matches:
        return None
    return float(matches[-1])


def is_improvement(new_value: float, best_value: float | None, direction: str) -> bool:
    """Check if new_value is an improvement over best_value."""
    if best_value is None:
        return True
    if direction == "max":
        return new_value > best_value
    else:
        return new_value < best_value


def run_script(script_path: str, timeout: int = 60, cwd: str | None = None) -> str:
    """Run a Python script and return its stdout output."""
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd or os.path.dirname(os.path.abspath(script_path)),
        check=True,
    )
    return result.stdout


def run_optimization_loop(
    config: dict,
    project_dir: str,
    max_iterations: int = 1,
) -> list[dict]:
    """Run the optimization loop.

    Returns a list of iteration result dicts.
    """
    from .results import write_result

    results_path = os.path.join(project_dir, "results.tsv")
    prepare_path = os.path.join(project_dir, config["prepare_script"])
    train_path = os.path.join(project_dir, config["train_script"])
    timeout = int(config["time_budget_seconds"])
    direction = config["metric_direction"]

    # Run prepare once
    if os.path.exists(prepare_path):
        run_script(prepare_path, timeout=timeout, cwd=project_dir)

    best_value = None
    iteration_results = []

    for i in range(max_iterations):
        try:
            output = run_script(train_path, timeout=timeout, cwd=project_dir)
            metric = extract_metric(output)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            iteration_results.append({
                "iteration": i,
                "metric": None,
                "status": "error",
                "description": str(e)[:100],
            })
            continue

        if metric is None:
            iteration_results.append({
                "iteration": i,
                "metric": None,
                "status": "no_metric",
                "description": "No METRIC found in output",
            })
            continue

        if is_improvement(metric, best_value, direction):
            status = "improved"
            best_value = metric
            # Try git commit
            commit_hash = _git_commit(project_dir, f"Iteration {i}: {config['metric_name']}={metric}")
        else:
            status = "discarded"
            commit_hash = "none"

        write_result(results_path, commit_hash, metric, status, f"Iteration {i}")
        iteration_results.append({
            "iteration": i,
            "metric": metric,
            "status": status,
            "commit": commit_hash,
        })

    return iteration_results


def _git_commit(project_dir: str, message: str) -> str:
    """Create a git commit and return the short hash."""
    try:
        subprocess.run(["git", "add", "-A"], cwd=project_dir, capture_output=True, check=True)
        subprocess.run(
            ["git", "commit", "-m", message, "--allow-empty"],
            cwd=project_dir, capture_output=True, check=True,
        )
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=project_dir, capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "no-commit"
