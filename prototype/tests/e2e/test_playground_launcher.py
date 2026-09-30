import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]


def test_local_launcher_serves_checkout_and_reaps_server_on_interrupt(tmp_path):
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    command = [
        sys.executable,
        "-u",
        str(ROOT / "scripts/launch_web.py"),
        "--no-wasm",
        "--no-manifest",
        "--no-browser",
        "--strict-port",
        "--port",
        str(port),
    ]
    launcher = subprocess.Popen(
        command,
        cwd=tmp_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            assert launcher.poll() is None, (
                "launcher exited before serving the playground"
            )
            try:
                with urlopen(f"http://127.0.0.1:{port}/web/", timeout=0.5) as response:
                    assert "Nomi" in response.read().decode()
                break
            except URLError:
                time.sleep(0.05)
        else:
            raise AssertionError("launcher never served the playground")
        launcher.send_signal(signal.SIGINT)
        output, _ = launcher.communicate(timeout=10)
        assert launcher.returncode == 0, output
        assert "Stopped." in output
        with socket.socket() as probe:
            assert probe.connect_ex(("127.0.0.1", port)) != 0
    finally:
        if launcher.poll() is None:
            launcher.send_signal(signal.SIGINT)
            launcher.communicate(timeout=10)
