#!/usr/bin/env python3
"""Verify the complete programs and exact output in the introductory guide."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs/guide/language_basics.md"
if __package__ in {None, ""}:
    sys.path.insert(0, str(ROOT))


@dataclass(frozen=True)
class Example:
    title: str
    source: str
    stdout: str


def read_examples(path: Path = GUIDE) -> list[Example]:
    examples = []
    for section in re.split(r"^## ", path.read_text(encoding="utf-8"), flags=re.M)[1:]:
        title = section.splitlines()[0]
        sources = re.findall(r"^```nomi\n(.*?)^```\s*$", section, re.M | re.S)
        outputs = re.findall(r"^```text\n(.*?)^```\s*$", section, re.M | re.S)
        if not sources and not outputs:
            continue
        if len(sources) != 1 or len(outputs) != 1:
            raise ValueError(f"{title}: expected one complete Nomi program and one output block")
        examples.append(Example(title, sources[0], outputs[0]))
    if not examples:
        raise ValueError(f"No complete examples found in {path}")
    return examples


WASM_RUN = """
const fs = require('node:fs');
const base = './prototype/runtime/js/';
const parser = require(base + 'pkg/nomi_parser.js');
parser.initSync({module: fs.readFileSync(base + 'pkg/nomi_parser_bg.wasm')});
const {lowerRustAstToCoreIr} = require(base + 'lower_to_core_ir.js');
const {CoreRuntime} = require(base + 'core_runtime.js');
const source = JSON.parse(fs.readFileSync(0, 'utf8'));
const payload = lowerRustAstToCoreIr(JSON.parse(parser.parse_nomi(source)));
if (payload.diagnosticCount) throw new Error(JSON.stringify(payload.diagnostics));
process.stdout.write(JSON.stringify(new CoreRuntime().evaluate(payload).stdout));
"""


def run_example(example: Example, route: str) -> str:
    if route == "wasm-js":
        node = shutil.which("node")
        if not node:
            raise RuntimeError("wasm-js requires Node.js; install it or select --route nomi")
        result = subprocess.run(
            [node, "-e", WASM_RUN], input=json.dumps(example.source), cwd=ROOT,
            text=True, capture_output=True, timeout=30,
        )
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or "WASM/JS execution failed")
        return json.loads(result.stdout)
    from prototype.runtime import execute

    options = {"mode": route} if route in {"nomi", "reduced"} else {"eval_backend": route}
    result = execute(source=example.source, raise_on_error=False, **options)
    if not result.ok:
        raise RuntimeError("; ".join(item.message for item in result.diagnostics))
    if result.stderr:
        raise RuntimeError(f"Unexpected stderr: {result.stderr}")
    return result.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--route", action="append", choices=("nomi", "reduced", "wasm-js", "core-runtime"),
        help="Execution route; repeatable. Default: all three documented routes.",
    )
    args = parser.parse_args()
    try:
        examples = read_examples()
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    failed = 0
    checked = 0
    for route in args.route or ["nomi", "reduced", "wasm-js"]:
        for example in examples:
            checked += 1
            try:
                actual = run_example(example, route)
                if actual != example.stdout:
                    raise ValueError(f"expected {example.stdout!r}, got {actual!r}")
                print(f"PASS {route}: {example.title}")
            except (RuntimeError, ValueError, OSError, subprocess.TimeoutExpired) as error:
                failed += 1
                print(f"FAIL {route}: {example.title}: {error}", file=sys.stderr)
    print(f"{checked - failed}/{checked} guide comparisons passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
