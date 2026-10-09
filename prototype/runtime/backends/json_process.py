"""Transport for replaceable executables that consume and produce JSON.

This layer owns process mechanics, not Core IR or language semantics.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"Non-JSON numeric constant: {value}")


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def run_json_process(
    command: list[str],
    payload: str,
    *,
    cwd: Path,
    label: str,
    timeout: float | None = None,
    reject_duplicate_keys: bool = False,
) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            input=payload.encode("utf-8"),
            capture_output=True,
            cwd=cwd,
            check=False,
            timeout=timeout,
        )
    except UnicodeEncodeError as exc:
        raise RuntimeError(f"{label} request is not valid UTF-8") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"{label} timed out") from exc
    except OSError as exc:
        raise RuntimeError(f"{label} could not start: {exc}") from exc
    if completed.returncode != 0:
        detail = (
            completed.stderr.decode("utf-8", errors="replace").strip()
            or completed.stdout.decode("utf-8", errors="replace").strip()
        )
        raise RuntimeError(f"{label} failed" + (f": {detail}" if detail else ""))
    try:
        response_text = completed.stdout.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError(f"{label} returned invalid UTF-8") from exc
    try:
        response = json.loads(
            response_text,
            parse_constant=_reject_json_constant,
            object_pairs_hook=_unique_json_object if reject_duplicate_keys else None,
        )
    except ValueError as exc:
        raise RuntimeError(f"{label} returned invalid JSON") from exc
    if not isinstance(response, dict):
        raise RuntimeError(f"{label} response must be a JSON object")  # noqa: TRY004 - backend protocol failure
    return response
