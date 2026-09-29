# Nomi Copilot Instructions

Use `AGENTS.md` as the main project map. Nomi is an exploratory programming
language, so current implementation behavior is evidence, not final language
authority. Target language decisions live in `docs/design/`; current runnable
pipeline truth lives in `docs/orientation/artifacts_and_usage.md`.

Before changing parser, runtime, web, tests, docs, or tooling, read the relevant
repo-local skill under `.agents/skills/`:

- `nomi-language-design` for syntax and semantic decisions.
- `nomi-parse` for grammar, AST lowering, and desugar work.
- `nomi-rust-parser` for Rust/WASM parser and browser payload contracts.
- `nomi-interp` for runtime/evaluation changes.
- `nomi-test` for test and snapshot work.
- `nomi-web` for the GitHub Pages playground, Monaco, worker/runtime, samples,
  manifests, and deployment.
- `nomi-ai-native` for agent setup, hooks, prompts, GitHub/Copilot
  instructions, and workflow repeatability.

Keep user-facing playground health visible. If a change touches `web/`,
`samples/`, `prototype/runtime/js/`, parser frontends, generated manifests, or
WASM artifacts, run or recommend:

```bash
python3 scripts/check_web_runtime.py
```

When adding or changing sample/runtime files, keep generated artifacts fresh:

```bash
python3 scripts/make_web.py --check
scripts/build_wasm.sh --check
```

For VS Code extension work, use the wrapper:

```bash
python3 tools/vscode/nomi/scripts/nomi-vscode.py test
python3 tools/vscode/nomi/scripts/nomi-vscode.py package
```

Do not advertise target-only syntax as runnable in `samples/` or the web
playground until parser, runtime, diagnostics, tests, and browser behavior all
agree. Prefer small, reversible changes driven by feature metadata, schemas,
capability tables, and inspection commands.

