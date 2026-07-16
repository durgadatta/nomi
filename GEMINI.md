# GEMINI.md - Nomi Project Instructions

This file provides Gemini-specific instructions for working on the Nomi project. These instructions take precedence over general defaults.

## Project Overview
Nomi is an experimental general-purpose language targeting Python-like
cognitive ease with explicit types, data boundaries, failure, effects,
concurrency, and industrial tooling. It is currently implemented as a
Python-hosted prototype plus a Rust/WASM-to-JavaScript browser path.

- **Parsing**: Uses Lark with layered grammar (`prototype/grammar/layers/`).
- **AST**: Lowers to Python AST where possible, with custom Nomi AST for specific features.
- **Interpreter**: Custom layers for Python-compatible and Nomi-specific behavior.

## Core Mandates & Principles
1. **Target Authority**: `docs/design/` defines the language target. Preserve
   current prototype behavior only while it remains a supported migration
   surface; intentional target changes may break Python parity and existing
   Nomi syntax.
2. **High-Risk Areas**: Binding, constraints, data boundaries, Result
   propagation, resources, effects, and concurrency are high-risk. Read
   `docs/design/syntax.md` and `docs/design/semantics.md` before modifying them.
3. **Small Primitives**: Favour small semantic primitives that combine into richer forms over feature accumulation.
4. **Verification**: NEVER assume success. A task is only complete when behavioral correctness is verified with tests (usually `pytest`).

## Documentation Precedence
1. `AGENTS.md`: The primary agent entrypoint and repository map.
2. `README.md`: User-facing vision and examples.
3. `docs/design/`: Canonical target language and industrial contracts.
4. `docs/research/`: Consolidated evidence and bounded open questions.
5. `docs/orientation/`: Current implementation and collaboration guidance.

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
