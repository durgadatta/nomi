# History: Undo Which World?

> Status: version-history evidence and proposed change/commit laws.

## Evidence And Pressure

Git revert records a reversing patch as a new commit rather than removing
history. This fact says nothing about reversing external effects caused by
running the earlier program.
[Git revert contract](https://git-scm.com/docs/git-revert).

Undoing a text edit, restoring an immutable model snapshot, retrying an action,
and compensating a remote payment are different operations. They may look alike
in a toolbar while having incompatible guarantees.

## Nomi Normal Form And Placement

A pure model change is proposed against a base revision and committed atomically
after validation. Its history can retain old/new values under a retention policy.
An external action instead has a typed outcome, authority, and application-owned
idempotency or compensation policy. Cancellation means stop/join according to
the operation contract; it does not promise no effect occurred.

Replay needs source, input, host observations, and profile. A replayable fake
capability can reproduce observations without reissuing real requests. An old
approval is never replayable permission. **Adapt:** reviewable change records,
explicit recovery, and useful causal history. **Reject:** universal undo or a
retry block that repeats effects implicitly.

## Discriminating Experiment

Edit an invoice quantity, undo it, then simulate a publication that succeeds
before its response is lost. Show the difference between model reversal and an
unknown remote outcome. Require explicit status and an idempotent recovery path,
not an optimistic retry. In the playground, Reset must explain the session state
it clears; it must not imply that an executed external action was undone.
