"""Load and validate YAML project configs."""

import yaml


class ConfigError(Exception):
    """Raised when config is invalid."""
    pass


REQUIRED_FIELDS = [
    "name",
    "metric_name",
    "metric_direction",
    "time_budget_seconds",
    "prepare_script",
    "train_script",
    "program_file",
]


def load_config(path: str) -> dict:
    """Load a YAML config file and validate it."""
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        raise
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML in {path}: {e}")

    if not isinstance(data, dict):
        raise ConfigError(f"Config must be a YAML mapping, got {type(data).__name__}")

    return validate_config(data)


def validate_config(data: dict) -> dict:
    """Validate a config dictionary."""
    for field in REQUIRED_FIELDS:
        if field not in data:
            raise ConfigError(f"Missing required field: {field}")

    if data["metric_direction"] not in ("min", "max"):
        raise ConfigError(
            f"metric_direction must be 'min' or 'max', got '{data['metric_direction']}'"
        )

    if not isinstance(data["time_budget_seconds"], (int, float)) or data["time_budget_seconds"] <= 0:
        raise ConfigError(
            f"time_budget_seconds must be a positive number, got {data['time_budget_seconds']}"
        )

    return data
