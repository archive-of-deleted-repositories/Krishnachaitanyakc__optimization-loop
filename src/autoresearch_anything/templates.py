"""Built-in project templates for different optimization domains."""
from __future__ import annotations

import os
import yaml

TEMPLATES = {
    "web_perf": {
        "config": {
            "name": "{project_name}",
            "metric_name": "lighthouse_score",
            "metric_direction": "max",
            "time_budget_seconds": 120,
            "prepare_script": "prepare.py",
            "train_script": "train.py",
            "program_file": "program.md",
        },
        "prepare": '''\
"""Prepare script for web performance optimization."""
import os

def setup():
    """Set up the web performance testing environment."""
    os.makedirs("output", exist_ok=True)
    print("Environment ready for web performance testing.")

if __name__ == "__main__":
    setup()
''',
        "train": '''\
"""Train script for web performance optimization."""
import random
import time

def evaluate_performance():
    """Simulate evaluating web performance metrics."""
    # Simulate Lighthouse-style scoring
    base_score = 65
    optimization_bonus = random.uniform(0, 30)
    score = min(100, base_score + optimization_bonus)
    return score

if __name__ == "__main__":
    score = evaluate_performance()
    print(f"Performance score: {score:.2f}")
    print(f"METRIC: {score:.2f}")
''',
        "program": """\
# Web Performance Optimization Strategy

## Goal
Maximize Lighthouse performance score.

## Approach
1. Minimize render-blocking resources
2. Optimize image loading
3. Reduce JavaScript bundle size
4. Implement caching strategies
""",
    },
    "db_query": {
        "config": {
            "name": "{project_name}",
            "metric_name": "query_latency_ms",
            "metric_direction": "min",
            "time_budget_seconds": 60,
            "prepare_script": "prepare.py",
            "train_script": "train.py",
            "program_file": "program.md",
        },
        "prepare": '''\
"""Prepare script for database query optimization."""
import sqlite3
import os

def setup():
    """Create a test database with sample data."""
    db_path = "test.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, age INTEGER)")
    for i in range(1000):
        cur.execute("INSERT INTO users VALUES (?, ?, ?, ?)",
                     (i, f"user_{i}", f"user_{i}@example.com", 20 + (i % 50)))
    conn.commit()
    conn.close()
    print("Database prepared with 1000 rows.")

if __name__ == "__main__":
    setup()
''',
        "train": '''\
"""Train script for database query optimization."""
import sqlite3
import time

def run_query():
    """Run a database query and measure latency."""
    conn = sqlite3.connect("test.db")
    cur = conn.cursor()
    start = time.perf_counter()
    cur.execute("SELECT name, email FROM users WHERE age > 30 ORDER BY name LIMIT 100")
    results = cur.fetchall()
    elapsed_ms = (time.perf_counter() - start) * 1000
    conn.close()
    return elapsed_ms

if __name__ == "__main__":
    latency = run_query()
    print(f"Query returned in {latency:.2f}ms")
    print(f"METRIC: {latency:.4f}")
''',
        "program": """\
# Database Query Optimization Strategy

## Goal
Minimize query latency in milliseconds.

## Approach
1. Add appropriate indexes
2. Optimize query structure
3. Use query planning hints
4. Reduce result set size
""",
    },
    "compiler": {
        "config": {
            "name": "{project_name}",
            "metric_name": "throughput_ops_per_sec",
            "metric_direction": "max",
            "time_budget_seconds": 90,
            "prepare_script": "prepare.py",
            "train_script": "train.py",
            "program_file": "program.md",
        },
        "prepare": '''\
"""Prepare script for compiler throughput optimization."""
import os

def setup():
    """Generate test input for compilation."""
    os.makedirs("input", exist_ok=True)
    with open("input/test_program.txt", "w") as f:
        for i in range(100):
            f.write(f"LET x{i} = {i} + {i+1}\\n")
            f.write(f"PRINT x{i}\\n")
    print("Test input generated.")

if __name__ == "__main__":
    setup()
''',
        "train": '''\
"""Train script for compiler throughput optimization."""
import time

def compile_and_measure():
    """Simulate compilation and measure throughput."""
    with open("input/test_program.txt") as f:
        lines = f.readlines()
    start = time.perf_counter()
    # Simple parse simulation
    parsed = []
    for line in lines:
        tokens = line.strip().split()
        parsed.append(tokens)
    elapsed = time.perf_counter() - start
    ops_per_sec = len(lines) / elapsed if elapsed > 0 else 0
    return ops_per_sec

if __name__ == "__main__":
    throughput = compile_and_measure()
    print(f"Throughput: {throughput:.0f} ops/sec")
    print(f"METRIC: {throughput:.2f}")
''',
        "program": """\
# Compiler Throughput Optimization Strategy

## Goal
Maximize operations processed per second.

## Approach
1. Optimize lexer/tokenizer
2. Reduce memory allocations
3. Batch processing
4. Cache intermediate results
""",
    },
    "code_quality": {
        "config": {
            "name": "{project_name}",
            "metric_name": "test_pass_rate",
            "metric_direction": "max",
            "time_budget_seconds": 60,
            "prepare_script": "prepare.py",
            "train_script": "train.py",
            "program_file": "program.md",
        },
        "prepare": '''\
"""Prepare script for code quality optimization."""
import os

def setup():
    """Set up the code quality testing environment."""
    os.makedirs("src_under_test", exist_ok=True)
    with open("src_under_test/calculator.py", "w") as f:
        f.write("""
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
""")
    print("Source code prepared.")

if __name__ == "__main__":
    setup()
''',
        "train": '''\
"""Train script for code quality optimization."""
import importlib.util
import sys
import os

def run_tests():
    """Run tests and calculate pass rate."""
    # Load the module under test
    spec = importlib.util.spec_from_file_location("calculator", "src_under_test/calculator.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    tests = [
        ("add(2,3)==5", mod.add(2, 3) == 5),
        ("subtract(5,3)==2", mod.subtract(5, 3) == 2),
        ("multiply(4,3)==12", mod.multiply(4, 3) == 12),
        ("divide(10,2)==5", mod.divide(10, 2) == 5.0),
    ]

    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    rate = passed / total if total > 0 else 0
    print(f"Tests: {passed}/{total} passed")
    print(f"METRIC: {rate:.4f}")
    return rate

if __name__ == "__main__":
    run_tests()
''',
        "program": """\
# Code Quality Optimization Strategy

## Goal
Maximize test pass rate (0.0 to 1.0).

## Approach
1. Fix failing tests
2. Improve error handling
3. Add edge case coverage
4. Refactor for testability
""",
    },
}


def list_templates() -> list[str]:
    """Return a list of available template names."""
    return list(TEMPLATES.keys())


def get_template(name: str) -> dict:
    """Get a template by name. Raises KeyError if not found."""
    return TEMPLATES[name]


def generate_project(project_dir: str, template_name: str, project_name: str) -> None:
    """Generate a project directory from a template."""
    template = get_template(template_name)
    os.makedirs(project_dir, exist_ok=True)

    # Write config.yaml
    config = dict(template["config"])
    config["name"] = project_name
    with open(os.path.join(project_dir, "config.yaml"), "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    # Write prepare.py
    with open(os.path.join(project_dir, "prepare.py"), "w") as f:
        f.write(template["prepare"])

    # Write train.py
    with open(os.path.join(project_dir, "train.py"), "w") as f:
        f.write(template["train"])

    # Write program.md
    with open(os.path.join(project_dir, "program.md"), "w") as f:
        f.write(template["program"])
