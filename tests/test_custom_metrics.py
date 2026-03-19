import os
import pytest
from optimization_loop.loop import extract_metrics, extract_metric


class TestExtractMetrics:
    def test_extract_single_named_metric(self):
        output = "METRIC accuracy: 0.95\n"
        metrics = extract_metrics(output)
        assert metrics == {"accuracy": 0.95}

    def test_extract_multiple_named_metrics(self):
        output = "METRIC accuracy: 0.95\nMETRIC loss: 0.05\nMETRIC f1: 0.92\n"
        metrics = extract_metrics(output)
        assert metrics == {"accuracy": 0.95, "loss": 0.05, "f1": 0.92}

    def test_extract_default_metric(self):
        output = "METRIC: 0.95\n"
        metrics = extract_metrics(output)
        assert metrics == {"metric": 0.95}

    def test_extract_mixed(self):
        output = "METRIC: 0.80\nMETRIC accuracy: 0.95\n"
        metrics = extract_metrics(output)
        assert "metric" in metrics
        assert "accuracy" in metrics

    def test_last_value_wins(self):
        output = "METRIC accuracy: 0.80\nMETRIC accuracy: 0.95\n"
        metrics = extract_metrics(output)
        assert metrics["accuracy"] == 0.95

    def test_no_metrics(self):
        output = "No metric here\n"
        metrics = extract_metrics(output)
        assert metrics == {}

    def test_backward_compat_extract_metric(self):
        output = "METRIC: 0.95\n"
        assert extract_metric(output) == 0.95

    def test_extract_metrics_negative(self):
        output = "METRIC loss: -3.14\n"
        metrics = extract_metrics(output)
        assert metrics["loss"] == -3.14


class TestCustomMetricsConfig:
    def test_config_with_metrics_list(self):
        from optimization_loop.config import validate_config
        data = {
            "name": "test",
            "metric_name": "accuracy",
            "metric_direction": "max",
            "time_budget_seconds": 60,
            "prepare_script": "prepare.py",
            "train_script": "train.py",
            "program_file": "program.md",
            "metrics": [
                {"name": "accuracy", "direction": "max"},
                {"name": "loss", "direction": "min"},
            ],
        }
        config = validate_config(data)
        assert len(config["metrics"]) == 2

    def test_config_without_metrics_list_still_works(self):
        from optimization_loop.config import validate_config
        data = {
            "name": "test",
            "metric_name": "accuracy",
            "metric_direction": "max",
            "time_budget_seconds": 60,
            "prepare_script": "prepare.py",
            "train_script": "train.py",
            "program_file": "program.md",
        }
        config = validate_config(data)
        assert "metrics" not in config or config.get("metrics") is None
