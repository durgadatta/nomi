#!/usr/bin/env python3
"""Friendly command center for the Nomi VS Code extension."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


EXTENSION_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXTENSION_ROOT.parents[2]


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="nomi-vscode",
        description="Manage the local Nomi VS Code extension without remembering npm/vsce details.",
    )
    parser.add_argument(
        "action",
        nargs="?",
        default="help",
        choices=[
            "help",
            "setup",
            "test",
            "package",
            "install-local",
            "enable-local",
            "activate-local",
            "dev",
            "status",
            "clean",
            "publish-check",
            "publish",
        ],
        help="Action to run. Default: help.",
    )
    parser.add_argument(
        "--publisher",
        help="Publisher id to use for publish-check output. This does not edit package.json.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompts for publish.",
    )
    args = parser.parse_args()

    actions = {
        "help": print_help,
        "setup": setup,
        "test": test,
        "package": package,
        "install-local": install_local,
        "enable-local": enable_local,
        "activate-local": enable_local,
        "dev": dev,
        "status": status,
        "clean": clean,
        "publish-check": lambda: publish_check(args.publisher),
        "publish": lambda: publish(args.yes),
    }
    return actions[args.action]()


def print_help() -> int:
    print(
        """Nomi VS Code Extension

Common actions:
  setup          Install npm dependencies
  test           Run VS Code extension tests
  package        Build a local .vsix package
  install-local  Build and install the .vsix into local VS Code / Insiders
  enable-local   Install/update the .vsix and open demo.nomi to activate it
  dev            Open this extension folder in VS Code / Insiders for F5 debugging
  status         Show environment, package, and generated artifact status
  clean          Remove generated local artifacts
  publish-check  Show the Marketplace publishing checklist
  publish        Run tests, package, and publish with vsce

Examples:
  python3 tools/vscode/nomi/scripts/nomi-vscode.py setup
  python3 tools/vscode/nomi/scripts/nomi-vscode.py enable-local
  python3 tools/vscode/nomi/scripts/nomi-vscode.py publish-check --publisher your-publisher
"""
    )
    return 0


def setup() -> int:
    require("npm", "Node.js/npm is required. On macOS: brew install node")
    run(["npm", "install"])
    return 0


def test() -> int:
    ensure_dependencies()
    run(["npm", "test"])
    return 0


def package() -> int:
    ensure_dependencies()
    run(["npm", "run", "package"])
    print(f"\nBuilt: {latest_vsix()}")
    return 0


def install_local() -> int:
    code = require_code()
    package()
    vsix = latest_vsix()
    run([code, "--install-extension", str(vsix), "--force"], cwd=REPO_ROOT)
    print("\nInstalled local Nomi extension package into VS Code.")
    return 0


def enable_local() -> int:
    code = require_code()
    install_local()
    demo = REPO_ROOT / "scripts" / "demo.nomi"
    if demo.exists():
        run([code, "--reuse-window", str(demo)], cwd=REPO_ROOT)
        print("\nOpened scripts/demo.nomi. The Nomi extension activates when a .nomi file opens.")
    else:
        run([code, "--reuse-window", str(REPO_ROOT)], cwd=REPO_ROOT)
        print("\nOpened the Nomi repository. Open any .nomi file to activate the extension.")
    print("If the extension was manually disabled in the UI, re-enable it from the Extensions view.")
    return 0


def dev() -> int:
    code = require_code()
    run([code, str(EXTENSION_ROOT)], cwd=REPO_ROOT)
    print("\nPress F5 in VS Code to launch the Extension Development Host.")
    return 0


def status() -> int:
    package_json = read_package_json()
    print("Nomi VS Code Extension Status")
    print(f"  Extension root: {EXTENSION_ROOT}")
    print(f"  Package: {package_json['publisher']}.{package_json['name']} {package_json['version']}")
    print(f"  node: {version_of('node')}")
    print(f"  npm: {version_of('npm')}")
    print(f"  code: {resolve_code_command() or 'not found'}")
    print(f"  dependencies: {'installed' if (EXTENSION_ROOT / 'node_modules').exists() else 'missing'}")

    vsix_files = sorted(EXTENSION_ROOT.glob("*.vsix"), key=lambda item: item.stat().st_mtime)
    if vsix_files:
        print(f"  latest .vsix: {vsix_files[-1].name}")
    else:
        print("  latest .vsix: none")
    return 0


def clean() -> int:
    paths = [
        EXTENSION_ROOT / "node_modules",
        EXTENSION_ROOT / ".vscode-test",
    ]
    paths.extend(EXTENSION_ROOT.glob("*.vsix"))
    paths.extend(EXTENSION_ROOT.glob("**/__pycache__"))

    for path in paths:
        if not path.exists():
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        print(f"Removed {path.relative_to(EXTENSION_ROOT)}")

    print("Clean complete.")
    return 0


def publish_check(publisher: str | None) -> int:
    package_json = read_package_json()
    publisher = publisher or package_json["publisher"]
    print("Marketplace Publish Checklist")
    print(f"  Publisher id: {publisher}")
    print(f"  Extension id: {publisher}.{package_json['name']}")
    print(f"  Version: {package_json['version']}")
    print("")
    print("Before publishing:")
    print("  1. Confirm publisher in package.json is the real Marketplace publisher id.")
    print("  2. Confirm repository.url points to the public repo.")
    print("  3. Add a LICENSE file or confirm inherited repo licensing is acceptable.")
    print("  4. Add an icon and changelog when ready for public polish.")
    print("  5. Create a Marketplace publisher and Azure DevOps PAT.")
    print(f"  6. Run: cd {EXTENSION_ROOT} && npx vsce login {publisher}")
    print("")
    print("Release command:")
    print(f"  python3 {relative_script()} publish")
    return 0


def publish(yes: bool) -> int:
    package_json = read_package_json()
    if not yes:
        print(f"About to publish {package_json['publisher']}.{package_json['name']} {package_json['version']}.")
        answer = input("Continue? [y/N] ").strip().lower()
        if answer not in {"y", "yes"}:
            print("Publish cancelled.")
            return 1

    test()
    package()
    run(["npx", "vsce", "publish"])
    return 0


def ensure_dependencies() -> None:
    require("npm", "Node.js/npm is required. On macOS: brew install node")
    if not (EXTENSION_ROOT / "node_modules").exists():
        print("Dependencies are missing; running setup first.", flush=True)
        setup()


def read_package_json() -> dict:
    with (EXTENSION_ROOT / "package.json").open(encoding="utf-8") as handle:
        return json.load(handle)


def latest_vsix() -> Path:
    vsix_files = sorted(EXTENSION_ROOT.glob("*.vsix"), key=lambda item: item.stat().st_mtime)
    if not vsix_files:
        raise SystemExit("No .vsix package found. Run the package action first.")
    return vsix_files[-1]


def require(command: str, message: str) -> None:
    if shutil.which(command):
        return
    raise SystemExit(message)


def require_code() -> str:
    code = resolve_code_command()
    if code:
        return code
    raise SystemExit(
        "VS Code's 'code-insiders' or 'code' CLI is required. In VS Code, run: "
        "Shell Command: Install 'code' command in PATH"
    )


def resolve_code_command() -> str | None:
    insiders = shutil.which("code-insiders")
    if insiders:
        return insiders

    code = shutil.which("code")
    if code:
        return code

    candidates = [
        Path("/Applications/Visual Studio Code - Insiders.app/Contents/Resources/app/bin/code-insiders"),
        Path.home() / "Applications/Visual Studio Code - Insiders.app/Contents/Resources/app/bin/code-insiders",
        Path("/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"),
        Path.home() / "Applications/Visual Studio Code.app/Contents/Resources/app/bin/code",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


def run(command: list[str], cwd: Path = EXTENSION_ROOT) -> None:
    print(f"\n$ {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def version_of(command: str) -> str:
    path = shutil.which(command)
    if not path:
        return "not found"
    completed = subprocess.run(
        [command, "--version"],
        cwd=EXTENSION_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip() or completed.stderr.strip() or "unknown"


def relative_script() -> str:
    return str((EXTENSION_ROOT / "scripts" / "nomi-vscode.py").relative_to(REPO_ROOT))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode) from error
