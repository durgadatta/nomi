"""Notebook diagnostics adapt runtime records without exposing host frames."""

import pytest

from tools.jupyter.nomi_kernel import NomiKernel


@pytest.fixture
def notebook(monkeypatch):
    kernel = NomiKernel()
    messages = []
    monkeypatch.setattr(kernel, "send_response", lambda _socket, kind, content: messages.append((kind, content)))
    return kernel, messages


def test_failed_cell_publishes_error_and_keeps_prior_output_and_state(notebook):
    kernel, messages = notebook
    reply = kernel.do_execute("quantity = 3\nprint('before')\nquantity + 'wrong'", silent=False)
    assert reply["status"] == "error"
    assert reply["ename"] == "TypeError"
    assert reply["nomi_diagnostics"][0]["code"] == "NOMI-RUNTIME"
    assert messages[-1] == ("error", {key: reply[key] for key in ("ename", "evalue", "traceback", "nomi_diagnostics")})
    assert ("stream", {"name": "stdout", "text": "before"}) in messages
    assert "File \"" not in "\n".join(reply["traceback"])
    assert "Traceback (most recent call last)" not in "\n".join(reply["traceback"])
    assert kernel.do_execute("quantity + 1", silent=False)["status"] == "ok"
    assert messages[-1][1]["data"]["text/plain"] == "4"


def test_parse_error_keeps_source_coordinates_and_excerpt(notebook):
    kernel, messages = notebook
    reply = kernel.do_execute("quantity =\n", silent=False)
    record = reply["nomi_diagnostics"][0]
    assert record["code"] == "NOMI-PARSE"
    assert record["span"]["line"] == 1
    assert record["source_excerpt"] == "quantity ="
    assert "quantity =" in "\n".join(reply["traceback"])
    assert "line 1" in "\n".join(reply["traceback"])
    assert messages[-1][0] == "error"


@pytest.mark.parametrize("source", ["missing", "%unknown", "%run missing.nomi", "%ast\nquantity ="])
def test_silent_failure_returns_error_without_publishing(notebook, source):
    kernel, messages = notebook
    reply = kernel.do_execute(source, silent=True)
    assert reply["status"] == "error"
    assert reply["traceback"]
    assert messages == []
    assert "Traceback (most recent call last)" not in "\n".join(reply["traceback"])


def test_run_command_uses_the_same_runtime_diagnostic_contract(notebook, tmp_path):
    kernel, messages = notebook
    path = tmp_path / "broken.nomi"
    path.write_text("quantity =\n", encoding="utf-8")
    reply = kernel.do_execute(f"%run {path}", silent=False)
    assert reply["nomi_diagnostics"][0]["code"] == "NOMI-PARSE"
    assert reply["nomi_diagnostics"][0]["span"]["filename"] == str(path)
    assert messages[-1][0] == "error"
