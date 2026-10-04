"""Notebook launch credentials and reuse are deliberate, bounded contracts."""

import json
import subprocess
from email.message import Message

import pytest

from scripts import run_nomi_docker as launcher
from tools.docker import serve_nomi_notebook as entrypoint


def inspection(
    *, image="nomi:jupyter", port="8888", host="127.0.0.1", token="private-token"
):
    return [
        {
            "Config": {
                "Image": image,
                "Env": [f"NOMI_JUPYTER_TOKEN={token}"],
                "Cmd": [
                    "--notebook",
                    "notebooks/nomi_syntax_tour.ipynb",
                    "--token",
                    token,
                ],
            },
            "NetworkSettings": {
                "Ports": {"8888/tcp": [{"HostIp": host, "HostPort": port}]}
            },
        }
    ]


@pytest.mark.parametrize("parse", [launcher.parse_args, entrypoint.parse_args])
def test_default_token_is_not_a_shared_credential(monkeypatch, parse):
    monkeypatch.delenv("NOMI_JUPYTER_TOKEN", raising=False)
    assert parse([]).token is None


@pytest.mark.parametrize("parse", [launcher.parse_args, entrypoint.parse_args])
def test_blank_tokens_are_rejected_before_startup(parse):
    with pytest.raises(SystemExit) as error:
        parse(["--token", ""])
    assert error.value.code == 2


@pytest.mark.parametrize(
    "changes",
    [{"image": "different"}, {"port": "9999"}, {"host": "0.0.0.0"}, {"token": ""}],
)
def test_incompatible_running_container_is_not_reused_or_removed(
    monkeypatch, changes, capsys
):
    args = launcher.parse_args(["--token", "private-token"])
    commands = []
    monkeypatch.setattr(launcher, "container_running", lambda name: True)

    def run(command, **kwargs):
        commands.append(command)
        return subprocess.CompletedProcess(
            command, 0, json.dumps(inspection(**changes))
        )

    monkeypatch.setattr(launcher, "run", run)
    with pytest.raises(RuntimeError, match="restart-container"):
        launcher.ensure_container(args, launcher.DEFAULT_NOTEBOOK)
    assert all(command[1:3] == ["container", "inspect"] for command in commands)
    assert "private-token" not in capsys.readouterr().out


def test_matching_reuse_recovers_existing_token_without_printing_it(
    monkeypatch, capsys
):
    monkeypatch.delenv("NOMI_JUPYTER_TOKEN", raising=False)
    args = launcher.parse_args([])
    monkeypatch.setattr(launcher, "container_running", lambda name: True)
    monkeypatch.setattr(
        launcher,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(
            command, 0, json.dumps(inspection())
        ),
    )
    launcher.ensure_container(args, launcher.DEFAULT_NOTEBOOK)
    assert args.token == "private-token"
    assert args.token not in capsys.readouterr().out


def test_new_container_gets_a_generated_token(monkeypatch):
    monkeypatch.delenv("NOMI_JUPYTER_TOKEN", raising=False)
    args = launcher.parse_args([])
    commands = []
    monkeypatch.setattr(launcher, "container_running", lambda name: False)
    monkeypatch.setattr(launcher, "container_exists", lambda name: False)
    monkeypatch.setattr(
        launcher, "run", lambda command, **kwargs: commands.append(command)
    )
    launcher.ensure_container(args, launcher.DEFAULT_NOTEBOOK)
    assert len(args.token) >= 32
    assert args.token != "nomi"
    assert f"NOMI_JUPYTER_TOKEN={args.token}" in commands[0]


def test_timeout_logs_do_not_echo_the_configured_credential(monkeypatch, capsys):
    token = "private-token&data"
    monkeypatch.setattr(launcher, "ensure_docker_runtime", lambda args: True)
    monkeypatch.setattr(launcher, "ensure_container", lambda args, notebook: None)
    monkeypatch.setattr(launcher, "wait_for_jupyter", lambda url, timeout: False)

    def run(command, **kwargs):
        assert kwargs.get("capture") is True
        return subprocess.CompletedProcess(
            command, 0, f"URL ?token=private-token%26data\n{token}"
        )

    monkeypatch.setattr(launcher, "run", run)
    assert launcher.main(["--no-build", "--no-browser", "--token", token]) == 1
    output = capsys.readouterr()
    assert token not in output.out + output.err
    assert "private-token%26data" not in output.out + output.err


@pytest.mark.parametrize(
    "content_type,body,expected",
    [
        ("text/html", b"<html>login</html>", False),
        ("application/json", b"{}", False),
        ("application/json", b"not-json", False),
        ("application/json", b'{"kernels": 0, "connections": 0}', True),
    ],
)
def test_readiness_requires_a_status_response_not_a_login_page(
    monkeypatch, content_type, body, expected
):
    class Response:
        status = 200
        headers = Message()
        headers["Content-Type"] = content_type

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, limit):
            return body

    ticks = iter([0, 0, 2])
    monkeypatch.setattr(launcher.time, "monotonic", lambda: next(ticks))
    monkeypatch.setattr(launcher.time, "sleep", lambda duration: None)
    monkeypatch.setattr(
        launcher.urllib.request, "urlopen", lambda *args, **kwargs: Response()
    )
    assert launcher.wait_for_jupyter("http://127.0.0.1/api/status", 1) is expected


def test_legacy_fixed_token_requires_explicit_restart_or_opt_in(monkeypatch):
    monkeypatch.delenv("NOMI_JUPYTER_TOKEN", raising=False)
    monkeypatch.setattr(launcher, "container_running", lambda name: True)
    monkeypatch.setattr(
        launcher,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(
            command, 0, json.dumps(inspection(token="nomi"))
        ),
    )
    with pytest.raises(RuntimeError, match="restart-container"):
        launcher.ensure_container(launcher.parse_args([]), launcher.DEFAULT_NOTEBOOK)
    args = launcher.parse_args(["--token", "nomi"])
    launcher.ensure_container(args, launcher.DEFAULT_NOTEBOOK)
    assert args.token == "nomi"


@pytest.mark.parametrize("parse", [launcher.parse_args, entrypoint.parse_args])
def test_blank_environment_credentials_are_rejected(monkeypatch, parse):
    monkeypatch.setenv("NOMI_JUPYTER_TOKEN", "   ")
    with pytest.raises(SystemExit):
        parse([])


def test_entrypoint_generates_and_redacts_current_identity_provider_token(
    monkeypatch, capsys
):
    monkeypatch.delenv("NOMI_JUPYTER_TOKEN", raising=False)
    monkeypatch.setattr(entrypoint, "running_inside_container", lambda: True)
    monkeypatch.setattr(
        entrypoint.secrets, "token_urlsafe", lambda size: "generated-private-token"
    )
    commands = []
    monkeypatch.setattr(
        entrypoint.subprocess, "run", lambda args, **kwargs: commands.append(args)
    )
    entrypoint.main(["--skip-kernel-install"])
    assert "--IdentityProvider.token=generated-private-token" in commands[0]
    assert "generated-private-token" not in capsys.readouterr().out
