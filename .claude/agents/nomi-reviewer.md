---
name: nomi-reviewer
description: Review Nomi code or docs changes for regressions, missing tests, semantic drift, and unsafe agent/tooling behavior.
tools: Read, Grep, Glob, Bash
model: sonnet
---

Canonical subagent prompt: `.codex/agents/nomi-reviewer.md`.

Read and follow the canonical prompt. This Claude-native shim exists only so
Claude Code can discover the project subagent without duplicating the prompt.
