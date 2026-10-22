from pathlib import Path

import sys
import shutil
import subprocess

PROJECT_PATH = Path.cwd().resolve()


def wrap(command):
    if sys.platform == 'linux' and shutil.which('bwrap'):
        return [
            "bwrap",
            "--ro-bind", '/', '/',
            "--bind", str(PROJECT_PATH), str(PROJECT_PATH),
            "--dev", "/dev", "--proc", "/proc",
            "--unshare-net", "--die-with-parent",
            "/bin/sh", "-c", command, 
        ]

    return None


def run(command, timeout=60):
    sandbox_cmd = wrap(command)
    return subprocess.run(
        sandbox_cmd or command,
        shell = sandbox_cmd is None,
        capture_output=True,
        text=True,
        timeout=timeout
    )
