import io
import json
import sys

import pytest

from tools.rag_mcp.mcp_server import NomiRagMcpServer


@pytest.mark.parametrize(
    "bad,code",
    [
        ("not JSON", -32700),
        ("null", -32600),
        ("[]", -32600),
        ("12", -32600),
        ('{"jsonrpc":"1.0","method":"tools/list","id":1}', -32600),
        ('{"jsonrpc":"2.0","method":null,"id":1}', -32600),
    ],
)
def test_stdio_bad_frames_report_protocol_errors_then_continue(
    tmp_path, monkeypatch, bad, code
):
    config = tmp_path / "rag.json"
    config.write_text('{"sources": []}')
    output = io.StringIO()
    valid = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    monkeypatch.setattr(sys, "stdin", io.StringIO(f"{bad}\n{valid}\n"))
    monkeypatch.setattr(sys, "stdout", output)
    NomiRagMcpServer(str(config)).serve()
    responses = [json.loads(line) for line in output.getvalue().splitlines()]
    assert len(responses) == 2
    assert responses[0]["id"] is None
    assert responses[0]["error"]["code"] == code
    assert responses[1]["id"] == 2
    assert responses[1]["result"]["tools"]


def test_stdio_whitespace_and_notifications_produce_no_response(tmp_path, monkeypatch):
    config = tmp_path / "rag.json"
    config.write_text('{"sources": []}')
    output = io.StringIO()
    notification = json.dumps({"jsonrpc": "2.0", "method": "tools/list"})
    monkeypatch.setattr(sys, "stdin", io.StringIO(f"\n   \n{notification}\n"))
    monkeypatch.setattr(sys, "stdout", output)
    NomiRagMcpServer(str(config)).serve()
    assert output.getvalue() == ""
