# Review

Use when asking an agent to review a change.

Prompt:

```text
Review the current Nomi diff. Prioritize findings over summary.

Look for:
- behavior regressions;
- parser/lowering/interpreter mismatch;
- missing focused tests or snapshots;
- docs that contradict active language direction;
- generated/local artifacts in git;
- overbroad hooks, permissions, MCP access, or agent instructions.
- independent expected judgments/traces and adverse cases at support boundaries;
- stale or incomplete check evidence, including edits after a passed receipt.

Return:
- findings ordered by severity with file paths;
- open questions/assumptions;
- checks run or recommended.

Use .codex/prompts/feedback-cycle.md to turn substantive findings into focused
regressions, repairs, fresh checks and the next bounded action.
```
