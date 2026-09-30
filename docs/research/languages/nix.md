# Nix

> Status: comparative evidence; scope is the Nix expression language.

## Observe

Nix uses a lazy functional expression language for configuration and build
description. Its expression model and build ecosystem are related but distinct;
a source expression is not by itself a reproducibility guarantee.
[Primary reference: Nix language](https://nix.dev/manual/nix/latest/language/).

## Judge And Pay

**Adopt** explicit build inputs and inspectable dependency identity as pressures.
**Reject** lazy ordinary Nomi calls and implicit environment access as a shortcut
to reusable configuration. **Defer** a dedicated build language: use ordinary
values and a capability-restricted evaluator first.

Nomi loses some concise recursive configuration composition and must manage
cyclic dependencies explicitly. It also cannot claim hermeticity from a lockfile
while a build can read arbitrary files, clocks, or network endpoints. Dependency
identity and execution authority are separate contracts.

## Test

Run the same build-description value with reordered declarations and two
different host environments. Require pinned inputs or a precise explanation of
which grant caused divergence. See [modules/tooling](../features/modules_tooling.md),
[effects](../features/effects.md), and [modules.nomi](../../design/targets/modules.nomi).
