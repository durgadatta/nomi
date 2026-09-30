from urllib.parse import parse_qs, urlparse

import pytest

from scripts import run_nomi_docker as launcher


@pytest.mark.parametrize(
    "option,value",
    [
        ("--port", "-1"),
        ("--port", "0"),
        ("--port", "65536"),
        ("--wait-seconds", "0"),
        ("--wait-seconds", "-1"),
        ("--colima-cpu", "0"),
        ("--colima-cpu", "-1"),
        ("--colima-memory", "0"),
        ("--colima-memory", "-1"),
        ("--colima-disk", "0"),
        ("--colima-disk", "-1"),
    ],
)
def test_invalid_options_stop_before_docker_setup(monkeypatch, option, value):
    def unexpected_setup(args):
        pytest.fail("invalid options reached Docker setup")

    monkeypatch.setattr(launcher, "ensure_docker_runtime", unexpected_setup)
    with pytest.raises(SystemExit) as error:
        launcher.main([option, value])
    assert error.value.code == 2


@pytest.mark.parametrize("port", [1, 65535])
def test_valid_port_boundaries_are_preserved(port):
    assert launcher.parse_args(["--port", str(port)]).port == port


def test_defaults_remain_unchanged():
    args = launcher.parse_args([])
    assert (args.port, args.wait_seconds) == (8888, 60)
    assert (args.colima_cpu, args.colima_memory, args.colima_disk) == (2, 4, 20)


def test_token_is_one_query_value_in_status_and_notebook_urls(monkeypatch):
    token = "a&b=/# c+%?"
    observed = {}
    monkeypatch.setattr(launcher, "ensure_docker_runtime", lambda args: True)
    monkeypatch.setattr(launcher, "ensure_container", lambda args, notebook: None)
    monkeypatch.setattr(
        launcher.webbrowser, "open", lambda url: observed.update(open=url)
    )

    def ready(url, timeout):
        observed["status"] = url
        return True

    monkeypatch.setattr(launcher, "wait_for_jupyter", ready)
    assert launcher.main(["--token", token, "--no-build"]) == 0
    for url in observed.values():
        parsed = urlparse(url)
        assert parsed.fragment == ""
        assert parse_qs(parsed.query) == {"token": [token]}
