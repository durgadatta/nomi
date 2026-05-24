"""Benchmark parser frontends on time and space for a given Nomi source file.

Usage::

    python3 tools/perf/bench_parsers.py [--file samples/demo.nomi] [--iterations N]

Runs each parser frontend through two benches:

1. **Parse acceptance** — raw parse timing for every frontend that can parse
   the current grammar (``parse_accepts`` contract).
2. **Full pipeline** — parse + lower + eval via ``RuntimeSession``, available
   only for frontends with ``lower_to_python_ast=True``.

Output is a comparison table on stdout and a JSON report in ``reports/bench/``.
"""

from __future__ import annotations

import argparse
import json
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
import tracemalloc
import webbrowser
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from prototype.parser.nomi.frontend import (
    get_parser_frontend,
    _RAW_TREE_CACHE,
)
from prototype.runtime.session import RuntimeSession

OUT_DIR = _REPO / "reports" / "bench"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Frontends to benchmark, in display order.
BENCH_FRONTENDS = [
    "lark-lalr",
    "rust-fast-ast",
    "pest-readable-cst",
    "tree-sitter-cst",
]

# Crate metadata for Rust subprocess RSS measurement.
_RUST_CRATES = {
    "rust-fast-ast": {
        "crate_dir": _REPO / "prototype" / "parser" / "backends" / "rust_fast_ast",
        "command": "ast-json",
        "binary_name": "nomi-rust-fast-ast",
    },
    "pest-readable-cst": {
        "crate_dir": _REPO / "prototype" / "parser" / "backends" / "pest_readable_cst",
        "command": "cst-json",
        "binary_name": "nomi-pest-readable-cst",
    },
}


# ── helpers ───────────────────────────────────────────────────────────────

def _summarize(samples: list[float]) -> dict:
    ordered = sorted(samples)
    n = len(ordered)
    return {
        "n": n,
        "min": round(ordered[0], 3),
        "median": round(statistics.median(ordered), 3),
        "avg": round(sum(ordered) / n, 3),
        "max": round(ordered[-1], 3),
    }


def _frontend_has(frontend_name: str, capability: str) -> bool:
    """Check a boolean capability on a frontend's spec."""
    frontend = get_parser_frontend(frontend_name)
    return getattr(frontend.spec.capabilities, capability, False)


# ── parse acceptance bench ────────────────────────────────────────────────

def bench_parse_accepts(
    frontend_name: str,
    code: str,
    iterations: int,
) -> dict:
    """Time parse_accepts for *frontend_name* across *iterations* runs."""
    frontend = get_parser_frontend(frontend_name)

    # Warm-up (also triggers cargo build for Rust frontends).
    frontend.parse_accepts(code=code)

    samples_ms = []
    mem_kb = []

    for _ in range(iterations):
        # Clear Lark's raw-tree cache so we measure actual parse time,
        # not a cache-hit lookup.  Rust subprocess frontends ignore this.
        _RAW_TREE_CACHE.clear()
        tracemalloc.start()
        t0 = time.perf_counter()
        frontend.parse_accepts(code=code)
        elapsed = (time.perf_counter() - t0) * 1000
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        samples_ms.append(elapsed)
        mem_kb.append(peak / 1024)

    return {
        "parse_ms": _summarize(samples_ms),
        "peak_memory_kb": _summarize(mem_kb),
    }


# ── full pipeline bench ───────────────────────────────────────────────────

def bench_full_pipeline(
    frontend_name: str,
    source_path: Path,
    iterations: int,
) -> dict | None:
    """Time the full parse + lower + eval pipeline via RuntimeSession.

    Returns None for frontends without lower_to_python_ast.
    """
    if not _frontend_has(frontend_name, "lower_to_python_ast"):
        return None

    samples = {"parse_ms": [], "eval_ms": [], "total_ms": [], "mem_kb": []}

    # Warm-up.
    session = RuntimeSession(parser_frontend=frontend_name)
    session.run(filename=source_path, capture_output=True)

    for _ in range(iterations):
        session = RuntimeSession(parser_frontend=frontend_name)
        tracemalloc.start()
        result = session.run(filename=source_path, capture_output=True)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        t = result.timings
        samples["parse_ms"].append(t.get("parse", 0) * 1000)
        samples["eval_ms"].append(t.get("eval", 0) * 1000)
        samples["total_ms"].append(t.get("total", 0) * 1000)
        samples["mem_kb"].append(peak / 1024)

    return {
        "parse_ms": _summarize(samples["parse_ms"]),
        "eval_ms": _summarize(samples["eval_ms"]),
        "total_ms": _summarize(samples["total_ms"]),
        "peak_memory_kb": _summarize(samples["mem_kb"]),
    }


# ── subprocess RSS ────────────────────────────────────────────────────────

def _find_binary(crate_dir: Path, binary_name: str) -> Path | None:
    """Find a compiled Rust binary, trying release then debug."""
    for profile in ("release", "debug"):
        candidate = crate_dir / "target" / profile / binary_name
        if candidate.exists():
            return candidate
    return None


def bench_subprocess_rss(
    frontend_name: str,
    source_path: Path,
    iterations: int,
) -> dict | None:
    """Measure peak RSS of a Rust parser subprocess via /usr/bin/time -l.

    Finds the compiled binary so we measure the parser, not cargo overhead.
    Returns None for non-Rust frontends or if the binary can't be found.
    """
    info = _RUST_CRATES.get(frontend_name)
    if info is None:
        return None

    crate_dir = info["crate_dir"]
    command = info["command"]
    binary_name = info["binary_name"]

    # Ensure the binary is built (warm-up already did this, but be safe).
    cargo = shutil.which("cargo")
    if cargo is None:
        return None

    target_dir = (
        Path(tempfile.gettempdir())
        / f"nomi-{binary_name}-target"
        / "bench-rss"
    )

    # Build in release for accurate RSS measurement.
    subprocess.run(
        [
            cargo, "build", "--release", "--quiet",
            "--manifest-path", str(crate_dir / "Cargo.toml"),
            "--target-dir", str(target_dir),
        ],
        cwd=crate_dir, text=True, capture_output=True,
    )

    binary = _find_binary(target_dir, binary_name)
    if binary is None:
        # Fall back to cargo run.
        return None

    source_path = source_path.resolve()
    time_bin = shutil.which("time") or "/usr/bin/time"

    rss_kb = []
    for _ in range(iterations):
        result = subprocess.run(
            [time_bin, "-l", str(binary), command, str(source_path)],
            cwd=crate_dir, text=True, capture_output=True,
        )
        # /usr/bin/time -l (BSD/macOS) writes resource usage to stderr.
        for line in result.stderr.splitlines():
            line = line.strip()
            if "maximum resident set size" in line:
                rss_bytes = int(line.split()[0])
                rss_kb.append(rss_bytes / 1024)
                break

    if not rss_kb:
        return None
    return _summarize(rss_kb)


# ── report rendering ──────────────────────────────────────────────────────

def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    """Render a markdown table."""
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def _fmt_ms(stats: dict | None) -> str:
    """Format a _summarize dict as ``median (min–max)`` in ms."""
    if stats is None:
        return "—"
    return f"{stats['median']:.2f} ({stats['min']:.2f}–{stats['max']:.2f})"


def _fmt_mem(stats: dict | None) -> str:
    """Format a _summarize dict as ``median KB``."""
    if stats is None:
        return "—"
    return f"{stats['median']:.0f}"


def render_markdown(
    source_name: str,
    source_lines: int,
    iterations: int,
    parse_results: dict,
    pipeline_results: dict,
    rss_results: dict,
) -> str:
    """Render the benchmark report as markdown for terminal output."""
    lines = [
        f"# Parser Frontend Benchmark — {source_name}",
        "",
        f"**{source_lines} lines, {iterations} iterations per frontend**  "
        f"Generated {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Parse Acceptance (raw parse timing)",
        "",
        _md_table(
            ["frontend", "parse median", "parse min–max", "Python mem (KB)", "subprocess RSS (KB)"],
            [
                [
                    name,
                    _fmt_ms(parse_results[name]["parse_ms"]),
                    f"{parse_results[name]['parse_ms']['min']:.2f} – {parse_results[name]['parse_ms']['max']:.2f}",
                    _fmt_mem(parse_results[name]["peak_memory_kb"]),
                    _fmt_mem(rss_results.get(name)),
                ]
                for name in BENCH_FRONTENDS
                if name in parse_results
            ],
        ),
        "",
        "## Full Pipeline (parse + lower + eval via RuntimeSession)",
        "",
    ]

    piped = [(n, r) for n, r in pipeline_results.items() if r is not None]
    if piped:
        lines.append(
            _md_table(
                ["frontend", "parse", "eval", "total"],
                [
                    [
                        name,
                        _fmt_ms(result["parse_ms"]),
                        _fmt_ms(result["eval_ms"]),
                        _fmt_ms(result["total_ms"]),
                    ]
                    for name, result in piped
                ],
            )
        )
    else:
        lines.append("_(no frontends support full pipeline yet)_")

    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- **Parse acceptance**: wall-clock time for `parse_accepts()`. "
                 "For Lark this is in-process LALR; for Rust frontends it "
                 "includes subprocess overhead.")
    lines.append("- **Full pipeline**: parse → AST lowering → interpreter eval "
                 "via `RuntimeSession`. Only available for frontends with "
                 "`lower_to_python_ast=True`.")
    lines.append("- **Python mem**: peak Python heap via `tracemalloc` during "
                 "parse_accepts. For subprocess frontends this reflects the "
                 "Python wrapper, not the Rust parser process.")
    lines.append("- **Subprocess RSS**: peak resident set size of the parser "
                 "binary (release build) via `/usr/bin/time -l`. Rust frontends "
                 "only.")
    lines.append("")

    return "\n".join(lines)


def render_html(
    source_name: str,
    source_lines: int,
    iterations: int,
    parse_results: dict,
    pipeline_results: dict,
    rss_results: dict,
    source_lines_list: list[str],
) -> str:
    """Render a self-contained HTML visualization of the benchmark."""
    parse_json = json.dumps(
        {k: v for k, v in parse_results.items()}, indent=2
    )
    pipeline_json = json.dumps(
        {k: v for k, v in pipeline_results.items() if v is not None}, indent=2
    )
    source_html = ""
    for i, line in enumerate(source_lines_list, 1):
        escaped = line.rstrip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        source_html += f'<tr><td class="ln">{i}</td><td class="code">{escaped or " "}</td></tr>\n'

    # Build frontend labels and parse bar data for JS.
    frontend_names = [n for n in BENCH_FRONTENDS if n in parse_results]
    frontend_labels_json = json.dumps(frontend_names)
    bar_colors = ["#e94560", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Parser Frontend Benchmark — {source_name}</title>
<style>
  :root {{ --bg: #1a1a2e; --card: #16213e; --accent: #e94560; --text: #eaeaea; --muted: #8a8aaa; --green: #2ecc71; --orange: #f39c12; --blue: #3498db; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
  h1 {{ font-size: 1.8rem; margin-bottom: 4px; }}
  h2 {{ font-size: 1.3rem; margin: 24px 0 12px; padding-bottom: 6px; border-bottom: 2px solid var(--accent); }}
  .meta {{ color: var(--muted); font-size: 0.85rem; margin-bottom: 24px; }}

  .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 32px; }}
  .card {{ background: var(--card); border-radius: 8px; padding: 16px; }}
  .card .label {{ color: var(--muted); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px; }}
  .card .value {{ font-size: 2rem; font-weight: 700; margin: 4px 0; }}
  .card .detail {{ font-size: 0.85rem; color: var(--muted); }}

  .bar-chart {{ margin-bottom: 28px; }}
  .bar-row {{ display: flex; align-items: center; margin-bottom: 6px; gap: 10px; }}
  .bar-label {{ width: 170px; text-align: right; font-size: 0.85rem; color: var(--muted); flex-shrink: 0; }}
  .bar-track {{ flex: 1; height: 28px; background: var(--card); border-radius: 4px; overflow: hidden; position: relative; }}
  .bar-fill {{ height: 100%; border-radius: 4px; display: flex; align-items: center; padding-left: 8px; font-size: 0.75rem; font-weight: 600; transition: width 0.4s; }}
  .bar-value {{ width: 110px; font-size: 0.8rem; font-variant-numeric: tabular-nums; flex-shrink: 0; }}

  .pipeline-bar {{ display: flex; align-items: center; margin-bottom: 6px; gap: 10px; }}
  .pipeline-label {{ width: 170px; text-align: right; font-size: 0.85rem; color: var(--muted); flex-shrink: 0; }}
  .pipeline-track {{ flex: 1; height: 28px; background: var(--card); border-radius: 4px; overflow: hidden; display: flex; }}
  .pipeline-parse {{ height: 100%; display: flex; align-items: center; padding-left: 8px; font-size: 0.75rem; font-weight: 600; }}
  .pipeline-eval {{ height: 100%; display: flex; align-items: center; padding-left: 8px; font-size: 0.75rem; }}
  .pipeline-value {{ width: 110px; font-size: 0.8rem; font-variant-numeric: tabular-nums; flex-shrink: 0; }}

  .sparkline {{ display: flex; align-items: flex-end; gap: 2px; height: 24px; }}
  .sparkline-bar {{ width: 6px; min-height: 2px; border-radius: 1px 1px 0 0; }}

  table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
  th {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid #2a2a4a; color: var(--muted); font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.5px; }}
  td {{ padding: 6px 10px; border-bottom: 1px solid #1a1a30; }}
  tr:hover {{ background: rgba(255,255,255,0.03); }}
  .num {{ text-align: right; font-variant-numeric: tabular-nums; }}

  .source {{ max-height: 400px; overflow-y: auto; background: var(--card); border-radius: 8px; font-size: 0.8rem; }}
  .source .ln {{ color: var(--muted); text-align: right; user-select: none; width: 40px; padding-right: 12px; }}
  .source .code {{ font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace; white-space: pre-wrap; }}

  .legend {{ display: flex; gap: 16px; margin-bottom: 8px; font-size: 0.78rem; color: var(--muted); }}
  .legend-dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 4px; vertical-align: middle; }}

  .note {{ color: var(--muted); font-size: 0.78rem; margin-top: 6px; }}

  @media (max-width: 768px) {{
    .bar-label, .pipeline-label {{ width: 100px; font-size: 0.75rem; }}
    .bar-value, .pipeline-value {{ width: 80px; font-size: 0.7rem; }}
  }}
</style>
</head>
<body>
<div class="container">

<h1>Parser Frontend Benchmark</h1>
<p class="meta">
  Source: <strong>{source_name}</strong> &mdash;
  {source_lines} lines &mdash;
  {iterations} iterations per frontend &mdash;
  {time.strftime('%Y-%m-%d %H:%M:%S')}
</p>

<div class="summary" id="summary"></div>

<h2>Parse Acceptance <span style="font-weight:normal;font-size:0.8rem;color:var(--muted);">raw parse timing</span></h2>
<div class="legend">
  <span><span class="legend-dot" style="background:var(--accent)"></span> median</span>
  <span><span class="legend-dot" style="background:rgba(233,69,96,0.3)"></span> min–max range</span>
</div>
<div class="bar-chart" id="parse-bars"></div>

<h2>Full Pipeline <span style="font-weight:normal;font-size:0.8rem;color:var(--muted);">parse + eval via RuntimeSession</span></h2>
<div class="legend">
  <span><span class="legend-dot" style="background:var(--orange)"></span> parse</span>
  <span><span class="legend-dot" style="background:var(--blue)"></span> eval</span>
</div>
<div class="bar-chart" id="pipeline-bars"></div>

<h2>Detail Tables</h2>
<div id="detail-tables"></div>

<h2>Source: {source_name}</h2>
<div class="source"><table>{source_html}</table></div>

</div>

<script>
const parseResults = {parse_json};
const pipelineResults = {pipeline_json};
const frontendNames = {frontend_labels_json};
const barColors = {json.dumps(bar_colors)};

// ---- summary cards ----
(function() {{
  const parses = Object.entries(parseResults);
  if (!parses.length) return;
  const fastest = parses.reduce((a,b) => a[1].parse_ms.median < b[1].parse_ms.median ? a : b);
  const slowest = parses.reduce((a,b) => a[1].parse_ms.median > b[1].parse_ms.median ? a : b);
  const spread = slowest[1].parse_ms.median - fastest[1].parse_ms.median;

  const piped = Object.entries(pipelineResults);
  let pipeHTML = '';
  if (piped.length) {{
    const bestPipe = piped.reduce((a,b) => a[1].total_ms.median < b[1].total_ms.median ? a : b);
    pipeHTML = '<div class="card"><div class="label">Fastest Full Pipeline</div><div class="value">' + bestPipe[1].total_ms.median.toFixed(1) + 'ms</div><div class="detail">' + bestPipe[0] + '</div></div>';
  }}

  document.getElementById('summary').innerHTML =
    '<div class="card"><div class="label">Fastest Parse</div><div class="value">' + fastest[1].parse_ms.median.toFixed(1) + 'ms</div><div class="detail">' + fastest[0] + '</div></div>' +
    '<div class="card"><div class="label">Slowest Parse</div><div class="value">' + slowest[1].parse_ms.median.toFixed(1) + 'ms</div><div class="detail">' + slowest[0] + ' &mdash; ' + spread.toFixed(0) + 'ms spread</div></div>' +
    '<div class="card"><div class="label">Source</div><div class="value" style="font-size:1.2rem;">' + {source_lines} + ' lines</div><div class="detail">' + {iterations} + ' iterations</div></div>' +
    pipeHTML;
}})();

// ---- parse acceptance bars ----
(function() {{
  const maxMedian = Math.max(...frontendNames.map(n => parseResults[n].parse_ms.median));
  let html = '';
  frontendNames.forEach((name, i) => {{
    const r = parseResults[name];
    const pct = maxMedian > 0 ? (r.parse_ms.median / maxMedian * 100) : 0;
    const rangeMin = (r.parse_ms.min / maxMedian * 100) || 0;
    const rangeMax = (r.parse_ms.max / maxMedian * 100) || 0;
    html += '<div class="bar-row">';
    html += '<span class="bar-label">' + name + '</span>';
    html += '<span class="bar-track">';
    html += '<span class="bar-fill" style="width:' + pct + '%;background:' + barColors[i % barColors.length] + '">' + r.parse_ms.median.toFixed(1) + 'ms</span>';
    html += '<span style="position:absolute;left:' + rangeMin + '%;width:' + (rangeMax - rangeMin) + '%;background:rgba(233,69,96,0.15);border-radius:4px;top:0;height:100%;pointer-events:none;"></span>';
    html += '</span>';
    html += '<span class="bar-value">med ' + r.parse_ms.median.toFixed(1) + 'ms</span>';
    html += '</div>';
  }});
  document.getElementById('parse-bars').innerHTML = html;
}})();

// ---- full pipeline bars ----
(function() {{
  const piped = Object.entries(pipelineResults);
  if (!piped.length) {{
    document.getElementById('pipeline-bars').innerHTML = '<p class="note">No frontends support full pipeline yet.</p>';
    return;
  }}
  const maxTotal = Math.max(...piped.map(([,r]) => r.total_ms.median));
  let html = '';
  piped.forEach(([name, r], i) => {{
    const parsePct = maxTotal > 0 ? (r.parse_ms.median / maxTotal * 100) : 0;
    const evalPct = maxTotal > 0 ? (r.eval_ms.median / maxTotal * 100) : 0;
    html += '<div class="pipeline-bar">';
    html += '<span class="pipeline-label">' + name + '</span>';
    html += '<span class="pipeline-track">';
    html += '<span class="pipeline-parse" style="width:' + parsePct + '%;background:var(--orange)">' + r.parse_ms.median.toFixed(1) + '</span>';
    html += '<span class="pipeline-eval" style="width:' + evalPct + '%;background:var(--blue)">' + r.eval_ms.median.toFixed(1) + '</span>';
    html += '</span>';
    html += '<span class="pipeline-value">' + r.total_ms.median.toFixed(1) + 'ms total</span>';
    html += '</div>';
  }});
  document.getElementById('pipeline-bars').innerHTML = html;
}})();

// ---- detail tables ----
(function() {{
  let html = '';
  html += '<h3 style="margin-top:0;">Parse Acceptance</h3>';
  html += '<table><thead><tr><th>Frontend</th><th class="num">Min</th><th class="num">Median</th><th class="num">Avg</th><th class="num">Max</th><th class="num">Samples</th></tr></thead><tbody>';
  frontendNames.forEach(name => {{
    const r = parseResults[name].parse_ms;
    html += '<tr>';
    html += '<td>' + name + '</td>';
    html += '<td class="num">' + r.min.toFixed(2) + 'ms</td>';
    html += '<td class="num"><strong>' + r.median.toFixed(2) + 'ms</strong></td>';
    html += '<td class="num">' + r.avg.toFixed(2) + 'ms</td>';
    html += '<td class="num">' + r.max.toFixed(2) + 'ms</td>';
    html += '<td class="num">' + r.n + '</td>';
    html += '</tr>';
  }});
  html += '</tbody></table>';

  const piped = Object.entries(pipelineResults);
  if (piped.length) {{
    html += '<h3>Full Pipeline</h3>';
    html += '<table><thead><tr><th>Frontend</th><th class="num">Parse</th><th class="num">Eval</th><th class="num">Total</th><th class="num">Samples</th></tr></thead><tbody>';
    piped.forEach(([name, r]) => {{
      html += '<tr>';
      html += '<td>' + name + '</td>';
      html += '<td class="num">' + r.parse_ms.median.toFixed(2) + 'ms</td>';
      html += '<td class="num">' + r.eval_ms.median.toFixed(2) + 'ms</td>';
      html += '<td class="num"><strong>' + r.total_ms.median.toFixed(2) + 'ms</strong></td>';
      html += '<td class="num">' + r.total_ms.n + '</td>';
      html += '</tr>';
    }});
    html += '</tbody></table>';
  }}
  document.getElementById('detail-tables').innerHTML = html;
}})();
</script>
</body>
</html>"""


# ── main ──────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark Nomi parser frontends on time and space"
    )
    parser.add_argument(
        "--file", default="samples/comprehensive.nomi",
        help="Source file to benchmark (default: samples/comprehensive.nomi)",
    )
    parser.add_argument(
        "--iterations", type=int, default=20,
        help="Number of timing samples per frontend (default: 20)",
    )
    parser.add_argument(
        "--rss", action="store_true",
        help="Measure subprocess peak RSS via /usr/bin/time -l (slower)",
    )
    parser.add_argument(
        "--open", action="store_true", default=False,
        help="Open HTML report in browser",
    )
    parser.add_argument(
        "--no-open", dest="open", action="store_false",
        help="Don't open browser",
    )
    args = parser.parse_args()

    if args.iterations < 1:
        parser.error("--iterations must be at least 1")

    source_path = _REPO / args.file
    if not source_path.exists():
        print(f"Error: file not found: {source_path}", file=sys.stderr)
        return 1

    code = source_path.read_text(encoding="utf-8")
    source_lines = len(code.splitlines())

    # Determine which frontends are available (registered in _FRONTENDS).
    # This includes frontends that haven't yet cleared the
    # parse_current_grammar gate (e.g. pest-readable-cst).
    active = []
    for name in BENCH_FRONTENDS:
        try:
            get_parser_frontend(name)
        except ValueError:
            continue
        active.append(name)

    print(
        f"Benchmarking {len(active)} frontend(s) on "
        f"{args.file} ({source_lines} lines, {args.iterations} iterations):"
    )
    for name in active:
        caps = get_parser_frontend(name).spec.capabilities
        flags = []
        if caps.parse_current_grammar:
            flags.append("parse")
        if caps.lower_to_python_ast:
            flags.append("ast")
        if caps.selectable_for_session_execution or caps.selectable_for_execution:
            flags.append("exec")
        print(f"  {name}: {', '.join(flags)}")
    print()

    # ── Parse acceptance bench ────────────────────────────────────────
    print("Parse acceptance", end="", flush=True)
    parse_results = {}
    for name in active:
        print(f"  {name}...", end="", flush=True)
        parse_results[name] = bench_parse_accepts(name, code, args.iterations)
        print(f" {parse_results[name]['parse_ms']['median']:.1f}ms median", flush=True)

    # ── Subprocess RSS ────────────────────────────────────────────────
    rss_results = {}
    if args.rss:
        print("Subprocess RSS", end="", flush=True)
        for name in active:
            if name in _RUST_CRATES:
                print(f"  {name}...", end="", flush=True)
                rss = bench_subprocess_rss(name, source_path, args.iterations)
                if rss:
                    rss_results[name] = rss
                    print(f" {rss['median']:.0f} KB median", flush=True)
                else:
                    print(" skipped (binary not found)", flush=True)

    # ── Full pipeline bench ───────────────────────────────────────────
    print("Full pipeline", end="", flush=True)
    pipeline_results = {}
    for name in active:
        if _frontend_has(name, "lower_to_python_ast"):
            print(f"  {name}...", end="", flush=True)
            pipeline_results[name] = bench_full_pipeline(
                name, source_path, args.iterations,
            )
            t = pipeline_results[name]["total_ms"]["median"]
            print(f" {t:.1f}ms total median", flush=True)
        else:
            pipeline_results[name] = None

    # ── Render markdown to stdout ─────────────────────────────────────
    md = render_markdown(
        source_path.name, source_lines, args.iterations,
        parse_results, pipeline_results, rss_results,
    )
    print()
    print(md)

    # ── Write JSON ────────────────────────────────────────────────────
    json_path = OUT_DIR / f"bench_{source_path.stem}.json"
    json_payload = {
        "source": str(source_path),
        "source_lines": source_lines,
        "iterations": args.iterations,
        "parse_acceptance": parse_results,
        "full_pipeline": {
            k: v for k, v in pipeline_results.items() if v is not None
        },
        "subprocess_rss": rss_results,
    }
    json_path.write_text(json.dumps(json_payload, indent=2), encoding="utf-8")
    print(f"JSON report: {json_path}")

    # ── Write HTML ────────────────────────────────────────────────────
    source_lines_list = code.splitlines()
    html = render_html(
        source_path.name, source_lines, args.iterations,
        parse_results, pipeline_results, rss_results, source_lines_list,
    )
    html_path = OUT_DIR / f"bench_{source_path.stem}.html"
    html_path.write_text(html, encoding="utf-8")
    print(f"HTML report: {html_path}")

    if args.open:
        webbrowser.open(f"file://{html_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
