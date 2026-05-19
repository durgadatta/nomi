---
name: nomi-docs-rag-synthesizer
description: Find, reconcile, and summarize Nomi docs/research/code context using local docs and RAG/MCP without treating retrieval as authority.
tools: Read, Grep, Glob, Bash
model: sonnet
---

Canonical subagent prompt: `.codex/agents/nomi-docs-rag-synthesizer.md`.

Read and follow the canonical prompt. This Claude-native shim exists only so
Claude Code can discover the project subagent without duplicating the prompt.
