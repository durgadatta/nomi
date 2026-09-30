from types import SimpleNamespace

import pytest

from scripts import launch_web


def launcher(monkeypatch, *, fail_browser=False):
    events = []
    args = SimpleNamespace(
        no_wasm=True,
        no_manifest=True,
        host="127.0.0.1",
        port=8090,
        strict_port=True,
        no_browser=False,
    )
    monkeypatch.setattr(launch_web, "parse_args", lambda: args)
    monkeypatch.setattr(launch_web, "choose_port", lambda *_args: 8090)

    class Server:
        returncode = None

        def poll(self):
            return self.returncode

        def wait(self, **_options):
            events.append("wait")
            self.returncode = 0
            return 0

        def terminate(self):
            events.append("terminate")

    server = Server()

    def start(*_args, **_options):
        events.append("spawn")
        return server

    def browser(_url):
        events.append("browser")
        if fail_browser:
            raise RuntimeError("browser unavailable")

    monkeypatch.setattr(launch_web.subprocess, "Popen", start)
    monkeypatch.setattr(
        launch_web,
        "wait_for_server",
        lambda *_args: events.append("ready"),
        raising=False,
    )
    monkeypatch.setattr(launch_web.webbrowser, "open", browser)
    return events, server


def test_browser_opens_only_after_server_readiness(monkeypatch):
    events, _ = launcher(monkeypatch)
    assert launch_web.main() == 0
    assert events == ["spawn", "ready", "browser", "wait"]


def test_browser_failure_reaps_server(monkeypatch):
    events, server = launcher(monkeypatch, fail_browser=True)
    with pytest.raises(RuntimeError, match="browser unavailable"):
        launch_web.main()
    assert events == ["spawn", "ready", "browser", "terminate", "wait"]
    assert server.returncode == 0


@pytest.mark.parametrize("port", [-1, 0, 65536])
def test_invalid_ports_fail_before_socket_binding(port):
    with pytest.raises(SystemExit, match="between 1 and 65535"):
        launch_web.choose_port("127.0.0.1", port, False)


def test_busy_maximum_port_does_not_probe_out_of_range(monkeypatch):
    seen = []

    def busy(_host, port):
        seen.append(port)
        return False

    monkeypatch.setattr(launch_web, "port_available", busy)
    with pytest.raises(SystemExit, match="No free port"):
        launch_web.choose_port("127.0.0.1", 65535, False)
    assert seen == [65535]


def test_readiness_reports_early_process_failure():
    server = SimpleNamespace(poll=lambda: 2)
    with pytest.raises(SystemExit, match="code 2"):
        launch_web.wait_for_server(server, "127.0.0.1", 8090)


def test_readiness_timeout_is_bounded():
    server = SimpleNamespace(poll=lambda: None)
    with pytest.raises(SystemExit, match="did not start"):
        launch_web.wait_for_server(server, "127.0.0.1", 8090, timeout=0)


def test_wildcard_readiness_probes_localhost(monkeypatch):
    calls = []

    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            pass

    def connect(address, **_options):
        calls.append(address)
        return Connection()

    monkeypatch.setattr(socket, "create_connection", connect)
    launch_web.wait_for_server(SimpleNamespace(poll=lambda: None), "0.0.0.0", 8090)
    assert calls == [("127.0.0.1", 8090)]


import socket
