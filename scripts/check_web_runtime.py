#!/usr/bin/env python3
"""Run the focused web/runtime artifact and contract checks."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-agent-doctor",
        action="store_true",
        help="skip .codex/scripts/agent_doctor.py",
    )
    return parser.parse_args()


def run_step(name: str, command: list[str]) -> None:
    print(f"\n== {name} ==", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    args = parse_args()
    python = sys.executable

    steps: list[tuple[str, list[str]]] = [
        (
            "web manifest freshness",
            [python, str(ROOT / "scripts" / "make_web.py"), "--check"],
        ),
        (
            "WASM parser freshness",
            [str(ROOT / "scripts" / "build_wasm.sh"), "--check"],
        ),
        (
            "browser/runtime contracts",
            [
                python,
                "-m",
                "pytest",
                "prototype/tests/contracts/test_wasm_js_core_parity_contract.py",
                "prototype/tests/contracts/test_wasm_js_pipeline_contract.py",
                "prototype/tests/contracts/test_host_capabilities_contract.py",
                "prototype/tests/unit/runtime/test_js_core_runtime_backend.py",
            ],
        ),
    ]

    agent_doctor = ROOT / ".codex" / "scripts" / "agent_doctor.py"
    if not args.skip_agent_doctor and agent_doctor.exists():
        steps.append(("agent doctor", [python, str(agent_doctor)]))

    for name, command in steps:
        run_step(name, command)

    print("\nweb/runtime checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
