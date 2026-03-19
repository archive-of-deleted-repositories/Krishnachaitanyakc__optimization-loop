import os
import pytest
from autoresearch_anything.sweep import run_sweep, build_sweep_grid


class TestBuildSweepGrid:
    def test_single_param(self):
        sweep_config = [{"name": "lr", "values": [0.01, 0.001]}]
        grid = build_sweep_grid(sweep_config)
        assert len(grid) == 2
        assert {"lr": 0.01} in grid
        assert {"lr": 0.001} in grid

    def test_multiple_params(self):
        sweep_config = [
            {"name": "lr", "values": [0.01, 0.001]},
            {"name": "batch_size", "values": [16, 32]},
        ]
        grid = build_sweep_grid(sweep_config)
        assert len(grid) == 4

    def test_empty_config(self):
        grid = build_sweep_grid([])
        assert grid == [{}]


class TestRunSweep:
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

    def test_sweep_runs_all_combinations(self, tmp_path):
        project_dir = str(tmp_path)
        config = self._make_config()

        # Script reads env vars and outputs metric
        train_path = os.path.join(project_dir, "train.py")
        with open(train_path, "w") as f:
            f.write(
                'import os\n'
                'lr = float(os.environ.get("SWEEP_lr", "0.01"))\n'
                'print(f"METRIC: {lr}")\n'
            )

        sweep_config = [{"name": "lr", "values": [0.01, 0.1]}]
        results = run_sweep(config, project_dir, sweep_config, timeout=10)
        assert len(results) == 2

    def test_sweep_injects_env_vars(self, tmp_path):
        project_dir = str(tmp_path)
        config = self._make_config()

        train_path = os.path.join(project_dir, "train.py")
        with open(train_path, "w") as f:
            f.write(
                'import os\n'
                'val = os.environ.get("SWEEP_alpha", "missing")\n'
                'print(f"Got alpha={val}")\n'
                'print(f"METRIC: {float(val)}")\n'
            )

        sweep_config = [{"name": "alpha", "values": [0.5]}]
        results = run_sweep(config, project_dir, sweep_config, timeout=10)
        assert len(results) == 1
        assert results[0]["metric"] == 0.5
