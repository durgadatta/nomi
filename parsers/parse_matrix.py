"""Run parser frontend acceptance fixtures and print a timing matrix.

This is not a benchmark lab. It is a quick experiment runner that exercises
every parser frontend enrolled in the shared parse-acceptance contract.
"""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from pathlib import Path

from prototype.parser.nomi.frontend import get_parse_acceptance_frontends


REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_FILES = (
    REPO_ROOT / "samples" / "block.nomi",
    REPO_ROOT / "samples" / "collections.nomi",
    REPO_ROOT / "samples" / "constraint.nomi",
    REPO_ROOT / "samples" / "demo.nomi",
    REPO_ROOT / "samples" / "demo_terse.nomi",
    REPO_ROOT / "samples" / "demo_verbose.nomi",
    REPO_ROOT / "samples" / "notebook_intro.nomi.nb",
    REPO_ROOT / "samples" / "others.nomi",
)


@dataclass(frozen=True, slots=True)
class MatrixRow:
    frontend: str
    roles: str
    fixture: str
    status: str
    milliseconds: float
    error: str = ""


def run_matrix(iterations: int = 1) -> list[MatrixRow]:
    rows: list[MatrixRow] = []
    for frontend in get_parse_acceptance_frontends():
        roles = ", ".join(frontend.spec.experiment_roles) or "-"
        for fixture in SAMPLE_FILES:
            started = time.perf_counter()
            status = "pass"
            error = ""
            try:
                for _ in range(iterations):
                    frontend.parse_accepts(filename=fixture)
            except Exception as exc:
                status = "fail"
                error = str(exc).splitlines()[0]
            elapsed = (time.perf_counter() - started) * 1000
            rows.append(
                MatrixRow(
                    frontend=frontend.spec.name,
                    roles=roles,
                    fixture=fixture.name,
                    status=status,
                    milliseconds=elapsed / max(iterations, 1),
                    error=error,
                )
            )
    return rows


def render_matrix(rows: list[MatrixRow]) -> str:
    output = [
        "| frontend | roles | fixture | status | ms | error |",
        "| --- | --- | --- | --- | ---: | --- |",
    ]
    for row in rows:
        output.append(
            "| {frontend} | {roles} | {fixture} | {status} | {ms:.3f} | {error} |".format(
                frontend=row.frontend,
                roles=row.roles,
                fixture=row.fixture,
                status=row.status,
                ms=row.milliseconds,
                error=row.error,
            )
        )
    return "\n".join(output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=1)
    args = parser.parse_args()

    rows = run_matrix(iterations=args.iterations)
    print(render_matrix(rows))
    return 1 if any(row.status != "pass" for row in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
