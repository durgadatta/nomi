"""Transport for replaceable executables that consume and produce JSON.

This layer owns process mechanics, not Core IR or language semantics.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


def run_json_process(
    command: list[str],
    payload: str,
    *,
    cwd: Path,
    label: str,
    timeout: float | None = None,
) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            input=payload,
            text=True,
            capture_output=True,
            cwd=cwd,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"{label} timed out") from exc
    except OSError as exc:
        raise RuntimeError(f"{label} could not start: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"{label} failed" + (f": {detail}" if detail else ""))
    try:
        response = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{label} returned invalid JSON") from exc
    if not isinstance(response, dict):
        raise RuntimeError(f"{label} response must be a JSON object")  # noqa: TRY004 - backend protocol failure
    return response
