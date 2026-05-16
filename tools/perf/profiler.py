"""Profile the Nomi pipeline end-to-end and emit a self-contained HTML report.

Usage::

    python3 tools/perf/profile.py [--file samples/demo.nomi] [--iterations N]

Output is written to ``reports/profile/`` (untracked).  Open the HTML file in
any browser — no external dependencies.
"""

import argparse
import ast
import cProfile
import io
import json
import os
import pstats
import sys
import time
import webbrowser
from pathlib import Path

# Ensure the repo root is on sys.path.
_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from prototype.parser.nomi.usage import (
    parse_raw_tree,
    parse_transformed_tree,
    generate_ast,
    _RAW_TREE_CACHE,
)
from prototype.grammar.assemble import assemble_grammar, get_layer_pipeline
from lark import Lark
from prototype.parser.nomi.postlexer import NomiPostLexer
from prototype.parser.nomi.ast_ import NomiToPythonAST
from prototype.syntax.surface import lower_surface_to_python
from prototype.parser.nomi.desugar import desugar_module

OUT_DIR = _REPO / "reports" / "profile"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ── profiling helpers ──────────────────────────────────────────────────

def _profile_func(func, *args, **kwargs):
    """Profile a single callable and return (elapsed_sec, pstats.Stats)."""
    profiler = cProfile.Profile()
    profiler.enable()
    t0 = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - t0
    profiler.disable()
    sio = io.StringIO()
    stats = pstats.Stats(profiler, stream=sio)
    return elapsed, stats, result


def _stats_to_records(stats, top_n=30):
    """Convert pstats.Stats to a list of dicts for JSON embedding."""
    records = []
    stats.sort_stats("cumtime")
    for func_info, (cc, nc, tt, ct, callers) in stats.stats.items():
        filename, lineno, funcname = func_info
        records.append({
            "file": filename,
            "line": lineno,
            "function": funcname,
            "ncalls": nc,
            "tottime": round(tt, 6),
            "cumtime": round(ct, 6),
            "percall_tot": round(tt / nc if nc else 0, 6),
            "percall_cum": round(ct / nc if nc else 0, 6),
        })
    records.sort(key=lambda r: -r["cumtime"])
    return records[:top_n]


# ── stage definitions ──────────────────────────────────────────────────

def profile_stages(code):
    """Profile each pipeline stage independently. Returns list of stage dicts."""
    stages = []

    # Clear caches so we measure first-parse cost.
    _RAW_TREE_CACHE.clear()

    # 1. Grammar assembly
    t0 = time.perf_counter()
    grammar = assemble_grammar()
    elapsed = time.perf_counter() - t0
    stages.append({"name": "Grammar assembly", "elapsed": elapsed, "records": []})

    # 2. Raw parse (covers lex + Earley).  Time accurately first,
    # then collect cProfile stats separately (cProfile adds ~4x overhead
    # for Earley's function-call-heavy inner loop).
    _RAW_TREE_CACHE.clear()
    t0 = time.perf_counter()
    raw_tree = parse_raw_tree(code=code)
    parse_elapsed = time.perf_counter() - t0

    _RAW_TREE_CACHE.clear()
    _parse_stats_elapsed, parse_stats, _ = _profile_func(parse_raw_tree, code=code)
    stages.append({
        "name": "Raw parse (lex + Earley)",
        "elapsed": parse_elapsed,  # accurate wall-clock time
        "records": _stats_to_records(parse_stats),
    })

    # 3. Layer transforms
    pipeline = get_layer_pipeline()
    t0 = time.perf_counter()
    transformed = pipeline.run(raw_tree)
    elapsed = time.perf_counter() - t0
    stages.append({"name": "Layer transforms", "elapsed": elapsed, "records": []})

    # 4. NomiToPythonAST
    t0 = time.perf_counter()
    surface_ast = NomiToPythonAST().transform(transformed)
    elapsed = time.perf_counter() - t0
    stages.append({"name": "NomiToPythonAST", "elapsed": elapsed, "records": []})

    # 5. Surface lowering
    t0 = time.perf_counter()
    lower_surface_to_python(surface_ast)
    elapsed = time.perf_counter() - t0
    stages.append({"name": "Surface lowering", "elapsed": elapsed, "records": []})

    # 6. Desugar — time accurately, then collect cProfile stats.
    t0 = time.perf_counter()
    desugared = desugar_module(surface_ast)
    desugar_elapsed = time.perf_counter() - t0

    elapsed_cp, stats, _ = _profile_func(desugar_module, surface_ast)
    stages.append({
        "name": "Desugar (10 passes)",
        "elapsed": desugar_elapsed,
        "records": _stats_to_records(stats),
    })

    # 7. Full end-to-end (cold cache for parse, then everything)
    _RAW_TREE_CACHE.clear()
    t0 = time.perf_counter()
    generate_ast(code=code)
    elapsed = time.perf_counter() - t0
    stages.append({"name": "Full pipeline (parse→ast→desugar)", "elapsed": elapsed, "records": []})

    # 8. Compile + exec (Python eval)
    # Note: some Nomi constructs (compose, safe navigation) produce
    # anonymous FunctionDef nodes that Python's compile() rejects.
    t0 = time.perf_counter()
    try:
        py_ast = generate_ast(code=code)
        ast.fix_missing_locations(py_ast)
        compiled = compile(py_ast, "<nomi_profile>", "exec")
        namespace = {}
        exec(compiled, namespace)
        eval_elapsed = time.perf_counter() - t0
        stages.append({"name": "Python compile + exec", "elapsed": eval_elapsed, "records": []})
    except (TypeError, ValueError) as e:
        eval_elapsed = time.perf_counter() - t0
        stages.append({"name": f"Python compile + exec (skipped: {e})", "elapsed": eval_elapsed, "records": []})

    return stages


# ── Earley item profiling ──────────────────────────────────────────────

def profile_earley_items(code):
    """Count Earley items created per grammar rule during a parse."""
    import lark.parsers.earley_common as ec

    rule_counts = {}
    original_init = ec.Item.__init__

    def counting_init(self, rule, ptr, start):
        original_init(self, rule, ptr, start)
        name = rule.origin.name
        rule_counts[name] = rule_counts.get(name, 0) + 1

    ec.Item.__init__ = counting_init

    _RAW_TREE_CACHE.clear()
    try:
        parse_raw_tree(code=code)
    finally:
        ec.Item.__init__ = original_init

    items = sorted(rule_counts.items(), key=lambda x: -x[1])
    return [{"rule": name, "items": count} for name, count in items]


# ── HTML report ────────────────────────────────────────────────────────

def _html_report(stages, earley_items, source_file, source_lines_list, total_time):
    """Render a self-contained HTML report."""
    stages_json = json.dumps(stages, indent=2)
    items_json = json.dumps(earley_items, indent=2)

    # Build source display
    source_html = ""
    for i, line in enumerate(source_lines_list, 1):
        escaped = line.rstrip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        source_html += f'<tr><td class="ln">{i}</td><td class="code">{escaped or " "}</td></tr>\n'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Nomi Pipeline Profile — {source_file}</title>
<style>
  :root {{ --bg: #1a1a2e; --card: #16213e; --accent: #e94560; --text: #eaeaea; --muted: #8a8aaa; --green: #2ecc71; --orange: #f39c12; --blue: #3498db; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
  h1 {{ font-size: 1.8rem; margin-bottom: 4px; }}
  h2 {{ font-size: 1.3rem; margin: 24px 0 12px; padding-bottom: 6px; border-bottom: 2px solid var(--accent); }}
  .meta {{ color: var(--muted); font-size: 0.85rem; margin-bottom: 24px; }}

  /* -- summary cards -- */
  .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; margin-bottom: 32px; }}
  .card {{ background: var(--card); border-radius: 8px; padding: 16px; }}
  .card .label {{ color: var(--muted); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px; }}
  .card .value {{ font-size: 2rem; font-weight: 700; margin: 4px 0; }}
  .card .pct {{ font-size: 0.85rem; color: var(--muted); }}

  /* -- stage bars -- */
  .stages {{ margin-bottom: 32px; }}
  .stage-row {{ display: flex; align-items: center; margin-bottom: 4px; gap: 10px; }}
  .stage-name {{ width: 200px; text-align: right; font-size: 0.85rem; color: var(--muted); flex-shrink: 0; }}
  .stage-bar-bg {{ flex: 1; height: 24px; background: var(--card); border-radius: 4px; overflow: hidden; position: relative; }}
  .stage-bar-fill {{ height: 100%; border-radius: 4px; transition: width 0.3s; }}
  .stage-time {{ width: 90px; font-size: 0.8rem; font-variant-numeric: tabular-nums; flex-shrink: 0; }}

  /* -- tables -- */
  table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
  th {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid #2a2a4a; color: var(--muted); font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.5px; }}
  td {{ padding: 6px 10px; border-bottom: 1px solid #1a1a30; }}
  tr:hover {{ background: rgba(255,255,255,0.03); }}
  .num {{ text-align: right; font-variant-numeric: tabular-nums; }}

  /* -- earley items chart -- */
  .earley-bar {{ display: flex; align-items: center; margin-bottom: 2px; gap: 8px; }}
  .earley-label {{ width: 180px; text-align: right; font-size: 0.78rem; color: var(--muted); flex-shrink: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
  .earley-bg {{ flex: 1; height: 16px; background: var(--card); border-radius: 3px; overflow: hidden; }}
  .earley-fill {{ height: 100%; border-radius: 3px; }}
  .earley-count {{ width: 70px; font-size: 0.75rem; text-align: right; font-variant-numeric: tabular-nums; flex-shrink: 0; }}
  .earley-pct {{ width: 45px; font-size: 0.7rem; text-align: right; color: var(--muted); flex-shrink: 0; }}

  /* -- source view -- */
  .source {{ max-height: 500px; overflow-y: auto; background: var(--card); border-radius: 8px; font-size: 0.8rem; }}
  .source table {{ font-size: 0.82rem; }}
  .source .ln {{ color: var(--muted); text-align: right; user-select: none; width: 40px; padding-right: 12px; }}
  .source .code {{ font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace; white-space: pre-wrap; }}

  /* -- colors -- */
  .c-accent {{ background: var(--accent); }}
  .c-blue {{ background: var(--blue); }}
  .c-green {{ background: var(--green); }}
  .c-orange {{ background: var(--orange); }}
  .c-0 {{ background: #e94560; }} .c-1 {{ background: #e76f51; }} .c-2 {{ background: #f4a261; }}
  .c-3 {{ background: #e9c46a; }} .c-4 {{ background: #2a9d8f; }} .c-5 {{ background: #287271; }}
  .c-6 {{ background: #264653; }} .c-7 {{ background: #8ecae6; }}

  .donut {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 6px; vertical-align: middle; }}

  .toggle {{ cursor: pointer; color: var(--blue); font-size: 0.8rem; }}
  .collapsible {{ display: none; }}
  .collapsible.open {{ display: block; }}

  @media (max-width: 768px) {{
    .stage-name {{ width: 120px; font-size: 0.75rem; }}
    .earley-label {{ width: 120px; }}
  }}
</style>
</head>
<body>
<div class="container">

<h1>Nomi Pipeline Profile</h1>
<p class="meta">
  Source: <strong>{source_file}</strong> &mdash;
  {len(source_lines_list)} lines &mdash;
  {total_time:.1f}ms total pipeline (first-parse, cold cache) &mdash;
  {time.strftime('%Y-%m-%d %H:%M:%S')}
</p>

<!-- ── Summary cards ── -->
<div class="summary" id="summary-cards"></div>

<!-- ── Stage breakdown ── -->
<h2>Stage Breakdown</h2>
<div class="stages" id="stage-bars"></div>

<!-- ── Earley item analysis ── -->
<h2>Earley Items per Grammar Rule</h2>
<p style="color:var(--muted);font-size:0.8rem;margin-bottom:8px;">
  Each Earley item is a (rule, position, origin) triple created during
  <code>predict_and_complete</code>.  More items → slower parse.
  Top rules by item count shown below.
</p>
<div id="earley-chart"></div>

<!-- ── Per-stage detail tables ── -->
<h2>Stage Details (cProfile)</h2>
<div id="stage-tables"></div>

<!-- ── Source ── -->
<h2>Source: {source_file}</h2>
<div class="source"><table>{source_html}</table></div>

</div>

<script>
const stages = {stages_json};
const earleyItems = {items_json};
const totalTime = stages.reduce((s, st) => s + st.elapsed, 0) * 1000;

// ---- summary cards ----
(function() {{
  const longest = stages.reduce((a,b) => a.elapsed > b.elapsed ? a : b);
  const totalMs = totalTime;
  let html = '';
  html += '<div class="card"><div class="label">Total Pipeline</div><div class="value">' + totalMs.toFixed(1) + 'ms</div></div>';
  html += '<div class="card"><div class="label">Bottleneck</div><div class="value">' + longest.name + '</div><div class="pct">' + (longest.elapsed * 1000).toFixed(1) + 'ms — ' + (longest.elapsed / (totalMs/1000) * 100).toFixed(1) + '%</div></div>';
  html += '<div class="card"><div class="label">Total Earley Items</div><div class="value">' + earleyItems.reduce((s,i) => s + i.items, 0).toLocaleString() + '</div><div class="pct">Top rule: ' + (earleyItems[0] ? earleyItems[0].rule : '—') + '</div></div>';
  html += '<div class="card"><div class="label">Source</div><div class="value" style="font-size:1.2rem;">' + {len(source_lines_list)} + ' lines</div></div>';
  document.getElementById('summary-cards').innerHTML = html;
}})();

// ---- stage bars ----
(function() {{
  const colors = ['c-0','c-1','c-2','c-3','c-4','c-5','c-6','c-7'];
  const maxMs = Math.max(...stages.map(s => s.elapsed)) * 1000;
  let html = '';
  stages.forEach((st, i) => {{
    const ms = st.elapsed * 1000;
    const pct = maxMs > 0 ? (ms / maxMs * 100) : 0;
    const pctOfTotal = totalTime > 0 ? (ms / totalTime * 100) : 0;
    html += '<div class="stage-row">';
    html += '<span class="stage-name" title="' + st.name + '">' + st.name + '</span>';
    html += '<span class="stage-bar-bg"><span class="stage-bar-fill ' + colors[i % colors.length] + '" style="width:' + pct + '%"></span></span>';
    html += '<span class="stage-time">' + ms.toFixed(1) + 'ms <small>(' + pctOfTotal.toFixed(1) + '%)</small></span>';
    html += '</div>';
  }});
  document.getElementById('stage-bars').innerHTML = html;
}})();

// ---- earley items ----
(function() {{
  const maxItems = earleyItems.length > 0 ? earleyItems[0].items : 1;
  const totalItems = earleyItems.reduce((s,i) => s + i.items, 0);
  const colors = ['c-0','c-1','c-2','c-3','c-4','c-5','c-6','c-7'];
  let html = '';
  earleyItems.slice(0, 30).forEach((ei, i) => {{
    const pct = ei.items / maxItems * 100;
    const pctTotal = totalItems > 0 ? (ei.items / totalItems * 100) : 0;
    html += '<div class="earley-bar">';
    html += '<span class="earley-label" title="' + ei.rule + '">' + ei.rule + '</span>';
    html += '<span class="earley-bg"><span class="earley-fill ' + colors[i % colors.length] + '" style="width:' + pct + '%"></span></span>';
    html += '<span class="earley-count">' + ei.items.toLocaleString() + '</span>';
    html += '<span class="earley-pct">' + pctTotal.toFixed(1) + '%</span>';
    html += '</div>';
  }});
  if (earleyItems.length > 30) {{
    html += '<p style="color:var(--muted);font-size:0.78rem;margin-top:4px;">... and ' + (earleyItems.length - 30) + ' more rules</p>';
  }}
  document.getElementById('earley-chart').innerHTML = html;
}})();

// ---- stage detail tables ----
(function() {{
  let html = '';
  stages.forEach((st, si) => {{
    if (!st.records || st.records.length === 0) return;
    const id = 'detail-' + si;
    html += '<h3 style="cursor:pointer;color:var(--blue);margin-top:16px;" onclick="var e=document.getElementById(\\'' + id + '\\');e.classList.toggle(\\'open\\')">';
    html += '▸ ' + st.name + ' <span style="color:var(--muted);font-weight:normal;font-size:0.8rem;">(' + (st.elapsed * 1000).toFixed(1) + 'ms, ' + st.records.length + ' functions)</span>';
    html += '</h3>';
    html += '<div class="collapsible" id="' + id + '">';
    html += '<table><thead><tr><th>Function</th><th class="num">Calls</th><th class="num">Total</th><th class="num">Cumulative</th><th class="num">Per Call</th></tr></thead><tbody>';
    st.records.forEach(r => {{
      const shortName = r.function.length > 60 ? r.function.substring(0, 57) + '...' : r.function;
      const shortFile = r.file.length > 40 ? '...' + r.file.substring(r.file.length - 37) : r.file;
      html += '<tr>';
      html += '<td title="' + r.file + ':' + r.line + '">' + shortName + '<br><small style="color:var(--muted)">' + shortFile + ':' + r.line + '</small></td>';
      html += '<td class="num">' + r.ncalls.toLocaleString() + '</td>';
      html += '<td class="num">' + (r.tottime * 1000).toFixed(2) + 'ms</td>';
      html += '<td class="num"><strong>' + (r.cumtime * 1000).toFixed(2) + 'ms</strong></td>';
      html += '<td class="num">' + (r.percall_cum * 1000).toFixed(3) + 'ms</td>';
      html += '</tr>';
    }});
    html += '</tbody></table></div>';
  }});
  document.getElementById('stage-tables').innerHTML = html;
}})();
</script>
</body>
</html>"""


# ── main ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Profile the Nomi pipeline")
    parser.add_argument("--file", default="samples/demo.nomi", help="Source file to profile")
    parser.add_argument("--iterations", type=int, default=1, help="Number of iterations (best time reported)")
    parser.add_argument("--open", action="store_true", default=True, help="Open report in browser (default)")
    parser.add_argument("--no-open", dest="open", action="store_false", help="Don't open browser")
    args = parser.parse_args()

    source_path = _REPO / args.file
    if not source_path.exists():
        print(f"Error: file not found: {source_path}")
        sys.exit(1)

    code = source_path.read_text(encoding="utf-8")
    source_lines = len(code.splitlines())

    print(f"Profiling: {args.file} ({source_lines} lines)")

    # Profile pipeline stages (best of N iterations).
    all_runs = []
    for i in range(args.iterations):
        if args.iterations > 1:
            print(f"  iteration {i + 1}/{args.iterations}...")
        stages = profile_stages(code)
        total = sum(s["elapsed"] for s in stages)
        all_runs.append((total, stages))

    if args.iterations > 1:
        # Use the run with minimum parse stage time (the bottleneck).
        all_runs.sort(key=lambda r: r[1][1]["elapsed"])  # sort by raw parse stage
        total_time, stages = all_runs[0]
    else:
        total_time, stages = all_runs[0]

    # Profile Earley items separately.
    print("  counting Earley items...")
    earley_items = profile_earley_items(code)

    total_items = sum(ei["items"] for ei in earley_items)
    print(f"  total Earley items: {total_items:,}")
    print(f"  total pipeline: {total_time * 1000:.1f}ms")

    # Render HTML.
    source_name = source_path.name
    source_lines_list = code.splitlines()
    html = _html_report(stages, earley_items, source_name, source_lines_list, total_time * 1000)

    out_path = OUT_DIR / f"profile_{source_path.stem}.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"\nReport written to: {out_path}")

    if args.open:
        webbrowser.open(f"file://{out_path}")


if __name__ == "__main__":
    main()
