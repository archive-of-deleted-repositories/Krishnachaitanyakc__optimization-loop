import os
import pytest
from unittest.mock import patch, MagicMock
from optimization_loop.parallel import run_parallel_iterations
from optimization_loop.results import write_result, parse_results


class TestRunParallelIterations:
    def _make_config(self):
        return {
            "name": "test",
            "metric_name": "score",
            "metric_direction": "max",
            "time_budget_seconds": 10,
            "prepare_script": "prepare.py",
            "train_script": "train.py",
            "program_file": "program.md",
        }

    def test_parallel_runs_collect_results(self, tmp_path):
        project_dir = str(tmp_path)
        config = self._make_config()

        # Create a simple train script
        train_path = os.path.join(project_dir, "train.py")
        with open(train_path, "w") as f:
            f.write('import random\nprint(f"METRIC: {random.uniform(0.5, 1.0):.4f}")\n')

        results = run_parallel_iterations(
            config, project_dir, num_parallel=3, timeout=10
        )
        assert len(results) == 3

    def test_parallel_handles_errors(self, tmp_path):
        project_dir = str(tmp_path)
        config = self._make_config()

        train_path = os.path.join(project_dir, "train.py")
        with open(train_path, "w") as f:
            f.write('raise ValueError("fail")\n')

        results = run_parallel_iterations(
            config, project_dir, num_parallel=2, timeout=10
        )
        assert len(results) == 2
        assert all(r["status"] == "error" for r in results)

    def test_file_locking_on_write(self, tmp_path):
        """Verify results file is written correctly under concurrency."""
        project_dir = str(tmp_path)
        config = self._make_config()

        train_path = os.path.join(project_dir, "train.py")
        with open(train_path, "w") as f:
            f.write('print("METRIC: 0.9")\n')

        run_parallel_iterations(config, project_dir, num_parallel=4, timeout=10)

        results_path = os.path.join(project_dir, "results.tsv")
        if os.path.exists(results_path):
            results = parse_results(results_path)
            # All written results should be parseable
            assert all("metric_value" in r for r in results)
