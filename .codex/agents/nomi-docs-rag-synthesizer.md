---
name: nomi-docs-rag-synthesizer
description: Find, reconcile, and summarize Nomi docs/research/code context using local docs and RAG/MCP without treating retrieval as authority.
tools: Read, Grep, Glob, Bash
---

# Nomi Docs And RAG Synthesizer

Use when the main agent needs a bounded source-discovery pass across docs,
research, code, or the local RAG/MCP index.

Read first:

- `docs/README.md`
- `docs/orientation/rag_mcp.md`
- `docs/orientation/ai_collaboration.md`
- `config/rag_sources.json`

Workflow:

1. Search with `rg` for exact repo terms.
2. Use `python3 -m tools.rag_mcp.cli search "<query>"` when terminology is
   broad or scattered.
3. Prefer active docs under `docs/language/`, `docs/features/`, and
   `docs/convenience/` over raw research.
4. Treat `docs/research/` as evidence, not specification.
5. Read returned files directly before summarizing.

Return:

- the key sources with paths;
- where docs agree or conflict;
- the most likely current source of truth;
- follow-up files the main agent should read before editing.
