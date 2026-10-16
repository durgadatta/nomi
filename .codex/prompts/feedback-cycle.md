# Feedback Cycle

Use for one bounded implementation or design increment. Resume the existing
plan or registered packet before creating another task document.

Prompt:

```text
Complete one evidence-driven Nomi feedback cycle:

1. Ground the change in AGENTS.md, the relevant skill, current Git state and
   the existing plan/packet. Name the user pressure, owner, supported boundary,
   independent expected values/judgments/traces, and rollback condition.
2. Establish the oracle before implementing. Reproduce the failure or record
   the missing capability with a focused fixture. Derive expectations from the
   accepted contract or reference behavior, not the implementation being tested.
3. Implement the smallest coherent change. Keep unsupported behavior explicit.
4. Obtain an independent review against the oracle and boundary. Use a separate
   reviewer when available; otherwise disclose the self-review limitation.
   Check adverse cases and the diff, not just green output.
5. Repair substantive findings and add focused regression coverage. Rerun the
   affected checks; widen validation according to the changed semantic surface.
   Keep failed receipts alongside later successes. Do not weaken an oracle to
   clear a failure without recording the independently justified target change.
6. Update the current bridge in place with evidence, gaps, validation and the
   exact next fixture/action. Put actual logs in ignored reports. Keep narrative
   evolution concise and isolated in HISTORY.md.
7. Review the staged diff and create a coherent checkpoint commit when the user
   has authorized commits. Generated reports remain ignored; copy a concise
   result summary into the tracked note. Continue with the next owned increment.

For actual checks, run explicit argv with:
python3 -m tools.check_receipt --timeout 120 -- python3 -m tools.design_passes check

The runner records local evidence under reports/checks/. Read the receipt and
log before reporting its outcome. It does not select or run registry commands,
validate an oracle, confer permissions, attest source contents, or commit.
Only status=passed with returncode=0 is a successful command. A passed command
still proves only what that command checks; it does not close a whole packet.
Running, interrupted, timed_out, launch_error and runner_error are incomplete
or failed evidence. Compare command, cwd, times, HEAD and before/after status;
Compare the worktree_sha256 fingerprints too; worktree_changed or an unavailable
fingerprint requires checking which evidence is still applicable. Fingerprints
cover the index and nonignored files, not dependencies, ignored inputs or a
transactional snapshot. Rerun affected checks after edits;
never reuse a stale receipt as proof of the current tree.
```
