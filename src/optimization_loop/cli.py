"""Click CLI for optimization-loop."""

import os
import click

from .config import load_config, ConfigError
from .templates import generate_project, list_templates
from .results import parse_results, format_results_table, get_resume_state
from .loop import run_optimization_loop


@click.group()
def cli():
    """optimization-loop: Optimize any quantifiable task."""
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
@click.option("--resume", is_flag=True, default=False, help="Resume from last checkpoint")
@click.option("--parallel", "-p", default=1, type=int, help="Number of parallel workers")
def run(project_dir, max_iterations, resume, parallel):
    """Run the optimization loop."""
    config_path = os.path.join(project_dir, "config.yaml")
    try:
        config = load_config(config_path)
    except (FileNotFoundError, ConfigError) as e:
        raise click.ClickException(str(e))

    click.echo(f"Starting optimization: {config['name']}")
    click.echo(f"Metric: {config['metric_name']} ({config['metric_direction']})")
    click.echo(f"Time budget: {config['time_budget_seconds']}s per iteration")

    start_iteration = 0
    best_value = None
    if resume:
        results_path = os.path.join(project_dir, "results.tsv")
        last_iter, best_val = get_resume_state(results_path, config["metric_direction"])
        if last_iter >= 0:
            start_iteration = last_iter + 1
            best_value = best_val
            click.echo(f"Resuming from iteration {start_iteration} (best={best_val})")

    click.echo()

    if parallel > 1:
        from .parallel import run_parallel_iterations

        results = run_parallel_iterations(
            config, project_dir, num_parallel=parallel,
            timeout=int(config["time_budget_seconds"]),
        )
        for r in results:
            status = r["status"]
            metric = r.get("metric", "N/A")
            click.echo(f"  Parallel run {r['index']}: {status} (metric={metric})")
        click.echo(f"\nCompleted {len(results)} parallel runs.")
    else:
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


@cli.command()
@click.option("--project-dir", "-d", default=".", help="Project directory")
@click.option("--output", "-o", default=None, help="Output PNG path")
@click.option("--metric-name", "-m", default="metric", help="Metric name for y-axis label")
def plot(project_dir, output, metric_name):
    """Generate a metric-over-time plot from results."""
    from .visualization import generate_plot

    results_path = os.path.join(project_dir, "results.tsv")
    if output is None:
        output = os.path.join(project_dir, "metrics.png")

    try:
        out_path = generate_plot(results_path, output, metric_name=metric_name)
        click.echo(f"Plot saved to {out_path}")
    except ValueError as e:
        raise click.ClickException(str(e))


@cli.command(name="export")
@click.option("--project-dir", "-d", default=".", help="Project directory")
@click.option("--format", "fmt", type=click.Choice(["json", "csv", "tsv"]), default="json", help="Export format")
@click.option("--output", "-o", default=None, help="Output file path")
def export_cmd(project_dir, fmt, output):
    """Export results to JSON, CSV, or TSV."""
    from .export import export_results

    results_path = os.path.join(project_dir, "results.tsv")
    if output is None:
        output = os.path.join(project_dir, f"results.{fmt}")

    try:
        export_results(results_path, output, fmt)
        click.echo(f"Exported to {output}")
    except ValueError as e:
        raise click.ClickException(str(e))


@cli.command()
@click.option("--project-dir", "-d", default=".", help="Project directory")
@click.option("--sweep-config", "-s", required=True, help="Path to sweep config YAML")
def sweep(project_dir, sweep_config):
    """Run a hyperparameter sweep."""
    import yaml
    from .sweep import run_sweep

    config_path = os.path.join(project_dir, "config.yaml")
    try:
        config = load_config(config_path)
    except (FileNotFoundError, ConfigError) as e:
        raise click.ClickException(str(e))

    try:
        with open(sweep_config) as f:
            sweep_params = yaml.safe_load(f)
    except Exception as e:
        raise click.ClickException(f"Failed to load sweep config: {e}")

    if not isinstance(sweep_params, list):
        raise click.ClickException("Sweep config must be a YAML list of {name, values} dicts")

    click.echo(f"Running sweep with {len(sweep_params)} parameters")
    results = run_sweep(config, project_dir, sweep_params)

    for r in results:
        params_str = ", ".join(f"{k}={v}" for k, v in r["params"].items())
        metric = r.get("metric", "N/A")
        click.echo(f"  [{r['status']}] {params_str} -> metric={metric}")

    click.echo(f"\nCompleted {len(results)} sweep runs.")
