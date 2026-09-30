import json
import sys

import pytest

from prototype.runtime.backends.json_process import run_json_process


def invoke(source, tmp_path, payload="{}", **options):
    return run_json_process(
        [sys.executable, "-c", source],
        payload,
        cwd=tmp_path,
        label="test-backend",
        **options,
    )


def test_transport_passes_json_without_shell_interpretation(tmp_path):
    payload = {"text": '\'; $(exit 1)\n"quoted"', "values": [1, 2]}
    source = "import sys; sys.stdout.write(sys.stdin.read())"
    assert invoke(source, tmp_path, json.dumps(payload)) == payload


def test_successful_stderr_is_not_part_of_json_response(tmp_path):
    source = "import sys; print('log', file=sys.stderr); print('{\"ok\": true}')"
    assert invoke(source, tmp_path) == {"ok": True}


@pytest.mark.parametrize("output", ["not json", "[]", "null", "12"])
def test_invalid_backend_response_names_the_boundary(tmp_path, output):
    with pytest.raises(RuntimeError, match="test-backend (returned|response)"):
        invoke(f"print({output!r})", tmp_path)


def test_process_failure_preserves_stderr_detail(tmp_path):
    source = "import sys; print('failure detail', file=sys.stderr); sys.exit(2)"
    with pytest.raises(RuntimeError, match="test-backend failed: failure detail"):
        invoke(source, tmp_path)


def test_transport_can_bound_a_configured_process(tmp_path):
    with pytest.raises(RuntimeError, match="test-backend timed out"):
        invoke("import time; time.sleep(10)", tmp_path, timeout=0.05)


def test_missing_executable_names_the_boundary(tmp_path):
    with pytest.raises(RuntimeError, match="test-backend could not start"):
        run_json_process(
            [str(tmp_path / "missing")], "{}", cwd=tmp_path, label="test-backend"
        )
