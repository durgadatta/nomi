#!/usr/bin/env python3
"""Pinned laboratory measurements, not a supported-capacity benchmark.

Each case has an independent expected outcome. Full receipts stay in ignored
reports; counters and memory definitions identify the measured host explicitly.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import tracemalloc


ROOT = Path(__file__).resolve().parent.parent
if __package__ in {None, ""}:
    sys.path.insert(0, str(ROOT))

from prototype.runtime.report_boundary import (  # noqa: E402
    BoundaryBudget,
    decode_data,
    encode_json,
    parse_json,
)


def cases():
    result = []

    def add(name, operation, value, expected="ok", **kwargs):
        result.append(
            dict(
                name=name, operation=operation, value=value, expected=expected, **kwargs
            )
        )

    for offset in (-1, 0, 1):
        size = 262144 + offset
        add(
            f"input-{size}",
            "parse",
            '"' + "a" * (size - 2) + '"',
            "ok" if offset <= 0 else "NOMI-BOUNDARY-LIMIT",
        )
        size = 65536 + offset
        add(
            f"output-{size}",
            "encode",
            "a" * (size - 2),
            "ok" if offset <= 0 else "NOMI-BOUNDARY-LIMIT",
        )
        count = 8192 + offset
        add(
            f"nodes-{count}",
            "parse",
            "[" + ",".join(["0"] * (count - 1)) + "]",
            "ok" if offset <= 0 else "NOMI-BOUNDARY-LIMIT",
        )
        depth = 32 + offset
        add(
            f"depth-{depth}",
            "parse",
            "[" * depth + "0" + "]" * depth,
            "ok" if offset <= 0 else "NOMI-BOUNDARY-LIMIT",
        )
    for rows in (127, 128, 129):
        text = json.dumps(
            {"customers": [{"id": "a", "name": "Ada", "age": 20}] * rows},
            separators=(",", ":"),
        )
        add(
            f"rows-{rows}",
            "decode",
            text,
            "ok" if rows <= 128 else "NOMI-DECODE-CONSTRAINT",
            schema="report-batch",
        )
    for errors, last in ((63, None), (64, {"name": "a", "age": 0}), (65, {"age": 0})):
        rows = [{}] * 21 + ([] if last is None else [last])
        add(
            f"errors-{errors}",
            "decode",
            json.dumps({"customers": rows}, separators=(",", ":")),
            "NOMI-DECODE-MISSING",
            schema="report-batch",
            error_count=min(errors, 64),
            complete=errors <= 64,
        )
    for digits in (4299, 4300, 4301, 5000):
        add(
            f"integer-{digits}-digits",
            "decode",
            '{"minimum_age":' + "9" * digits + "}",
            "NOMI-NUMERIC-CAPACITY",
            python_expected="ok" if digits <= 4300 else "NOMI-NUMERIC-CAPACITY",
            schema="report-options",
        )
    for token, expected in (
        ("9007199254740991", "ok"),
        ("9007199254740992", "NOMI-NUMERIC-CAPACITY"),
    ):
        add(
            f"safe-integer-{token}",
            "decode",
            '{"minimum_age":' + token + "}",
            expected,
            python_expected="ok",
            schema="report-options",
        )
    for units in (999999, 1000000, 1000001):
        # Admission stops before allocating a tokenized copy when shared work is exhausted.
        add(
            f"shared-work-{units}",
            "parse",
            "0",
            "ok" if units <= 1000000 else "NOMI-BOUNDARY-LIMIT",
            initial_work=units - 4,
        )
    for key_size in (8000, 9000):
        add(
            f"diagnostic-key-{key_size}",
            "decode",
            json.dumps({"x" * key_size: 0}),
            "NOMI-DECODE-EXTRA" if key_size == 8000 else "NOMI-BOUNDARY-LIMIT",
            schema="report-options",
        )
    add(
        "repeated-input",
        "parse",
        "{}",
        "NOMI-BOUNDARY-LIMIT",
        limits={"aggregate_input_limit": 6},
        repeat=4,
        preceding_ok=3,
    )
    add(
        "repeated-output",
        "encode",
        "a",
        "NOMI-BOUNDARY-LIMIT",
        limits={"output_limit": 3},
        repeat=2,
        preceding_ok=1,
    )
    add("escaped-expansion", "encode", "\x00" * 10923, "NOMI-BOUNDARY-LIMIT")
    return result


def check(case, outcome, *, python=False):
    expected = (
        case.get("python_expected", case["expected"]) if python else case["expected"]
    )
    assert ("ok" if outcome["ok"] else outcome["errors"][0]["code"]) == expected, case[
        "name"
    ]
    if "error_count" in case:
        assert len(outcome["errors"]) == case["error_count"], case["name"]
        assert outcome["complete"] == case["complete"], case["name"]


JS_PROBE = r"""
function measure(library, cases) {
  return cases.map(c => {
    const budget = new library.BoundaryBudget(c.limits || {});
    budget.work = c.initial_work || 0;
    const started = performance.now();
    const before = typeof process === 'object' ? process.memoryUsage().heapUsed : null;
    let outcome;
    const preceding = [];
    for (let i = 0; i < (c.repeat || 1); i++) {
      if (c.operation === 'parse') outcome = library.parseJson(c.value, budget);
      else if (c.operation === 'encode') outcome = library.encodeJson(c.value, budget);
      else {
        const parsed = library.parseJson(c.value, budget);
        outcome = parsed.ok ? library.decodeData(parsed.value, c.schema, budget) : parsed;
      }
      preceding.push(outcome.ok);
    }
    return {name: c.name, ok: outcome.ok,
      code: outcome.ok ? null : outcome.errors[0].code,
      error_count: outcome.errors ? outcome.errors.length : 0, complete: outcome.complete,
      preceding, elapsed_ms: performance.now() - started, receipt: budget.receipt(),
      heap_delta_bytes: before === null ? null : process.memoryUsage().heapUsed - before,
      process_peak_rss_kib: before === null ? null : process.resourceUsage().maxRSS};
  });
}
"""


def verify_js(vectors, rows):
    for case, row in zip(vectors, rows, strict=True):
        assert row["name"] == case["name"]
        assert ("ok" if row["ok"] else row["code"]) == case["expected"], row
        if "error_count" in case:
            assert (
                row["error_count"] == case["error_count"]
                and row["complete"] == case["complete"]
            )
        if "preceding_ok" in case:
            assert row["preceding"] == [True] * case["preceding_ok"] + [False]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--browser",
        action="store_true",
        help="also measure the same library in a real Chromium worker",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "reports/report-boundary/measurements.json",
    )
    args = parser.parse_args()
    vectors = cases()
    rows = []
    for case in vectors:
        budget = BoundaryBudget(**case.get("limits", {}))
        budget.work = case.get("initial_work", 0)
        tracemalloc.start()
        started = time.perf_counter()
        preceding = []
        for _ in range(case.get("repeat", 1)):
            if case["operation"] == "parse":
                outcome = parse_json(case["value"], budget)
            elif case["operation"] == "encode":
                outcome = encode_json(case["value"], budget)
            else:
                parsed = parse_json(case["value"], budget)
                outcome = (
                    decode_data(parsed["value"], case["schema"], budget)
                    if parsed["ok"]
                    else parsed
                )
            preceding.append(outcome["ok"])
        elapsed = (time.perf_counter() - started) * 1000
        peak = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        check(case, outcome, python=True)
        if "preceding_ok" in case:
            assert preceding == [True] * case["preceding_ok"] + [False]
        rows.append(
            dict(
                name=case["name"],
                ok=outcome["ok"],
                code=None if outcome["ok"] else outcome["errors"][0]["code"],
                elapsed_ms=elapsed,
                traced_peak_bytes=peak,
                receipt=budget.receipt(),
            )
        )
    node = subprocess.run(
        [
            "node",
            "-e",
            JS_PROBE
            + "const l = require('./prototype/runtime/js/report_boundary.js'); const cases = JSON.parse(require('fs').readFileSync(0, 'utf8')); process.stdout.write(JSON.stringify({host:process.version, rows:measure(l, cases)}));",
        ],
        input=json.dumps(vectors),
        text=True,
        capture_output=True,
        cwd=ROOT,
        check=True,
    )
    node_result = json.loads(node.stdout)
    verify_js(vectors, node_result["rows"])
    result = {
        "environment": {
            "observed_utc": datetime.now(timezone.utc).isoformat(),
            "python": sys.version,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "node": node_result["host"],
            "source_sha256": {
                path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
                for path in (
                    "prototype/runtime/report_boundary.py",
                    "prototype/runtime/js/report_boundary.js",
                )
            },
        },
        "python": rows,
        "node": node_result["rows"],
    }
    if args.browser:
        from playwright.sync_api import sync_playwright
        from scripts.check_web_browser import playground_url

        with playground_url(None) as url, sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()
            page.goto(url + "style.css")
            library_url = url + "../prototype/runtime/js/report_boundary.js"
            program = (
                "importScripts("
                + json.dumps(library_url)
                + ");\n"
                + JS_PROBE
                + "\nonmessage = event => postMessage(measure(NomiReportBoundary, event.data));"
            )
            measured = page.evaluate(
                """({program, cases}) => new Promise((resolve, reject) => {
              const url = URL.createObjectURL(new Blob([program], {type:'text/javascript'}));
              const worker = new Worker(url);
              worker.onmessage = event => { worker.terminate(); URL.revokeObjectURL(url); resolve(event.data); };
              worker.onerror = event => { worker.terminate(); URL.revokeObjectURL(url); reject(new Error(event.message)); };
              worker.postMessage(cases);
            })""",
                {"program": program, "cases": vectors},
            )
            verify_js(vectors, measured)
            result["environment"]["chromium"] = browser.version
            result["browser_worker"] = measured
            browser.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        f"{len(vectors)} independent cases passed on {len(result) - 1} hosts; receipt: {args.output}"
    )


if __name__ == "__main__":
    main()
