import os
import pytest
from click.testing import CliRunner
from autoresearch_anything.cli import cli


class TestInitCommand:
    def test_init_creates_project(self, tmp_path):
        runner = CliRunner()
        project_dir = os.path.join(str(tmp_path), "test-proj")
        result = runner.invoke(cli, ["init", project_dir, "--template", "web_perf"])
        assert result.exit_code == 0
        assert os.path.exists(os.path.join(project_dir, "config.yaml"))

    def test_init_default_template(self, tmp_path):
        runner = CliRunner()
        project_dir = os.path.join(str(tmp_path), "default-proj")
        result = runner.invoke(cli, ["init", project_dir])
        assert result.exit_code == 0
        assert os.path.exists(os.path.join(project_dir, "config.yaml"))

    def test_init_invalid_template(self, tmp_path):
        runner = CliRunner()
        project_dir = os.path.join(str(tmp_path), "bad-proj")
        result = runner.invoke(cli, ["init", project_dir, "--template", "nonexistent"])
        assert result.exit_code != 0


class TestResultsCommand:
    def test_results_no_file(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(cli, ["results", "--project-dir", str(tmp_path)])
        assert result.exit_code == 0
        assert "No results" in result.output


class TestStatusCommand:
    def test_status_no_results(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(cli, ["status", "--project-dir", str(tmp_path)])
        assert result.exit_code == 0
        assert "No results" in result.output or "no results" in result.output.lower()
