"""Parallel execution of optimization iterations using ThreadPoolExecutor."""
from __future__ import annotations

import os
import sys
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from .loop import extract_metric
from .results import write_result

_file_lock = threading.Lock()


def _run_single_iteration(
    train_path: str,
    timeout: int,
    project_dir: str,
    index: int,
) -> dict:
    """Run a single train script iteration and return the result dict."""
    try:
        result = subprocess.run(
            [sys.executable, train_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=project_dir,
            check=True,
        )
        output = result.stdout
        metric = extract_metric(output)
        if metric is None:
            return {
                "index": index,
                "metric": None,
                "status": "no_metric",
                "description": "No METRIC found in output",
            }
        return {
            "index": index,
            "metric": metric,
            "status": "completed",
            "description": f"Parallel run {index}",
        }
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        return {
            "index": index,
            "metric": None,
            "status": "error",
            "description": str(e)[:100],
        }


def run_parallel_iterations(
    config: dict,
    project_dir: str,
    num_parallel: int = 2,
    timeout: int | None = None,
) -> list[dict]:
    """Run multiple optimization iterations in parallel.

    Args:
        config: Project config dict.
        project_dir: Path to the project directory.
        num_parallel: Number of parallel workers.
        timeout: Per-iteration timeout in seconds.

    Returns:
        List of result dicts from each parallel run.
    """
    train_path = os.path.join(project_dir, config["train_script"])
    if timeout is None:
        timeout = int(config["time_budget_seconds"])
    results_path = os.path.join(project_dir, "results.tsv")

    results = []
    with ThreadPoolExecutor(max_workers=num_parallel) as executor:
        futures = {
            executor.submit(
                _run_single_iteration, train_path, timeout, project_dir, i
            ): i
            for i in range(num_parallel)
        }
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            # Thread-safe write to results file
            if result["metric"] is not None:
                with _file_lock:
                    write_result(
                        results_path,
                        "parallel",
                        result["metric"],
                        result["status"],
                        result["description"],
                    )

    results.sort(key=lambda r: r["index"])
    return results
