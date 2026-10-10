"""Developer retrieval tools require an owned config outside a checkout."""

import json
import subprocess
import sys

import pytest

from prototype.tests.e2e import test_distribution_boundary as wheel_helpers

distribution = wheel_helpers.distribution


def run_installed(installed, cwd, module, arguments, stdin=""):
    code = (
        f"import sys; sys.path.insert(0, {str(installed)!r}); "
        f"sys.argv={[module, *arguments]!r}; from {module} import main; main()"
    )
    return subprocess.run(
        [sys.executable, "-I", "-c", code], cwd=cwd, input=stdin,
        capture_output=True, text=True, timeout=20,
    )


@pytest.mark.parametrize("module", ["tools.rag_mcp.cli", "tools.rag_mcp.mcp_server"])
def test_installed_default_explains_checkout_config_without_traceback(distribution, tmp_path, module):
    installed, _ = distribution
    result = run_installed(installed, tmp_path, module, ["build"] if module.endswith("cli") else [])
    assert result.returncode == 2
    assert result.stdout == ""
    assert "--config /absolute/path" in result.stderr
    assert "not shipped in the wheel" in result.stderr
    assert "Traceback" not in result.stderr
    assert not (installed / ".nomi").exists()


def test_installed_explicit_config_builds_searches_and_starts_mcp(distribution, tmp_path):
    installed, _ = distribution
    source = tmp_path / "notes"
    source.mkdir()
    (source / "lesson.md").write_text("Binding constraints describe local contracts.\n")
    config = tmp_path / "rag_sources.json"
    config.write_text(json.dumps({
        "index_path": "cache/index.json",
        "sources": [{"name": "notes", "path": "notes", "include": ["**/*.md"]}],
    }))
    arguments = ["--config", str(config)]
    build = run_installed(installed, tmp_path, "tools.rag_mcp.cli", arguments + ["build"])
    assert build.returncode == 0, build.stderr
    assert "Indexed 1 chunks" in build.stdout
    assert (tmp_path / "cache/index.json").exists()
    search = run_installed(
        installed, tmp_path, "tools.rag_mcp.cli", arguments + ["search", "binding constraints"],
    )
    assert search.returncode == 0, search.stderr
    assert "lesson.md:1" in search.stdout
    assert "Binding constraints" in search.stdout
    request = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}) + "\n"
    mcp = run_installed(installed, tmp_path, "tools.rag_mcp.mcp_server", arguments, request)
    assert mcp.returncode == 0, mcp.stderr
    assert mcp.stderr == ""
    response = json.loads(mcp.stdout)
    assert response["id"] == 1
    assert response["result"]["serverInfo"]["name"] == "nomi-rag"
    assert not (installed / ".nomi").exists()
