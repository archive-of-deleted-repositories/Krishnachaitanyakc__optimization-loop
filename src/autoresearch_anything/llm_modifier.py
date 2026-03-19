"""LLM-based train script modification using Anthropic Claude."""
from __future__ import annotations

import os
import re


def build_prompt(
    train_path: str,
    program_path: str,
    results_history: list[dict],
) -> str:
    """Build the prompt for the LLM to modify the train script.

    Args:
        train_path: Path to the current train.py script.
        program_path: Path to the program.md strategy file.
        results_history: List of past result dicts.

    Returns:
        The prompt string.
    """
    with open(train_path) as f:
        train_code = f.read()

    with open(program_path) as f:
        program_text = f.read()

    history_text = ""
    if results_history:
        lines = []
        for r in results_history:
            lines.append(
                f"  metric={r['metric_value']}, status={r['status']}, {r['description']}"
            )
        history_text = "\n".join(lines)
    else:
        history_text = "  No previous results."

    return f"""You are an optimization assistant. Your task is to modify a training script to improve its metric.

## Strategy (program.md)
{program_text}

## Current train.py
```python
{train_code}
```

## Results history
{history_text}

## Instructions
- Modify the train.py code to improve the metric based on the strategy and past results.
- Return ONLY the complete modified Python code, no explanations.
- The script must print a line matching 'METRIC: <value>' to stdout.
- Keep the same general structure but make targeted improvements.
"""


def _call_llm(prompt: str, api_key: str) -> str:
    """Call the Anthropic Claude API and return the response text."""
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def _extract_code(response: str) -> str:
    """Extract Python code from the LLM response, stripping markdown fences."""
    # Try to extract from code fences
    match = re.search(r"```python\s*\n(.*?)```", response, re.DOTALL)
    if match:
        return match.group(1).strip() + "\n"
    match = re.search(r"```\s*\n(.*?)```", response, re.DOTALL)
    if match:
        return match.group(1).strip() + "\n"
    return response.strip() + "\n"


def modify_train_script(
    train_path: str,
    program_path: str,
    results_history: list[dict],
    api_key: str | None = None,
    write_back: bool = False,
) -> str:
    """Use an LLM to generate a modified train.py.

    Args:
        train_path: Path to the current train.py.
        program_path: Path to program.md.
        results_history: Past results for context.
        api_key: Anthropic API key. Defaults to AUTORESEARCH_LLM_API_KEY env var.
        write_back: If True, overwrite train_path with the new code.

    Returns:
        The new train.py code.
    """
    if api_key is None:
        api_key = os.environ.get("AUTORESEARCH_LLM_API_KEY", "")

    prompt = build_prompt(train_path, program_path, results_history)
    response = _call_llm(prompt, api_key)
    new_code = _extract_code(response)

    if write_back:
        with open(train_path, "w") as f:
            f.write(new_code)

    return new_code
