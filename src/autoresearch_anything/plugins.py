"""Plugin system with MetricExtractor and TemplateProvider base classes."""
from __future__ import annotations

import importlib.util
import os
import sys

_registered_extractors: list[MetricExtractor] = []
_registered_providers: list[TemplateProvider] = []


class MetricExtractor:
    """Base class for metric extractors. Subclass and override extract()."""

    name: str = "base"

    def extract(self, output: str) -> dict[str, float]:
        raise NotImplementedError

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.name != "base":
            _registered_extractors.append(cls())


class TemplateProvider:
    """Base class for template providers. Subclass and override get_templates()."""

    name: str = "base"

    def get_templates(self) -> dict[str, dict]:
        raise NotImplementedError

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.name != "base":
            _registered_providers.append(cls())


def load_plugins_from_dir(plugin_dir: str) -> None:
    """Load all .py files from a directory as plugins."""
    if not os.path.isdir(plugin_dir):
        return

    for filename in sorted(os.listdir(plugin_dir)):
        if not filename.endswith(".py") or filename.startswith("_"):
            continue
        filepath = os.path.join(plugin_dir, filename)
        module_name = f"autoresearch_plugin_{filename[:-3]}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = mod
                spec.loader.exec_module(mod)
        except Exception:
            pass  # Skip broken plugins silently


def get_plugin_metric_extractors() -> list[MetricExtractor]:
    """Return all registered MetricExtractor plugin instances."""
    return list(_registered_extractors)


def get_plugin_template_providers() -> list[TemplateProvider]:
    """Return all registered TemplateProvider plugin instances."""
    return list(_registered_providers)


def load_default_plugins() -> None:
    """Load plugins from the default ~/.autoresearch/plugins/ directory."""
    default_dir = os.path.expanduser("~/.autoresearch/plugins")
    load_plugins_from_dir(default_dir)
