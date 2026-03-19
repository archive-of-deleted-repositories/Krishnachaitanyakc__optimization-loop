import os
import json
import csv
import pytest
from optimization_loop.export import export_results
from optimization_loop.results import write_result


class TestExportResults:
    def _make_results(self, tmp_path):
        path = os.path.join(str(tmp_path), "results.tsv")
        write_result(path, "abc123", 0.95, "improved", "First")
        write_result(path, "def456", 0.90, "discarded", "Second")
        return path

    def test_export_json(self, tmp_path):
        results_path = self._make_results(tmp_path)
        out_path = os.path.join(str(tmp_path), "out.json")
        export_results(results_path, out_path, "json")
        with open(out_path) as f:
            data = json.load(f)
        assert len(data) == 2
        assert data[0]["commit"] == "abc123"
        assert data[0]["metric_value"] == 0.95

    def test_export_csv(self, tmp_path):
        results_path = self._make_results(tmp_path)
        out_path = os.path.join(str(tmp_path), "out.csv")
        export_results(results_path, out_path, "csv")
        with open(out_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["commit"] == "abc123"

    def test_export_tsv(self, tmp_path):
        results_path = self._make_results(tmp_path)
        out_path = os.path.join(str(tmp_path), "out.tsv")
        export_results(results_path, out_path, "tsv")
        with open(out_path) as f:
            reader = csv.DictReader(f, delimiter="\t")
            rows = list(reader)
        assert len(rows) == 2

    def test_export_invalid_format(self, tmp_path):
        results_path = self._make_results(tmp_path)
        out_path = os.path.join(str(tmp_path), "out.xml")
        with pytest.raises(ValueError, match="Unsupported"):
            export_results(results_path, out_path, "xml")
