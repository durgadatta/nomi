# GEMINI.md - Nomi Project Instructions

This file provides Gemini-specific instructions for working on the Nomi project. These instructions take precedence over general defaults.

## Project Overview
Nomi is an experimental programming language built around a small, coherent core: values, bindings, functions, calls, blocks, constraints, and controlled evaluation. It is currently implemented as a Python-hosted prototype.

- **Parsing**: Uses Lark with layered grammar (`prototype/grammar/layers/`).
- **AST**: Lowers to Python AST where possible, with custom Nomi AST for specific features.
- **Interpreter**: Custom layers for Python-compatible and Nomi-specific behavior.

## Core Mandates & Principles
1. **Python Parity**: Preserve Python parity where Nomi intentionally follows Python. Explicit semantic departures MUST be documented and verified with tests.
2. **High-Risk Areas**: Binding, constraints, and resumable control (yield-to-block) are high-risk. ALWAYS read relevant docs in `docs/features/` before modifying these.
3. **Small Primitives**: Favour small semantic primitives that combine into richer forms over feature accumulation.
4. **Verification**: NEVER assume success. A task is only complete when behavioral correctness is verified with tests (usually `pytest`).

## Documentation Precedence
1. `AGENTS.md`: The primary agent entrypoint and repository map.
2. `README.md`: User-facing vision and examples.
3. `docs/language/` & `docs/features/`: Active design workspace and specs.
4. `docs/orientation/`: Implementation guidelines and AI collaboration doctrine.
5. `docs/archive/`: Historical material (not canonical specification).

## Recommended Workflows
1. **Research & Strategy**:
   - Read `AGENTS.md` and relevant design notes.
   - Use `grep_search` and `glob` to map the codebase.
   - Identify affected parser, AST, interpreter, and test surfaces.
2. **Implementation (Focused Increments)**:
   - Create a short plan before editing.
   - Implement one coherent increment at a time.
   - For long-running tasks, use the checkpoint note format specified in `docs/orientation/ai_collaboration.md`.
3. **Validation**:
   - Run focused tests: `pytest prototype/tests/path/to/test.py`.
   - Run full suite: `pytest`.
   - Update documentation if behavior or design changes.

## Code & Style Guidelines
- **Python Style**: Match surrounding code; prioritize readability.
- **Testing**: Tests should name intended semantic behavior, not just implementation details.
- **Comments**: Sparse but useful, especially around complex control flow.
- **Diagnostics**: Always consider what failure or diagnostic should exist when a feature is misused.

## Common Commands
- **Install**: `pip install -e .`
- **CLI**: `python3 scripts/cli.py <file>.nomi`
- **Tests**: `pytest`
- **RAG/MCP**: `python3 -m tools.rag_mcp.mcp_server`
