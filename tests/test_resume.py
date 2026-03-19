import os
import pytest
from optimization_loop.results import parse_results, write_result, get_resume_state


class TestGetResumeState:
    def test_resume_from_existing_results(self, tmp_path):
        path = os.path.join(str(tmp_path), "results.tsv")
        write_result(path, "abc123", 0.90, "improved", "Iteration 0")
        write_result(path, "def456", 0.95, "improved", "Iteration 1")
        write_result(path, "ghi789", 0.85, "discarded", "Iteration 2")

        last_iter, best_val = get_resume_state(path, "max")
        assert last_iter == 2
        assert best_val == 0.95

    def test_resume_min_direction(self, tmp_path):
        path = os.path.join(str(tmp_path), "results.tsv")
        write_result(path, "abc123", 0.50, "improved", "Iteration 0")
        write_result(path, "def456", 0.30, "improved", "Iteration 1")

        last_iter, best_val = get_resume_state(path, "min")
        assert last_iter == 1
        assert best_val == 0.30

    def test_resume_no_results(self, tmp_path):
        path = os.path.join(str(tmp_path), "results.tsv")
        last_iter, best_val = get_resume_state(path, "max")
        assert last_iter == -1
        assert best_val is None

    def test_resume_empty_file(self, tmp_path):
        path = os.path.join(str(tmp_path), "results.tsv")
        with open(path, "w") as f:
            f.write("commit\tmetric_value\tstatus\tdescription\n")
        last_iter, best_val = get_resume_state(path, "max")
        assert last_iter == -1
        assert best_val is None
