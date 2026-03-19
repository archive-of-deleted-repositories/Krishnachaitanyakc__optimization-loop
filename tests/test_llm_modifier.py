import os
import pytest
from unittest.mock import patch, MagicMock
from optimization_loop.llm_modifier import build_prompt, modify_train_script


class TestBuildPrompt:
    def test_builds_prompt_with_all_parts(self, tmp_path):
        train_path = os.path.join(str(tmp_path), "train.py")
        with open(train_path, "w") as f:
            f.write('print("METRIC: 0.5")\n')

        program_path = os.path.join(str(tmp_path), "program.md")
        with open(program_path, "w") as f:
            f.write("# Goal\nMaximize accuracy.\n")

        results_history = [
            {"commit": "abc", "metric_value": 0.5, "status": "improved", "description": "Iter 0"},
        ]

        prompt = build_prompt(train_path, program_path, results_history)
        assert "train.py" in prompt or "print" in prompt
        assert "Goal" in prompt
        assert "0.5" in prompt

    def test_builds_prompt_empty_history(self, tmp_path):
        train_path = os.path.join(str(tmp_path), "train.py")
        with open(train_path, "w") as f:
            f.write('x = 1\n')

        program_path = os.path.join(str(tmp_path), "program.md")
        with open(program_path, "w") as f:
            f.write("# Plan\n")

        prompt = build_prompt(train_path, program_path, [])
        assert "x = 1" in prompt


class TestModifyTrainScript:
    @patch("optimization_loop.llm_modifier._call_llm")
    def test_modify_returns_new_code(self, mock_llm, tmp_path):
        mock_llm.return_value = 'print("METRIC: 0.9")\n'

        train_path = os.path.join(str(tmp_path), "train.py")
        with open(train_path, "w") as f:
            f.write('print("METRIC: 0.5")\n')

        program_path = os.path.join(str(tmp_path), "program.md")
        with open(program_path, "w") as f:
            f.write("# Plan\n")

        new_code = modify_train_script(train_path, program_path, [], api_key="test-key")
        assert "0.9" in new_code

    @patch("optimization_loop.llm_modifier._call_llm")
    def test_modify_writes_file(self, mock_llm, tmp_path):
        mock_llm.return_value = 'print("METRIC: 0.9")\n'

        train_path = os.path.join(str(tmp_path), "train.py")
        with open(train_path, "w") as f:
            f.write('print("METRIC: 0.5")\n')

        program_path = os.path.join(str(tmp_path), "program.md")
        with open(program_path, "w") as f:
            f.write("# Plan\n")

        modify_train_script(
            train_path, program_path, [], api_key="test-key", write_back=True
        )
        with open(train_path) as f:
            assert "0.9" in f.read()
