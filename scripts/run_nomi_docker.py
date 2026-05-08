#!/usr/bin/env python3
"""Build and run the portable Nomi Jupyter Docker image."""


#TODO: later the macos depdnency should be isolated out; there should be a install/setup process that abstracts out the os

from __future__ import annotations

import argparse
import http.client
import platform
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = "nomi:jupyter"
DEFAULT_CONTAINER = "nomi-jupyter"
DEFAULT_PORT = 8888
DEFAULT_TOKEN = "nomi"
DEFAULT_NOTEBOOK = "notebooks/nomi_syntax_tour.ipynb"


def run(args: list[str], *, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    print(f"+ {' '.join(args)}", flush=True)
    return subprocess.run(
        args,
        cwd=ROOT,
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
    )


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def docker_available() -> bool:
    try:
        run(["docker", "version"], capture=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def ensure_macos_docker_runtime(args: argparse.Namespace) -> bool:
    brew = shutil.which("brew")
    if not brew:
        print(
            "Docker is not available and Homebrew was not found. Install Docker Desktop "
            "or Homebrew + Colima, then run this script again.",
            file=sys.stderr,
        )
        return False

    if not command_exists("docker") or not command_exists("colima"):
        run([brew, "install", "docker", "docker-buildx", "docker-compose", "colima"])

    if not docker_available():
        run(
            [
                "colima",
                "start",
                "--cpu",
                str(args.colima_cpu),
                "--memory",
                str(args.colima_memory),
                "--disk",
                str(args.colima_disk),
            ]
        )

    return docker_available()


def ensure_docker_runtime(args: argparse.Namespace) -> bool:
    if docker_available():
        return True

    if args.no_runtime_setup:
        print("Docker is not available. Start/install Docker and run this script again.", file=sys.stderr)
        return False

    if platform.system() == "Darwin":
        print("Docker is not available yet; setting up Docker CLI + Colima with Homebrew.", flush=True)
        return ensure_macos_docker_runtime(args)

    print(
        "Docker is not available. Install Docker for this Linux system, start the daemon, "
        "then run this script again.",
        file=sys.stderr,
    )
    return False


def image_exists(image: str) -> bool:
    result = run(["docker", "image", "inspect", image], check=False, capture=True)
    return result.returncode == 0


def container_exists(name: str) -> bool:
    result = run(["docker", "container", "inspect", name], check=False, capture=True)
    return result.returncode == 0


def container_running(name: str) -> bool:
    result = run(
        ["docker", "container", "inspect", "-f", "{{.State.Running}}", name],
        check=False,
        capture=True,
    )
    return result.returncode == 0 and result.stdout.strip().endswith("true")


def build_image(image: str, rebuild: bool) -> None:
    if rebuild or not image_exists(image):
        args = ["docker", "build", "-t", image, "-f", "Dockerfile", "."]
        run(args)
    else:
        print(f"Image already exists: {image}", flush=True)


def remove_existing_container(name: str) -> None:
    if container_exists(name):
        run(["docker", "rm", "-f", name])


def ensure_container(args: argparse.Namespace, notebook: str) -> None:
    if container_running(args.container_name) and not args.restart_container and not args.rebuild:
        print(f"Container already running: {args.container_name}", flush=True)
        return

    if container_exists(args.container_name):
        remove_existing_container(args.container_name)

    command = [
        "docker",
        "run",
        "-d",
        "--rm",
        "--name",
        args.container_name,
        "-p",
        f"127.0.0.1:{args.port}:8888",
        "-e",
        f"NOMI_JUPYTER_TOKEN={args.token}",
        args.image,
        "--notebook",
        notebook,
        "--token",
        args.token,
    ]
    if args.minimal:
        command.append("--minimal")
    run(command)


def wait_for_jupyter(url: str, timeout: int) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status < 500:
                    return True
        except (
            ConnectionResetError,
            http.client.RemoteDisconnected,
            TimeoutError,
            urllib.error.URLError,
        ):
            time.sleep(1)
    return False


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build and run Nomi's Dockerized Jupyter demo notebook."
    )
    parser.add_argument("--image", default=DEFAULT_IMAGE, help="Docker image tag to build/run.")
    parser.add_argument(
        "--container-name",
        default=DEFAULT_CONTAINER,
        help="Name for the running Docker container.",
    )
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Host port for Jupyter.")
    parser.add_argument("--token", default=DEFAULT_TOKEN, help="Jupyter token.")
    parser.add_argument(
        "--notebook",
        default=DEFAULT_NOTEBOOK,
        help="Notebook path inside the repository to open.",
    )
    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Open notebooks/nomi_minimal.ipynb instead of the syntax tour.",
    )
    parser.add_argument("--no-build", action="store_true", help="Run without building first.")
    parser.add_argument("--rebuild", action="store_true", help="Force a fresh docker build.")
    parser.add_argument(
        "--restart-container",
        action="store_true",
        help="Restart the Jupyter container even if it is already running.",
    )
    parser.add_argument("--no-browser", action="store_true", help="Print the URL without opening it.")
    parser.add_argument(
        "--no-runtime-setup",
        action="store_true",
        help="Do not try to install/start Docker or Colima automatically.",
    )
    parser.add_argument("--colima-cpu", type=int, default=2, help="CPU count for first-time Colima setup.")
    parser.add_argument("--colima-memory", type=int, default=4, help="Memory in GiB for Colima setup.")
    parser.add_argument("--colima-disk", type=int, default=20, help="Disk size in GiB for Colima setup.")
    parser.add_argument(
        "--wait-seconds",
        type=int,
        default=60,
        help="How long to wait for Jupyter before opening the URL.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    notebook = "notebooks/nomi_minimal.ipynb" if args.minimal else args.notebook
    notebook_url = quote(notebook)
    url = f"http://127.0.0.1:{args.port}/lab/tree/{notebook_url}?token={args.token}"
    status_url = f"http://127.0.0.1:{args.port}/api/status?token={args.token}"

    if not ensure_docker_runtime(args):
        return 1

    if not args.no_build:
        build_image(args.image, args.rebuild)

    ensure_container(args, notebook)

    print(f"Waiting for Jupyter at {status_url}", flush=True)
    if not wait_for_jupyter(status_url, args.wait_seconds):
        print("Jupyter did not respond before the timeout. Recent container logs:", file=sys.stderr)
        run(["docker", "logs", "--tail", "80", args.container_name], check=False)
        return 1

    print(f"Nomi notebook is ready: {url}", flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    print(f"Stop it with: docker stop {args.container_name}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
