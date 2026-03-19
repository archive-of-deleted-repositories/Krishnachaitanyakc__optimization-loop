import os
import pytest
from autoresearch_anything.templates import (
    get_template,
    list_templates,
    generate_project,
    TEMPLATES,
)


class TestListTemplates:
    def test_returns_template_names(self):
        names = list_templates()
        assert "web_perf" in names
        assert "db_query" in names
        assert "compiler" in names
        assert "code_quality" in names


class TestGetTemplate:
    def test_get_valid_template(self):
        tmpl = get_template("web_perf")
        assert "config" in tmpl
        assert "prepare" in tmpl
        assert "train" in tmpl
        assert "program" in tmpl

    def test_get_invalid_template(self):
        with pytest.raises(KeyError):
            get_template("nonexistent")


class TestGenerateProject:
    def test_creates_project_files(self, tmp_path):
        project_dir = os.path.join(str(tmp_path), "test-project")
        generate_project(project_dir, "web_perf", "test-project")
        assert os.path.exists(os.path.join(project_dir, "config.yaml"))
        assert os.path.exists(os.path.join(project_dir, "prepare.py"))
        assert os.path.exists(os.path.join(project_dir, "train.py"))
        assert os.path.exists(os.path.join(project_dir, "program.md"))

    def test_config_has_correct_name(self, tmp_path):
        import yaml

        project_dir = os.path.join(str(tmp_path), "my-proj")
        generate_project(project_dir, "db_query", "my-proj")
        with open(os.path.join(project_dir, "config.yaml")) as f:
            config = yaml.safe_load(f)
        assert config["name"] == "my-proj"

    def test_all_templates_generate(self, tmp_path):
        for name in list_templates():
            project_dir = os.path.join(str(tmp_path), name)
            generate_project(project_dir, name, name)
            assert os.path.exists(os.path.join(project_dir, "config.yaml"))
