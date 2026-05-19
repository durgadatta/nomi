# Start Task

Use when beginning a non-trivial Nomi task.

Prompt:

```text
Restate the concrete goal, identify the likely files and skills involved, then
make a short implementation plan before editing. Use AGENTS.md as the working
map and load the relevant .agents/skills/*/SKILL.md file. If local RAG/MCP is
useful, use it only for source discovery and read returned files directly.

Before coding, call out:
- goal;
- likely files;
- relevant skill(s);
- focused validation command(s);
- any user decision that would materially change the implementation.
```
