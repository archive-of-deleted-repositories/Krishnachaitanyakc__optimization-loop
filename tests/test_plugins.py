import os
import pytest
from optimization_loop.plugins import (
    MetricExtractor,
    TemplateProvider,
    load_plugins_from_dir,
    get_plugin_metric_extractors,
    get_plugin_template_providers,
)


class TestMetricExtractor:
    def test_base_class_raises(self):
        extractor = MetricExtractor()
        with pytest.raises(NotImplementedError):
            extractor.extract("output text")

    def test_subclass_works(self):
        class MyExtractor(MetricExtractor):
            name = "my_extractor"

            def extract(self, output: str) -> dict[str, float]:
                return {"custom": 1.0}

        ext = MyExtractor()
        assert ext.extract("anything") == {"custom": 1.0}
        assert ext.name == "my_extractor"


class TestTemplateProvider:
    def test_base_class_raises(self):
        provider = TemplateProvider()
        with pytest.raises(NotImplementedError):
            provider.get_templates()

    def test_subclass_works(self):
        class MyProvider(TemplateProvider):
            name = "my_provider"

            def get_templates(self) -> dict[str, dict]:
                return {"custom_template": {"config": {}, "prepare": "", "train": "", "program": ""}}

        prov = MyProvider()
        templates = prov.get_templates()
        assert "custom_template" in templates


class TestLoadPluginsFromDir:
    def test_loads_plugin_from_directory(self, tmp_path):
        plugin_dir = str(tmp_path)
        plugin_file = os.path.join(plugin_dir, "my_plugin.py")
        with open(plugin_file, "w") as f:
            f.write(
                'from optimization_loop.plugins import MetricExtractor\n'
                'class TestExtractor(MetricExtractor):\n'
                '    name = "test_ext"\n'
                '    def extract(self, output):\n'
                '        return {"test": 42.0}\n'
            )

        load_plugins_from_dir(plugin_dir)
        extractors = get_plugin_metric_extractors()
        names = [e.name for e in extractors]
        assert "test_ext" in names

    def test_nonexistent_dir_is_noop(self):
        load_plugins_from_dir("/nonexistent/path/to/plugins")
        # Should not raise
