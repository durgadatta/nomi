#!/usr/bin/env python3
"""Prepare and launch the Nomi web playground."""

import argparse
import errno
import socket
import subprocess
import sys
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
    if port_available(host, preferred):
        return preferred
    if strict:
        raise SystemExit(f"Port {preferred} is already in use on {host}.")

    for port in range(preferred + 1, preferred + 50):
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


def main() -> int:
    args = parse_args()
    if not args.no_wasm:
        build_wasm()
    if not args.no_manifest:
        regenerate_manifest()

    port = choose_port(args.host, args.port, args.strict_port)
    url = f"http://{args.host}:{port}/web/"
    print(f"Starting Nomi web playground at {url}")

    if not args.no_browser:
        webbrowser.open(url)

    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", args.host],
        cwd=str(ROOT),
    )
    try:
        return server.wait()
    except KeyboardInterrupt:
        server.terminate()
        print("\nStopped.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
