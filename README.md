# optimization-loop

**Autoresearch for everything.**

---

Most optimization tools are locked to ML hyperparameters. But optimization is everywhere -- web performance, database queries, compiler flags, code quality. **optimization-loop** generalizes the autoresearch loop to *any* task with a quantifiable metric: define a script, point it at a metric, and let the loop modify, run, evaluate, and keep or discard changes automatically.

## Quick Start

```bash
pip install optimization-loop
```

```python
from optimization_loop.loop import run_optimization_loop
from optimization_loop.config import load_config

config = load_config("config.yaml")
results = run_optimization_loop(config, project_dir=".", max_iterations=50)
print(f"Best: {max(r['metric'] for r in results if r['metric'])}")
```

## Features

- **Domain-agnostic** -- built-in templates for web performance, database queries, compiler optimization, and code quality
- **Pluggable metric extraction** -- any script that prints `METRIC: <value>` works out of the box
- **Git-native** -- auto-commits improvements, discards regressions, full history of what worked
- **Parallel workers** -- run multiple optimization candidates simultaneously
- **Hyperparameter sweeps** -- grid search via YAML sweep configs
- **Resume support** -- pick up where you left off after interruptions
- **LLM-powered modifications** -- optional AI-guided code changes between iterations
- **Remote execution** -- run optimization loops on remote machines
- **Export & visualization** -- results to JSON/CSV/TSV, metric-over-time plots
- **Plugin system** -- extend with custom modifiers, metrics, and callbacks
- **Notifications** -- get alerts when optimization finds improvements

## CLI Usage

```bash
# Initialize a project from a template
optimization-loop init my-project --template web_perf

# Run the optimization loop
optimization-loop run --project-dir my-project --max-iterations 50

# Run with parallel workers
optimization-loop run -d my-project -n 100 --parallel 4

# Resume a previous run
optimization-loop run -d my-project --resume

# Run a hyperparameter sweep
optimization-loop sweep -d my-project --sweep-config sweep.yaml

# View results
optimization-loop results -d my-project
optimization-loop status -d my-project

# Generate a metric plot
optimization-loop plot -d my-project -o progress.png

# Export results
optimization-loop export -d my-project --format csv -o results.csv
```

## Python API

```python
from optimization_loop.config import load_config
from optimization_loop.loop import run_optimization_loop
from optimization_loop.parallel import run_parallel_iterations
from optimization_loop.sweep import run_sweep
from optimization_loop.visualization import generate_plot

# Standard loop
config = load_config("config.yaml")
results = run_optimization_loop(config, ".", max_iterations=100)

# Parallel execution
results = run_parallel_iterations(config, ".", num_parallel=4, timeout=120)

# Hyperparameter sweep
sweep_params = [{"name": "lr", "values": [0.001, 0.01, 0.1]}]
sweep_results = run_sweep(config, ".", sweep_params)

# Visualize progress
generate_plot("results.tsv", "metrics.png", metric_name="accuracy")
```

## Configuration

```yaml
name: my-project
metric_name: score
metric_direction: max        # or min
time_budget_seconds: 60
prepare_script: prepare.py
train_script: train.py
program_file: program.md
```

## How It Works

1. `init` scaffolds a project with config, prepare, train, and program files from a template
2. `run` executes the loop: modify code -> run script -> extract metric -> compare to best -> git commit if improved -> log to results.tsv
3. Parallel mode distributes candidates across workers; sweep mode does grid search
4. Every improvement is a git commit; every regression is discarded -- your repo *is* the experiment log

## Comparison

| Feature | optimization-loop | autoresearch (Karpathy) | Optuna | Ray Tune |
|---|---|---|---|---|
| Domain | Any quantifiable task | ML training only | ML hyperparams | ML hyperparams |
| Git integration | Built-in auto-commit | Built-in | None | None |
| Templates | Web, DB, compiler, code | ML only | None | None |
| Parallel workers | Yes | No | Yes | Yes |
| LLM-guided modifications | Yes | Yes | No | No |
| Sweep support | Yes | No | Yes | Yes |
| Resume | Yes | No | Yes | Yes |
| Zero dependencies on ML | Yes | No | No | No |
| Setup complexity | `pip install` + YAML | Clone + configure | Library integration | Library integration |

## License

MIT
