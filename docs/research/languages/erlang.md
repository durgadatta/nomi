# Erlang

> Status: comparative evidence; scope is OTP supervision.

## Observe

OTP supervisors manage child processes with explicit restart strategies and
restart limits. Recovery is an architectural policy rather than a local
exception-catching trick.
[Primary reference: supervision principles](https://www.erlang.org/doc/system/sup_princ.html).

## Judge And Pay

**Adopt** naming recovery and ownership policies. **Defer** restartable actor
trees to libraries or a service profile. **Reject** equating a lexical TaskGroup
with a supervisor: joining finite work and maintaining a long-lived service
have different lifetime and state-recovery obligations.

Nomi's initial task model may be simpler for a batch import but less useful for
resilient services. Automatic restart also risks duplicate external actions.
A proposed supervisor needs a state, idempotency, authority, and observability
contract before syntax, not just an appealing "restart on failure" option.

## Test

Sketch a worker that publishes a report and crashes just after publication.
Force a restart; specify how duplicate publication is detected. Keep this
separate from [the finite concurrency fixture](../../design/targets/concurrency.nomi).
See [concurrency](../features/concurrency.md) and [effects](../features/effects.md).
