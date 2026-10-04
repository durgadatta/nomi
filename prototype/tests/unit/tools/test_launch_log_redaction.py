"""Redaction applies to launcher-owned output, not Jupyter's own server logs."""

from urllib.parse import parse_qs, urlparse

import pytest

from scripts import run_nomi_docker as launcher
from tools.docker import serve_nomi_notebook as entrypoint
from tools.docker.launch_logging import redacted_command, unauthenticated_url


@pytest.mark.parametrize("invoke", [launcher.run, entrypoint.run_step])
def test_logged_secrets_are_redacted_but_real_arguments_are_preserved(
    monkeypatch, capsys, tmp_path, invoke
):
    secret = "a&b=/# c+%?"
    arguments = [
        "command",
        "-e",
        f"NOMI_JUPYTER_TOKEN={secret}",
        "--token",
        secret,
        f"--ServerApp.token={secret}",
        "--password",
        secret,
    ]
    observed = []
    monkeypatch.setattr(
        launcher.subprocess, "run", lambda args, **kwargs: observed.append(args)
    )
    if invoke is launcher.run:
        invoke(arguments)
    else:
        invoke(arguments, cwd=tmp_path)
    assert observed == [arguments]
    assert secret not in capsys.readouterr().out
    assert arguments[4] == secret


def test_redaction_handles_split_flags_without_mutating_source():
    arguments = ["python", "--ServerApp.token", "secret", "--notebook", "file.ipynb"]
    assert redacted_command(arguments) == [
        "python",
        "--ServerApp.token",
        "<redacted>",
        "--notebook",
        "file.ipynb",
    ]
    assert arguments[2] == "secret"


def test_printable_url_removes_only_authentication_query_values():
    url = "http://127.0.0.1:8888/lab?token=a%26b&path=a%2Fb&token=two&password=p#cell"
    printable = unauthenticated_url(url)
    assert parse_qs(urlparse(printable).query) == {"path": ["a/b"]}
    assert urlparse(printable).fragment == "cell"


@pytest.mark.parametrize("no_browser", [False, True])
def test_host_launcher_prints_no_authenticated_url(monkeypatch, capsys, no_browser):
    secret = "do-not-log-me&value"
    observed = []
    monkeypatch.setattr(launcher, "ensure_docker_runtime", lambda args: True)
    monkeypatch.setattr(launcher, "ensure_container", lambda args, notebook: None)
    monkeypatch.setattr(launcher, "wait_for_jupyter", lambda url, timeout: True)
    monkeypatch.setattr(launcher.webbrowser, "open", observed.append)
    options = ["--no-build", "--token", secret]
    if no_browser:
        options.append("--no-browser")
    assert launcher.main(options) == 0
    printed = capsys.readouterr().out
    assert secret not in printed
    assert "token=" not in printed
    if no_browser:
        assert observed == []
        assert "Jupyter login" in printed
    else:
        assert parse_qs(urlparse(observed[0]).query) == {"token": [secret]}


def test_docker_context_excludes_local_state_and_common_credential_files():
    from pathlib import Path

    root = Path(__file__).resolve().parents[4]
    rules = set((root / ".dockerignore").read_text(encoding="utf-8").splitlines())
    assert {
        ".nomi",
        ".codex",
        ".claude",
        ".opencode",
        ".agents",
        "**/.env",
        "**/.env.*",
        "**/*.pem",
        "**/*.key",
    } <= rules
