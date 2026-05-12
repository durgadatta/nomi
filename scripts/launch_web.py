#!/usr/bin/env python3
"""Prepare and launch the Nomi web playground in a browser."""

import subprocess
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    print("Building manifest...")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "make_web.py")], check=True)

    print("Starting server at http://localhost:8080/web/")
    webbrowser.open("http://localhost:8080/web/")

    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8080"],
        cwd=str(ROOT),
    )
    try:
        server.wait()
    except KeyboardInterrupt:
        server.terminate()
        print("\nStopped.")


if __name__ == "__main__":
    main()
