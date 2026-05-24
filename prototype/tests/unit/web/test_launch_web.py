import subprocess

import pytest

from scripts import launch_web


def test_build_wasm_reports_remediation_for_failed_toolchain(monkeypatch):
    def fail(*args, **kwargs):
        raise subprocess.CalledProcessError(1, args[0])

    monkeypatch.setattr(launch_web.subprocess, "run", fail)

    with pytest.raises(SystemExit) as excinfo:
        launch_web.build_wasm()

    message = str(excinfo.value)
    assert "WASM parser build failed" in message
    assert "wasm32-unknown-unknown" in message
    assert "wasm-bindgen" in message
    assert "--no-wasm" in message
