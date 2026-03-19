# autoresearch-anything

Generalize the autoresearch optimization loop to ANY quantifiable optimization task.

## Overview

autoresearch-anything provides a pluggable optimization loop that works with any task that has a quantifiable metric. Define a prepare script, a train script, and a program file, then let the loop modify, run, evaluate, and keep or discard changes based on your metric.

## Installation

```bash
pip install -e .
```

## Usage

### Initialize a new project from a template

```bash
autoresearch-anything init my-project --template web_perf
```

Available templates: `web_perf`, `db_query`, `compiler`, `code_quality`

### Run the optimization loop

```bash
cd my-project
autoresearch-anything run
```

### View results

```bash
autoresearch-anything results
autoresearch-anything status
```

## Configuration

Projects use a `config.yaml` file:

```yaml
name: my-project
metric_name: score
metric_direction: max
time_budget_seconds: 60
prepare_script: prepare.py
train_script: train.py
program_file: program.md
```

## How It Works

1. `init` creates a project directory with config, prepare, train, and program files from a template.
2. `run` loads the config, runs prepare once, then loops:
   - Modify the train script
   - Run it with time budget
   - Extract metric from stdout (last line matching `METRIC: <value>`)
   - Compare to best result
   - Git commit if improved
   - Log to results.tsv
3. `results` shows the results table.
4. `status` shows the current best metric.
