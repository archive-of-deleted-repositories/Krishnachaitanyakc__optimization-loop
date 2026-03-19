import os
import pytest
from optimization_loop.results import write_result, parse_results, format_results_table


class TestWriteResult:
    def test_write_creates_file(self, tmp_path):
        path = os.path.join(str(tmp_path), "results.tsv")
        write_result(path, "abc123", 0.95, "improved", "Initial run")
        assert os.path.exists(path)

    def test_write_appends(self, tmp_path):
        path = os.path.join(str(tmp_path), "results.tsv")
        write_result(path, "abc123", 0.95, "improved", "First")
        write_result(path, "def456", 0.90, "discarded", "Second")
        results = parse_results(path)
        assert len(results) == 2

    def test_write_creates_header(self, tmp_path):
        path = os.path.join(str(tmp_path), "results.tsv")
        write_result(path, "abc123", 0.95, "improved", "Test")
        with open(path) as f:
            header = f.readline().strip()
        assert "commit" in header
        assert "metric_value" in header


class TestParseResults:
    def test_parse_valid(self, tmp_path):
        path = os.path.join(str(tmp_path), "results.tsv")
        write_result(path, "abc123", 0.95, "improved", "Test run")
        results = parse_results(path)
        assert len(results) == 1
        assert results[0]["commit"] == "abc123"
        assert results[0]["metric_value"] == 0.95
        assert results[0]["status"] == "improved"

    def test_parse_empty_file(self, tmp_path):
        path = os.path.join(str(tmp_path), "results.tsv")
        with open(path, "w") as f:
            f.write("commit\tmetric_value\tstatus\tdescription\n")
        results = parse_results(path)
        assert results == []

    def test_parse_missing_file(self):
        results = parse_results("/nonexistent/results.tsv")
        assert results == []


class TestFormatResultsTable:
    def test_format_with_results(self, tmp_path):
        path = os.path.join(str(tmp_path), "results.tsv")
        write_result(path, "abc123", 0.95, "improved", "First")
        write_result(path, "def456", 0.90, "discarded", "Second")
        results = parse_results(path)
        table = format_results_table(results)
        assert "abc123" in table
        assert "0.95" in table

    def test_format_empty(self):
        table = format_results_table([])
        assert "No results" in table
