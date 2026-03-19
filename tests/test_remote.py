import os
import pytest
from unittest.mock import patch, MagicMock
from autoresearch_anything.remote import (
    LocalExecutor,
    SSHExecutor,
    DockerExecutor,
    create_executor,
)


class TestLocalExecutor:
    def test_run_script(self, tmp_path):
        script = os.path.join(str(tmp_path), "test.py")
        with open(script, "w") as f:
            f.write('print("METRIC: 42.0")\n')

        executor = LocalExecutor()
        output = executor.run(script, timeout=10, cwd=str(tmp_path))
        assert "METRIC: 42.0" in output

    def test_run_script_error(self, tmp_path):
        script = os.path.join(str(tmp_path), "bad.py")
        with open(script, "w") as f:
            f.write('raise ValueError("test")\n')

        executor = LocalExecutor()
        with pytest.raises(Exception):
            executor.run(script, timeout=10, cwd=str(tmp_path))


class TestSSHExecutor:
    @patch("autoresearch_anything.remote._run_ssh")
    def test_ssh_run(self, mock_ssh):
        mock_ssh.return_value = "METRIC: 0.95\n"
        executor = SSHExecutor(host="remote.example.com", user="testuser")
        output = executor.run("train.py", timeout=60, cwd="/remote/project")
        assert "METRIC: 0.95" in output
        mock_ssh.assert_called_once()

    def test_ssh_config(self):
        executor = SSHExecutor(host="remote.example.com", user="testuser", key_file="/path/key")
        assert executor.host == "remote.example.com"
        assert executor.user == "testuser"


class TestDockerExecutor:
    @patch("autoresearch_anything.remote._run_docker")
    def test_docker_run(self, mock_docker):
        mock_docker.return_value = "METRIC: 0.85\n"
        executor = DockerExecutor(image="python:3.11")
        output = executor.run("train.py", timeout=60, cwd="/project")
        assert "METRIC: 0.85" in output
        mock_docker.assert_called_once()


class TestCreateExecutor:
    def test_local_default(self):
        executor = create_executor({})
        assert isinstance(executor, LocalExecutor)

    def test_local_explicit(self):
        executor = create_executor({"remote": {"type": "local"}})
        assert isinstance(executor, LocalExecutor)

    def test_ssh_executor(self):
        config = {"remote": {"type": "ssh", "host": "example.com", "user": "me"}}
        executor = create_executor(config)
        assert isinstance(executor, SSHExecutor)

    def test_docker_executor(self):
        config = {"remote": {"type": "docker", "image": "python:3.11"}}
        executor = create_executor(config)
        assert isinstance(executor, DockerExecutor)
