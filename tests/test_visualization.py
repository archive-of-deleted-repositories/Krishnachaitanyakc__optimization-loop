import os
import pytest
from autoresearch_anything.results import write_result
from autoresearch_anything.visualization import generate_plot


class TestGeneratePlot:
    def _make_results(self, tmp_path):
        path = os.path.join(str(tmp_path), "results.tsv")
        write_result(path, "a1", 0.80, "improved", "Iteration 0")
        write_result(path, "a2", 0.85, "improved", "Iteration 1")
        write_result(path, "a3", 0.82, "discarded", "Iteration 2")
        write_result(path, "a4", 0.90, "improved", "Iteration 3")
        return path

    def test_generates_png(self, tmp_path):
        results_path = self._make_results(tmp_path)
        out_path = os.path.join(str(tmp_path), "metrics.png")
        generate_plot(results_path, out_path, metric_name="accuracy")
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 0

    def test_default_output_path(self, tmp_path):
        results_path = self._make_results(tmp_path)
        out_path = generate_plot(results_path, metric_name="score")
        assert os.path.exists(out_path)
        assert out_path.endswith(".png")

    def test_empty_results(self, tmp_path):
        results_path = os.path.join(str(tmp_path), "results.tsv")
        with open(results_path, "w") as f:
            f.write("commit\tmetric_value\tstatus\tdescription\n")
        out_path = os.path.join(str(tmp_path), "out.png")
        with pytest.raises(ValueError, match="No results"):
            generate_plot(results_path, out_path)
