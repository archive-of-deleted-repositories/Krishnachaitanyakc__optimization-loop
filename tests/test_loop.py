import os
import subprocess
import pytest
from autoresearch_anything.loop import extract_metric, is_improvement, run_script


class TestExtractMetric:
    def test_extract_from_stdout(self):
        output = "Loading data...\nTraining...\nMETRIC: 0.95\n"
        assert extract_metric(output) == 0.95

    def test_extract_last_metric(self):
        output = "METRIC: 0.80\nRetrying...\nMETRIC: 0.95\n"
        assert extract_metric(output) == 0.95

    def test_no_metric_found(self):
        output = "No metric here\nJust logs\n"
        assert extract_metric(output) is None

    def test_extract_negative_metric(self):
        output = "METRIC: -3.14\n"
        assert extract_metric(output) == -3.14

    def test_extract_integer_metric(self):
        output = "METRIC: 42\n"
        assert extract_metric(output) == 42.0


class TestIsImprovement:
    def test_max_improvement(self):
        assert is_improvement(0.95, 0.90, "max") is True

    def test_max_no_improvement(self):
        assert is_improvement(0.85, 0.90, "max") is False

    def test_min_improvement(self):
        assert is_improvement(0.10, 0.20, "min") is True

    def test_min_no_improvement(self):
        assert is_improvement(0.30, 0.20, "min") is False

    def test_first_run_always_improves_max(self):
        assert is_improvement(0.50, None, "max") is True

    def test_first_run_always_improves_min(self):
        assert is_improvement(0.50, None, "min") is True

    def test_equal_is_not_improvement(self):
        assert is_improvement(0.90, 0.90, "max") is False


class TestRunScript:
    def test_run_simple_script(self, tmp_path):
        script = os.path.join(str(tmp_path), "test.py")
        with open(script, "w") as f:
            f.write('print("METRIC: 42.0")\n')
        output = run_script(script, timeout=10)
        assert "METRIC: 42.0" in output

    def test_run_script_timeout(self, tmp_path):
        script = os.path.join(str(tmp_path), "slow.py")
        with open(script, "w") as f:
            f.write("import time\ntime.sleep(100)\n")
        with pytest.raises(subprocess.TimeoutExpired):
            run_script(script, timeout=1)

    def test_run_script_error(self, tmp_path):
        script = os.path.join(str(tmp_path), "bad.py")
        with open(script, "w") as f:
            f.write("raise ValueError('test error')\n")
        with pytest.raises(subprocess.CalledProcessError):
            run_script(script, timeout=10)
