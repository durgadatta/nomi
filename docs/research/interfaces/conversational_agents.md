# Dialogue: Negotiate Intent Before Execution

> Status: agent-interface evidence and proposed Nomi safety contracts.

## Evidence And Pressure

VS Code documents tool approvals and security controls for agent workflows.
Those UI controls are not a substitute for a runtime security boundary.
[Approvals](https://code.visualstudio.com/docs/agents/run/approvals),
[Security](https://code.visualstudio.com/docs/agents/run/security).

Natural language can help a person explore an underspecified goal. It is not
automatically a precise, reproducible, authorized program. A fluent explanation
can conceal changed assumptions; hostile input can masquerade as an instruction.

## Nomi Normal Form And Placement

An agent proposes ordinary source, typed data, or a versioned change set. The
proposal identifies assumptions, unresolved choices, expected effects, tests,
and provenance. It is then parsed, checked, inspected, and authorized using the
same contracts as a human-authored edit. Model output never manufactures a
capability or overrides an instruction boundary.

Separate claim kinds: generated suggestion, compiler fact, test observation,
and host result. A "repair" must preserve error causes and identify changes to
public behavior. No natural-language expression is admitted into core evaluation;
model-backed APIs, if explored, are explicit effectful libraries with budgets,
privacy policy, and nondeterminism in their contracts.

## Discriminating Experiment

Ask an agent to fix an invoice import containing malicious text in a customer
field. Review its source diff, decoding behavior, and requested capabilities.
Change the source after approval and verify the old proposal cannot execute
against it. Compare an explanation to actual diagnostics. The GitHub playground
payoff is a reviewable proposed program, not a chat answer silently treated as
trusted code or an implemented agent feature.
