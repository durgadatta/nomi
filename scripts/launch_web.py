#!/usr/bin/env python3
"""Prepare and launch the Nomi web playground."""

import argparse
import errno
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PORT = 8080


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="host interface to bind")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="preferred port")
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="print the URL without opening a browser",
    )
    parser.add_argument(
        "--no-manifest",
        action="store_true",
        help="skip regenerating web/manifest.json",
    )
    parser.add_argument(
        "--strict-port",
        action="store_true",
        help="fail instead of choosing the next free port when the requested port is busy",
    )
    parser.add_argument(
        "--no-wasm",
        action="store_true",
        help="skip building the WASM parser",
    )
    return parser.parse_args()


def port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError as error:
            if error.errno not in {errno.EADDRINUSE, errno.EADDRNOTAVAIL}:
                raise
            return False
    return True


def choose_port(host: str, preferred: int, strict: bool) -> int:
    if not 1 <= preferred <= 65535:
        raise SystemExit("Port must be between 1 and 65535.")
    if port_available(host, preferred):
        return preferred
    if strict:
        raise SystemExit(f"Port {preferred} is already in use on {host}.")

    for port in range(preferred + 1, min(preferred + 50, 65536)):
        if port_available(host, port):
            print(f"Port {preferred} is busy; using {port}.")
            return port

    raise SystemExit(f"No free port found near {preferred}.")


def build_wasm() -> None:
    build_script = ROOT / "scripts" / "build_wasm.sh"
    if not build_script.exists():
        print("WASM build script not found — skipping WASM build.")
        return
    print("Building WASM parser...")
    try:
        subprocess.run(["bash", str(build_script)], check=True)
    except FileNotFoundError as exc:
        raise SystemExit(
            "Unable to run bash for the WASM build. Install bash or launch with "
            "--no-wasm to use the committed parser artifacts."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            "WASM parser build failed. Check that Rust, the "
            "wasm32-unknown-unknown target, and wasm-bindgen are installed, "
            "or launch with --no-wasm to use committed artifacts. "
            "Freshness can be checked with: scripts/build_wasm.sh --check"
        ) from exc


def regenerate_manifest() -> None:
    print("Building web manifest...")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "make_web.py")], check=True)


def wait_for_server(
    server: subprocess.Popen, host: str, port: int, *, timeout: float = 10
) -> None:
    probe_host = "127.0.0.1" if host == "0.0.0.0" else host
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        status = server.poll()
        if status is not None:
            raise SystemExit(f"Playground server exited during startup (code {status}).")
        try:
            with socket.create_connection((probe_host, port), timeout=0.2):
                return
        except OSError:
            time.sleep(0.05)
    raise SystemExit(f"Playground server did not start on {host}:{port} within {timeout}s.")


def main() -> int:
    args = parse_args()
    if not args.no_wasm:
        build_wasm()
    if not args.no_manifest:
        regenerate_manifest()

    port = choose_port(args.host, args.port, args.strict_port)
    browser_host = "127.0.0.1" if args.host == "0.0.0.0" else args.host
    url = f"http://{browser_host}:{port}/web/"
    print(f"Starting Nomi web playground at {url}")

    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", args.host],
        cwd=str(ROOT),
    )
    try:
        wait_for_server(server, args.host, port)
        if not args.no_browser:
            webbrowser.open(url)
        return server.wait()
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0
    finally:
        if server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
