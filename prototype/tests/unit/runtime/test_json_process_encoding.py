import json
import sys

import pytest

from prototype.runtime.backends.json_process import run_json_process


def invoke(source, tmp_path, payload="{}"):
    return run_json_process(
        [sys.executable, "-c", source],
        payload,
        cwd=tmp_path,
        label="encoding-backend",
    )


def test_raw_unicode_round_trips_as_utf8(tmp_path):
    payload = {"text": "caf\u00e9 \u03bb \u65e5"}
    source = "import sys; sys.stdout.buffer.write(sys.stdin.buffer.read())"
    assert invoke(source, tmp_path, json.dumps(payload, ensure_ascii=False)) == payload


def test_binary_success_logs_do_not_corrupt_json_response(tmp_path):
    source = (
        "import sys; sys.stderr.buffer.write(b'\\xff'); "
        "sys.stdout.buffer.write(b'{\"ok\": true}')"
    )
    assert invoke(source, tmp_path) == {"ok": True}


def test_invalid_utf8_response_names_transport_boundary(tmp_path):
    with pytest.raises(RuntimeError, match="encoding-backend returned invalid UTF-8"):
        invoke("import sys; sys.stdout.buffer.write(b'\\xff')", tmp_path)


def test_binary_failure_logs_preserve_process_failure(tmp_path):
    source = "import sys; sys.stderr.buffer.write(b'failure \\xff'); sys.exit(2)"
    with pytest.raises(RuntimeError, match="encoding-backend failed: failure"):
        invoke(source, tmp_path)


def test_unencodable_request_is_rejected_before_process_starts(tmp_path):
    marker = tmp_path / "started"
    source = "from pathlib import Path; Path('started').touch()"
    with pytest.raises(
        RuntimeError, match="encoding-backend request is not valid UTF-8"
    ):
        invoke(source, tmp_path, '{"text": "\ud800"}')
    assert not marker.exists()


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_non_json_constants_are_rejected_in_nested_response(tmp_path, constant):
    output = '{"values": [' + constant + "]}"
    with pytest.raises(RuntimeError, match="encoding-backend returned invalid JSON"):
        invoke(f"print({output!r})", tmp_path)
