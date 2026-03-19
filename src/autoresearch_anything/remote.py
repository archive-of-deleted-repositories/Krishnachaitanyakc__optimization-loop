"""Remote execution support: SSH, Docker, and local subprocess."""
from __future__ import annotations

import os
import subprocess
import sys
from abc import ABC, abstractmethod


class Executor(ABC):
    """Base class for script executors."""

    @abstractmethod
    def run(self, script_path: str, timeout: int = 60, cwd: str | None = None) -> str:
        """Run a script and return stdout."""
        ...


class LocalExecutor(Executor):
    """Run scripts locally via subprocess."""

    def run(self, script_path: str, timeout: int = 60, cwd: str | None = None) -> str:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd or os.path.dirname(os.path.abspath(script_path)),
            check=True,
        )
        return result.stdout


class SSHExecutor(Executor):
    """Run scripts on a remote host via SSH."""

    def __init__(self, host: str, user: str = "root", key_file: str | None = None):
        self.host = host
        self.user = user
        self.key_file = key_file

    def run(self, script_path: str, timeout: int = 60, cwd: str | None = None) -> str:
        return _run_ssh(self.host, self.user, self.key_file, script_path, timeout, cwd)


class DockerExecutor(Executor):
    """Run scripts in a Docker container."""

    def __init__(self, image: str = "python:3.11"):
        self.image = image

    def run(self, script_path: str, timeout: int = 60, cwd: str | None = None) -> str:
        return _run_docker(self.image, script_path, timeout, cwd)


def _run_ssh(
    host: str,
    user: str,
    key_file: str | None,
    script_path: str,
    timeout: int,
    cwd: str | None,
) -> str:
    """Execute a script on a remote host via SSH using paramiko."""
    try:
        import paramiko
    except ImportError:
        raise ImportError("paramiko is required for SSH execution: pip install paramiko")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    connect_kwargs = {"hostname": host, "username": user}
    if key_file:
        connect_kwargs["key_filename"] = key_file

    try:
        client.connect(**connect_kwargs)
        cmd = f"cd {cwd} && python {script_path}" if cwd else f"python {script_path}"
        stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
        output = stdout.read().decode("utf-8")
        exit_code = stdout.channel.recv_exit_status()
        if exit_code != 0:
            err = stderr.read().decode("utf-8")
            raise subprocess.CalledProcessError(exit_code, cmd, output=output, stderr=err)
        return output
    finally:
        client.close()


def _run_docker(
    image: str,
    script_path: str,
    timeout: int,
    cwd: str | None,
) -> str:
    """Execute a script in a Docker container."""
    cmd = ["docker", "run", "--rm"]
    if cwd:
        cmd.extend(["-v", f"{cwd}:/workspace", "-w", "/workspace"])
    cmd.extend([image, "python", script_path])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=True,
    )
    return result.stdout


def create_executor(config: dict) -> Executor:
    """Create an executor based on the config.

    Config format:
        remote:
          type: local|ssh|docker
          host: hostname (ssh)
          user: username (ssh)
          key_file: path (ssh, optional)
          image: docker_image (docker)
    """
    remote = config.get("remote", {})
    if not remote:
        return LocalExecutor()

    exec_type = remote.get("type", "local")

    if exec_type == "local":
        return LocalExecutor()
    elif exec_type == "ssh":
        return SSHExecutor(
            host=remote["host"],
            user=remote.get("user", "root"),
            key_file=remote.get("key_file"),
        )
    elif exec_type == "docker":
        return DockerExecutor(image=remote.get("image", "python:3.11"))
    else:
        return LocalExecutor()
