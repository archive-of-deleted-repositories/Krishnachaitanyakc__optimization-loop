import os
import tempfile
import pytest
import yaml
from optimization_loop.config import load_config, validate_config, ConfigError


def _write_config(tmp_path, data):
    path = os.path.join(tmp_path, "config.yaml")
    with open(path, "w") as f:
        yaml.dump(data, f)
    return path


class TestLoadConfig:
    def test_load_valid_config(self, tmp_path):
        data = {
            "name": "test-project",
            "metric_name": "accuracy",
            "metric_direction": "max",
            "time_budget_seconds": 30,
            "prepare_script": "prepare.py",
            "train_script": "train.py",
            "program_file": "program.md",
        }
        path = _write_config(str(tmp_path), data)
        config = load_config(path)
        assert config["name"] == "test-project"
        assert config["metric_direction"] == "max"
        assert config["time_budget_seconds"] == 30

    def test_load_missing_file(self):
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/config.yaml")

    def test_load_invalid_yaml(self, tmp_path):
        path = os.path.join(str(tmp_path), "config.yaml")
        with open(path, "w") as f:
            f.write(": invalid: yaml: {{{}}}][")
        with pytest.raises(ConfigError):
            load_config(path)


class TestValidateConfig:
    def test_valid_config(self):
        data = {
            "name": "test",
            "metric_name": "score",
            "metric_direction": "max",
            "time_budget_seconds": 60,
            "prepare_script": "prepare.py",
            "train_script": "train.py",
            "program_file": "program.md",
        }
        config = validate_config(data)
        assert config["name"] == "test"

    def test_missing_required_field(self):
        data = {"name": "test"}
        with pytest.raises(ConfigError, match="metric_name"):
            validate_config(data)

    def test_invalid_metric_direction(self):
        data = {
            "name": "test",
            "metric_name": "score",
            "metric_direction": "sideways",
            "time_budget_seconds": 60,
            "prepare_script": "prepare.py",
            "train_script": "train.py",
            "program_file": "program.md",
        }
        with pytest.raises(ConfigError, match="metric_direction"):
            validate_config(data)

    def test_invalid_time_budget(self):
        data = {
            "name": "test",
            "metric_name": "score",
            "metric_direction": "min",
            "time_budget_seconds": -5,
            "prepare_script": "prepare.py",
            "train_script": "train.py",
            "program_file": "program.md",
        }
        with pytest.raises(ConfigError, match="time_budget"):
            validate_config(data)
