# Agent Assets

Shared AI-agent assets live here so they are not tied to one tool.

## Skills

`skills/*/SKILL.md` files are plain Markdown with YAML frontmatter. Agents with
native skill loading can load them directly; other agents can read the relevant
`SKILL.md` before working.

Current skills:

- `caveman`: ultra-concise output for low-context or terse models.
- `nomi-interp`: interpreter runtime changes.
- `nomi-language-design`: language design synthesis and syntax critique.
- `nomi-parse`: parser, grammar, and AST lowering changes.
- `nomi-reduce`: syntactic reduction/desugar work.
- `nomi-test`: test authoring and multi-interpreter test patterns.
- `nomi-web`: web playground and Monaco editor work.
