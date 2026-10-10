"""Configuration failures should explain recovery without protocol pollution."""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]


@pytest.mark.parametrize("module", ["tools.rag_mcp.cli", "tools.rag_mcp.mcp_server"])
@pytest.mark.parametrize("contents", [None, "{", "[]", '{"sources": [3]}'])
def test_configuration_startup_failure_is_actionable_and_keeps_stdout_empty(
    tmp_path, module, contents,
):
    config = tmp_path / "rag.json"
    if contents is not None:
        config.write_text(contents)
    command = [sys.executable, "-m", module, "--config", str(config)]
    if module.endswith("cli"):
        command.append("build")
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=20)
    assert result.returncode == 2
    assert result.stdout == ""
    assert "Traceback" not in result.stderr
    assert str(config) in result.stderr
    if contents is None:
        assert "--config" in result.stderr
    assert not (tmp_path / ".nomi").exists()
