Artifacts and Usage
===
Nomi is executed through a Python-based runner, with parsing performed by Lark and programs lowered into a Python AST before being interpreted by a layered runtime. Python serves as the current host environment, enabling rapid iteration and reference testing during development.

Parsing and evaluation can now be modified with substantial granularity, though the resumable-control subsystem (generator/coroutine–based) remains one of the more delicate components—functional, tested, but documented with caveats.

The primary entry point of the project is the execution of a **Nomi
source file**, currently exposed through a Python-based runner:

``` bash
python run_nomi.py [filename]  # defaults to demo.nomi
```

This command parses and executes the given Nomi file. The default
behavior runs `demo.nomi`, which serves as the reference execution
example. The implementation can be inspected directly in `run_nomi.py`.

A variety of additional Python and Nomi source examples---covering both
parsing and execution---are available under:

    prototype/test/data/sample_source/

These examples are designed to expose the full pipeline, from surface
syntax to runtime behavior.

-   **Grammar and Parsing:** Lark is used to define the grammar and
    perform parsing. Grammars live under `prototype/grammar/`, and
    parsing logic resides under `prototype/parse/`.
-   **AST Lowering:** Parsed programs are first transformed into a
    Python AST, establishing Python as the baseline semantic substrate.
-   **Execution:** Execution is handled by a layered interpreter located
    in `prototype/interpreter/`.


Nomi-specific semantics are introduced through AST reduction, semantic overlays, and controlled context management. Semantic shifts—such as constraint handling or yield-to-block generalization—are implemented through explicit AST rewrites coupled with controlled deviations from the baseline semantics.

This approach serves several purposes simultaneously:

-   It grounds the project in Python's historical evolution and
    practical experience\
-   It exposes internal inconsistencies and redundancies as concrete
    design inputs\
-   It enables orthogonal redesign through direct semantic substitution

Semantic extensions---such as **constraint handling** and
**yield-to-block generalization**---are implemented through explicit AST
rewrites combined with embedded semantic shifts.

The test suite is located under:

    prototype/tests/

Most tests currently operate at the regression/functional level;
finer-grained coverage will be introduced gradually.

## AI Agent Entry Point

The repository includes a root `opencode.json` config file for AI coding
agents running under OpenCode. It sets the default model, enables `pyright` LSP
and `ruff` formatting for Python files, maps instruction files, controls
permissions, and provides commented-out templates for providers, agents,
commands, and MCP servers.

The root `AGENTS.md` file serves as the project-level working map for setup
commands, test commands, repository structure, design-document reading order,
and long-running Codex-style checkpoint workflow.

The companion process note `ai_collaboration.md` explains how
Nomi uses AI for exploration, critique, implementation planning, test pressure,
and checkpointing while keeping code, tests, and active design docs as the
source of truth.

These artifacts follow the public AGENTS.md convention and reflect the existing
Nomi AI collaboration history documented in `implementation_guideline.md`, the
tracked `.codex/config.toml`, and the AI-assisted design notes under
`../archive/design_review/`.

Use `AGENTS.md` as the first stop for agent work, then follow its links into
the active design documents before changing parser, interpreter,
constraint, or yield-to-block behavior.

## Web Playground

The web playground under `web/` provides a browser-based Nomi editor backed by
Monaco and Pyodide. It is a static site: the Python-hosted prototype is loaded
into the browser from files listed in `web/manifest.json`, and sample programs
are loaded from `samples/*.nomi`.

The playground has two execution modes. `Run File` and `Ctrl+Enter` evaluate
the current editor contents from a clean interpreter session. `# %%` comments
split a file into lightweight cells; `Run Cell` and `Shift+Enter` evaluate the
current cell against the browser session, while `Run All` restarts that session
and evaluates all cells in order. The `Cells` result tab keeps a compact
input/output history beside the plain output and bindings views.

Use the launcher for local testing:

```bash
python3 scripts/launch_web.py
```

The launcher regenerates the manifest, picks the requested port or the next
available one, starts `python3 -m http.server`, and opens the playground. Common
options:

```bash
python3 scripts/launch_web.py --no-browser
python3 scripts/launch_web.py --port 8090
python3 scripts/launch_web.py --strict-port
```

Regenerate or check the manifest directly with:

```bash
python3 scripts/make_web.py
python3 scripts/make_web.py --check
```

`make_web.py` includes prototype `.py` and `.lark` runtime files plus
`samples/*.nomi`. When `samples/demo.nomi`, `samples/demo_terse.nomi`,
`samples/notebook_intro.nomi`, or another focused sample changes, rerun the
manifest generator before testing the web editor.

Known UI issues (side-by-side scrolling, Monaco layout) are tracked in
`web/web_playground_ui_challenges.md`.

## Portable Docker Notebook

The repository can be packaged into a portable Linux-based Jupyter image with:

```bash
python3 scripts/run_nomi_docker.py
```

The launcher is designed to be the single host command for first run and reuse.
It checks for Docker, can set up Docker CLI plus Colima on macOS through
Homebrew when Docker is not ready, builds the root `Dockerfile` when needed,
starts or reuses the `nomi:jupyter` container, and opens
`notebooks/nomi_syntax_tour.ipynb` in Jupyter Lab with the local `Nomi` kernel
registered inside the container.

The Docker context is bounded by `.dockerignore`, which excludes local scratch
files, generated reports, installed JavaScript dependencies, Python caches, and
distribution artifacts while keeping source, notebooks, documentation, and AI
artifacts in the image.

The container entrypoint lives at `tools/docker/serve_nomi_notebook.py`.


## Building a New Substrate Beneath a Familiar Surface

While Python serves as Nomi’s conceptual and semantic baseline, almost all infrastructure beyond the standard AST layer has been built from the ground up. The parser is hand-rolled with Lark; the evaluator, environment model, and resumable-control mechanisms are entirely new. Python’s built-in `ast.parse` and `exec` are used only for reference tests—ensuring that, where Nomi intentionally follows Python, alignment is exact.

The implementation still uses Python’s concrete data structures (dicts, lists, objects) and function-calling mechanism, but only through thin, explicit abstraction layers. These layers are intentionally designed to be peeled away as the implementation matures—making room for a VM-based interpreter, custom bytecode, or a stack-machine execution model.

Python is thus the host, the semantic reference, and the bootstrap substrate, but not the destination. The internal architecture is already oriented toward eventual decoupling, and many of the bridges into the Python runtime are intentionally one-way and marked for removal when the language is ready.
