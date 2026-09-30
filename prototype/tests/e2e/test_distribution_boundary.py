import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope="module")
def distribution(tmp_path_factory):
    build_root = tmp_path_factory.mktemp("distribution-build")
    for name in ("pyproject.toml", "README.md"):
        shutil.copy2(ROOT / name, build_root / name)
    ignored = shutil.ignore_patterns(
        "node_modules", "target", "__pycache__", ".vscode-test", "*.vsix"
    )
    for name in ("prototype", "scripts", "tools"):
        shutil.copytree(ROOT / name, build_root / name, ignore=ignored)
    wheels = build_root / "wheels"
    build = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            "--no-build-isolation",
            "--wheel-dir",
            str(wheels),
            str(build_root),
        ],
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    assert build.returncode == 0, build.stdout + build.stderr
    wheel = next(wheels.glob("nomi-*.whl"))
    installed = build_root / "installed"
    with zipfile.ZipFile(wheel) as archive:
        archive.extractall(installed)
        names = set(archive.namelist())
    return installed, names


def test_wheel_contains_runtime_assets_not_test_packages(distribution):
    _, names = distribution
    required = {
        "prototype/grammar/layers/bindings.lark",
        "prototype/grammar/pattern_surface.lark",
        "prototype/runtime/host_capabilities.json",
        "prototype/runtime/js/core_runtime.js",
        "prototype/runtime/js/lower_to_core_ir.js",
        "prototype/runtime/js/pkg/nomi_parser_worker_bg.wasm",
        "scripts/demo.nomi",
    }
    assert required <= names
    assert not any(name.startswith("prototype/tests/") for name in names)


def test_wheel_runs_runtime_and_default_cli_outside_checkout(distribution, tmp_path):
    installed, _ = distribution
    code = "\n".join(
        [
            "import sys",
            f"sys.path.insert(0, {str(installed)!r})",
            "import prototype",
            "from prototype.runtime import execute",
            "result = execute(source='x = 2\\nprint(x + 3)\\n')",
            "assert result.stdout == '5\\n'",
            f"assert prototype.__file__.startswith({str(installed)!r})",
            "from scripts.cli import main",
            "sys.argv = ['nomi']",
            "main()",
        ]
    )
    result = subprocess.run(
        [sys.executable, "-I", "-c", code],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Nomi Demo: Key Features" in result.stdout


def test_source_cli_help_needs_neither_install_nor_parser_import(tmp_path):
    result = subprocess.run(
        [sys.executable, "-I", "-S", str(ROOT / "scripts/cli.py"), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "--parser-frontend" in result.stdout


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is required")
def test_wheel_can_select_the_js_backend_outside_checkout(distribution, tmp_path):
    installed, _ = distribution
    code = "\n".join(
        [
            "import sys",
            f"sys.path.insert(0, {str(installed)!r})",
            "from prototype.runtime import execute",
            "result = execute(source='print(2 + 3)\\n', eval_backend='js-core-runtime')",
            "assert result.stdout == '5\\n'",
        ]
    )
    result = subprocess.run(
        [sys.executable, "-I", "-c", code],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_python_version_requirement_names_the_ast_boundary():
    import tomllib

    with (ROOT / "pyproject.toml").open("rb") as handle:
        metadata = tomllib.load(handle)
    assert metadata["project"]["requires-python"] == ">=3.12"
