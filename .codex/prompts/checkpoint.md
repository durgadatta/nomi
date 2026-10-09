# Checkpoint

Use during long sessions, handoffs, or context compaction.

Prompt:

```text
Create a concise checkpoint for this Nomi task:
- Goal
- Current plan
- Completed changes
- Next exact step
- Open questions
- Tests/checks run and results
- Receipt paths and concise outcomes, including failures, checked HEAD/dirty
  state, and any edits since verification (reports/checks remains ignored)
- Review findings resolved or outstanding; smallest durable improvement made
  from this cycle, or why none was justified
- Files touched

Keep it operational. Do not write a narrative diary. If a repo-root task note
is not explicitly needed, keep the checkpoint in the conversation/final answer.
```
