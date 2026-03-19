"""Click CLI for autoresearch-anything."""

import os
import click

from .config import load_config, ConfigError
from .templates import generate_project, list_templates
from .results import parse_results, format_results_table
from .loop import run_optimization_loop


@click.group()
def cli():
    """autoresearch-anything: Optimize any quantifiable task."""
    pass


@cli.command()
@click.argument("project_dir")
@click.option("--template", "-t", default="code_quality", help="Template to use")
@click.option("--name", "-n", default=None, help="Project name (defaults to directory name)")
def init(project_dir, template, name):
    """Initialize a new optimization project from a template."""
    available = list_templates()
    if template not in available:
        raise click.ClickException(
            f"Unknown template '{template}'. Available: {', '.join(available)}"
        )

    if name is None:
        name = os.path.basename(os.path.abspath(project_dir))

    generate_project(project_dir, template, name)
    click.echo(f"Project '{name}' created at {project_dir} using template '{template}'.")


@cli.command()
@click.option("--project-dir", "-d", default=".", help="Project directory")
@click.option("--max-iterations", "-n", default=10, help="Max optimization iterations")
def run(project_dir, max_iterations):
    """Run the optimization loop."""
    config_path = os.path.join(project_dir, "config.yaml")
    try:
        config = load_config(config_path)
    except (FileNotFoundError, ConfigError) as e:
        raise click.ClickException(str(e))

    click.echo(f"Starting optimization: {config['name']}")
    click.echo(f"Metric: {config['metric_name']} ({config['metric_direction']})")
    click.echo(f"Time budget: {config['time_budget_seconds']}s per iteration")
    click.echo()

    results = run_optimization_loop(config, project_dir, max_iterations)

    for r in results:
        status = r["status"]
        metric = r.get("metric", "N/A")
        click.echo(f"  Iteration {r['iteration']}: {status} (metric={metric})")

    click.echo(f"\nCompleted {len(results)} iterations.")


@cli.command()
@click.option("--project-dir", "-d", default=".", help="Project directory")
def results(project_dir):
    """Show the results table."""
    results_path = os.path.join(project_dir, "results.tsv")
    data = parse_results(results_path)
    click.echo(format_results_table(data))


@cli.command()
@click.option("--project-dir", "-d", default=".", help="Project directory")
def status(project_dir):
    """Show current best metric."""
    results_path = os.path.join(project_dir, "results.tsv")
    data = parse_results(results_path)

    if not data:
        click.echo("No results yet.")
        return

    # Find best based on config if available
    config_path = os.path.join(project_dir, "config.yaml")
    direction = "max"
    metric_name = "metric"
    try:
        from .config import load_config
        config = load_config(config_path)
        direction = config["metric_direction"]
        metric_name = config["metric_name"]
    except Exception:
        pass

    if direction == "max":
        best = max(data, key=lambda r: r["metric_value"])
    else:
        best = min(data, key=lambda r: r["metric_value"])

    click.echo(f"Best {metric_name}: {best['metric_value']:.4f}")
    click.echo(f"Commit: {best['commit']}")
    click.echo(f"Total runs: {len(data)}")
