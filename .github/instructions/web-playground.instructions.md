---
applyTo: "web/**,samples/**,scripts/launch_web.py,scripts/make_web.py,scripts/check_web_*.py,.github/workflows/playground-ci.yml,prototype/runtime/js/**,prototype/tests/contracts/test_web_*.py,prototype/tests/contracts/test_wasm_js_*.py"
---

# Web Playground Instructions

The playground is the most direct user-facing way to run Nomi from GitHub. Keep
it honest, runnable, and aligned with `README.md`.

Use `docs/orientation/artifacts_and_usage.md`,
`docs/orientation/wasm_js_runtime_review.md`, and
`.agents/skills/nomi-web/SKILL.md` before substantial changes.

The current browser default is:

```text
source -> Rust/WASM parser -> JavaScript Core IR lowerer -> JS Core Runtime
```

Run this focused gate after meaningful web/runtime/sample changes:

```bash
python3 scripts/check_web_runtime.py
```

For UI, worker wiring, sample loading, or deployment changes, also run
`python3 scripts/check_web_browser.py`. Setup is documented in the README's
Web Playground section. CI runs both commands; browser screenshots, logs, and
traces are written to ignored `reports/web-browser/`.

If sample files or prototype runtime files change, keep the manifest and
metadata fresh:

```bash
python3 scripts/make_web.py
python3 scripts/make_web.py --check
```

If Rust parser sources change, keep committed WASM outputs and build metadata
fresh:

```bash
scripts/build_wasm.sh
scripts/build_wasm.sh --check
```

Do not move target-only examples into `samples/` until the CLI and browser path
both run them. Prefer structured diagnostics and capability metadata over
browser-only switches.
