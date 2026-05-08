"""Start Jupyter Lab inside the Nomi Docker image.

This module is the Docker image entrypoint. When run directly from a local
checkout, it delegates to scripts/run_nomi_docker.py so accidental VS Code task
invocations still use the Docker flow.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote


def project_root() -> Path:
    configured = Path(os.environ.get("NOMI_PROJECT_ROOT", "/workspace")).resolve()
    if configured.exists():
        return configured
    return Path(__file__).resolve().parents[2]


def run_step(args: list[str], *, cwd: Path) -> None:
    print(f"+ {' '.join(args)}", flush=True)
    subprocess.run(args, cwd=cwd, check=True)


def install_kernel(root: Path) -> None:
    run_step([sys.executable, "-m", "tools.jupyter.install_nomi_kernel", "--user"], cwd=root)


def running_inside_container() -> bool:
    return Path("/.dockerenv").exists()


def delegate_to_host_launcher(root: Path, args: argparse.Namespace) -> None:
    command = [sys.executable, str(root / "scripts" / "run_nomi_docker.py")]
    if args.minimal:
        command.append("--minimal")
    if args.notebook != str(root / "notebooks" / "nomi_syntax_tour.ipynb"):
        command.extend(["--notebook", args.notebook])
    if args.port != "8888":
        command.extend(["--port", args.port])
    if args.token != "nomi":
        command.extend(["--token", args.token])
    run_step(command, cwd=root)


def notebook_url(root: Path, notebook: Path) -> str:
    try:
        relative_notebook = notebook.relative_to(root)
    except ValueError:
        relative_notebook = notebook
    return quote(relative_notebook.as_posix())


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    root = project_root()
    default_host = os.environ.get("NOMI_JUPYTER_HOST")
    if default_host is None:
        default_host = "0.0.0.0" if root == Path("/workspace") else "127.0.0.1"
    parser = argparse.ArgumentParser(description="Serve the Nomi Jupyter demo notebook.")
    parser.add_argument(
        "--notebook",
        default=str(root / "notebooks" / "nomi_syntax_tour.ipynb"),
        help="Notebook path to open inside Jupyter Lab.",
    )
    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Open notebooks/nomi_minimal.ipynb instead of the syntax tour.",
    )
    parser.add_argument(
        "--host",
        default=default_host,
        help="Jupyter bind host inside the container.",
    )
    parser.add_argument(
        "--port",
        default=os.environ.get("NOMI_JUPYTER_PORT", "8888"),
        help="Jupyter bind port inside the container.",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("NOMI_JUPYTER_TOKEN", "nomi"),
        help="Jupyter token. Set to an empty string to disable token auth.",
    )
    parser.add_argument(
        "--skip-kernel-install",
        action="store_true",
        help="Do not refresh the Nomi kernelspec before launching Jupyter.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    root = project_root()
    args = parse_args(argv)

    if not running_inside_container() and os.environ.get("NOMI_ALLOW_LOCAL_JUPYTER") != "1":
        delegate_to_host_launcher(root, args)
        return

    notebook = root / "notebooks" / "nomi_minimal.ipynb" if args.minimal else Path(args.notebook)
    if not notebook.is_absolute():
        notebook = root / notebook
    notebook = notebook.resolve()

    if not notebook.exists():
        raise SystemExit(f"Notebook not found under runtime root {root}: {notebook}")

    if not args.skip_kernel_install:
        install_kernel(root)

    command = [
        sys.executable,
        "-m",
        "jupyterlab",
        f"--ServerApp.ip={args.host}",
        f"--ServerApp.port={args.port}",
        "--ServerApp.open_browser=False",
        f"--ServerApp.root_dir={root}",
        f"--ServerApp.default_url=/lab/tree/{notebook_url(root, notebook)}",
        f"--ServerApp.token={args.token}",
        "--ServerApp.password=",
        "--LabServerApp.notebook_starts_kernel=True",
    ]
    run_step(command, cwd=root)


if __name__ == "__main__":
    main()
