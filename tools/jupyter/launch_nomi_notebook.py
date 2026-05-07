"""Install the Nomi kernel and launch the syntax tour notebook."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run_step(args: list[str], *, cwd: Path) -> None:
    print(f"+ {' '.join(args)}")
    subprocess.run(args, cwd=cwd, check=True)


def install_dependencies(root: Path) -> None:
    run_step([sys.executable, "-m", "pip", "install", "-e", ".[jupyter]"], cwd=root)


def install_kernel(root: Path) -> None:
    run_step([sys.executable, "-m", "tools.jupyter.install_nomi_kernel", "--user"], cwd=root)


def check_kernel(root: Path) -> None:
    run_step([sys.executable, "-m", "tools.jupyter.check_nomi_kernel"], cwd=root)


def launch_notebook(root: Path, notebook: Path, no_browser: bool) -> None:
    server_root = root
    try:
        relative_notebook = notebook.relative_to(server_root)
    except ValueError:
        server_root = notebook.parent
        relative_notebook = Path(notebook.name)

    notebook_url = quote(relative_notebook.as_posix())
    args = [
        sys.executable,
        "-m",
        "notebook",
        f"--ServerApp.root_dir={server_root}",
        f"--ServerApp.default_url=/lab/tree/{notebook_url}",
        "--LabServerApp.notebook_starts_kernel=True",
    ]
    if no_browser:
        args.append("--no-browser")
    run_step(args, cwd=root)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    root = project_root()
    default_notebook = root / "notebooks" / "nomi_syntax_tour.ipynb"
    minimal_notebook = root / "notebooks" / "nomi_minimal.ipynb"

    parser = argparse.ArgumentParser(
        description="Install the local Nomi Jupyter kernel and open the syntax tour notebook."
    )
    parser.add_argument(
        "notebook",
        nargs="?",
        type=Path,
        default=default_notebook,
        help="Notebook to open. Defaults to notebooks/nomi_syntax_tour.ipynb.",
    )
    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Open notebooks/nomi_minimal.ipynb instead of the full syntax tour.",
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Do not run pip install -e '.[jupyter]' before launching.",
    )
    parser.add_argument(
        "--skip-check",
        action="store_true",
        help="Do not run the Nomi kernel smoke check before launching.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Start Notebook without opening a browser window.",
    )
    args = parser.parse_args(argv)
    if args.minimal:
        args.notebook = minimal_notebook
    return args


def main(argv: list[str] | None = None) -> None:
    root = project_root()
    args = parse_args(argv)
    notebook = args.notebook.expanduser()
    if not notebook.is_absolute():
        notebook = root / notebook
    notebook = notebook.resolve()

    if not notebook.exists():
        raise SystemExit(f"Notebook not found: {notebook}")

    if not args.skip_install:
        install_dependencies(root)
    install_kernel(root)
    if not args.skip_check:
        check_kernel(root)
    launch_notebook(root, notebook, args.no_browser)


if __name__ == "__main__":
    main()
