"""Install the local Nomi Jupyter kernelspec."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

from jupyter_client.kernelspec import KernelSpecManager


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def kernel_json(root: Path, display_name: str) -> dict:
    pythonpath = str(root)
    existing_pythonpath = os.environ.get("PYTHONPATH")
    if existing_pythonpath:
        pythonpath = pythonpath + os.pathsep + existing_pythonpath

    return {
        "argv": [
            sys.executable,
            "-m",
            "tools.jupyter.nomi_kernel",
            "-f",
            "{connection_file}",
        ],
        "display_name": display_name,
        "language": "nomi",
        "env": {
            "NOMI_PROJECT_ROOT": str(root),
            "PYTHONPATH": pythonpath,
        },
        "metadata": {
            "debugger": False,
        },
    }


def install_kernel(name: str, display_name: str, user: bool, prefix: str | None) -> str:
    root = project_root()
    manager = KernelSpecManager()
    temp_dir = Path(tempfile.mkdtemp(prefix="nomi-kernel-"))

    try:
        (temp_dir / "kernel.json").write_text(
            json.dumps(kernel_json(root, display_name), indent=2),
            encoding="utf-8",
        )
        destination = manager.install_kernel_spec(
            str(temp_dir),
            kernel_name=name,
            user=user,
            prefix=prefix,
        )
        return str(destination)
    finally:
        shutil.rmtree(temp_dir)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Install the Nomi Jupyter kernel.")
    parser.add_argument("--name", default="nomi", help="Kernel name used by Jupyter.")
    parser.add_argument("--display-name", default="Nomi", help="Kernel display name.")
    parser.add_argument("--prefix", help="Install into a specific Jupyter prefix.")
    parser.add_argument(
        "--sys-prefix",
        action="store_true",
        help="Install into sys.prefix instead of the user kernels directory.",
    )
    parser.add_argument(
        "--user",
        action="store_true",
        help="Install into the user kernels directory. This is the default.",
    )
    args = parser.parse_args(argv)

    prefix = sys.prefix if args.sys_prefix else args.prefix
    user = False if prefix else True
    if args.user:
        user = True
        prefix = None

    destination = install_kernel(
        name=args.name,
        display_name=args.display_name,
        user=user,
        prefix=prefix,
    )
    print(f"Installed Nomi kernel '{args.name}' at {destination}")


if __name__ == "__main__":
    main()
