# Snapshot Regeneration

Use when semantic changes require regression snapshot updates.

Prompt:

```text
Regenerate Nomi snapshots only after confirming the behavior change is intended.

Before regeneration:
- identify the semantic change;
- run the narrow failing regression or feature test;
- explain why the old output is stale.

Command:
pytest --force-regen prototype/tests/regression/test_interpreter.py

After regeneration:
- list changed snapshot files;
- inspect representative diffs;
- run the focused regression again without --force-regen;
- summarize the semantic reason in the final answer.
```
