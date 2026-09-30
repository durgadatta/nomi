from types import SimpleNamespace

import pytest

from tools.jupyter import nomi_kernel


@pytest.fixture
def kernel(monkeypatch):
    instance = nomi_kernel.NomiKernel()
    messages = []
    monkeypatch.setattr(
        instance,
        "send_response",
        lambda _socket, kind, content: messages.append((kind, content)),
    )
    return instance, messages


def test_silent_execution_keeps_state_without_streaming_output(kernel):
    instance, messages = kernel
    reply = instance.do_execute("x = 2\nprint(x)\nx + 3", silent=True)
    assert reply["status"] == "ok"
    assert instance.runtime_session.bindings["x"] == 2
    assert messages == []


@pytest.mark.parametrize("command", ["%who", "%help", "%ast\nx = 1"])
def test_silent_kernel_commands_do_not_publish_output(kernel, command):
    instance, messages = kernel
    reply = instance.do_execute(command, silent=True)
    assert reply["status"] == "ok"
    assert messages == []


def test_ast_and_completeness_use_runtime_inspection_without_execution(
    kernel, monkeypatch
):
    instance, messages = kernel
    calls = []

    def inspect_runtime(**options):
        calls.append(options)
        return SimpleNamespace(output="runtime AST")

    monkeypatch.setattr(nomi_kernel, "inspect_runtime", inspect_runtime, raising=False)
    assert instance.do_is_complete("x = 1") == {"status": "complete"}
    assert instance.do_execute("%ast\nx = 1", silent=False)["status"] == "ok"
    assert len(calls) == 2
    assert all(
        call["source"] == "x = 1\n" and call["stage"] == "python_ast" for call in calls
    )
    assert messages[-1] == ("stream", {"name": "stdout", "text": "runtime AST\n"})
    assert "x" not in instance.runtime_session.bindings


def test_completion_and_who_use_public_session_bindings(kernel):
    instance, messages = kernel
    instance.runtime_session = SimpleNamespace(
        bindings={"apple": 1, "apricot": 2, "__hidden": 3}
    )
    reply = instance.do_complete("ap", 2)
    assert reply["matches"] == ["apple", "apricot"]
    assert instance.do_execute("%who", silent=False)["status"] == "ok"
    assert messages[-1][1]["text"] == "apple\napricot\n"
