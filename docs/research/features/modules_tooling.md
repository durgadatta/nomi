# Modules And Tooling

> Status: comparative evidence; package principles accepted, implementation open.

User pressure: grow a script into a shared package while retaining readable
interfaces and useful explanations on every frontend.

| Evidence | Mechanism | Nomi consequence |
| --- | --- | --- |
| [OCaml](../languages/ocaml.md) | Module abstraction | Public signatures must support separate reasoning. |
| [Kotlin](../languages/kotlin.md) | Closed alternatives across boundaries | Variant evolution belongs in API compatibility checks. |
| [Roc](../languages/roc.md) | Host architecture | Explicit capability profiles across deployments. |
| [Dhall](../languages/dhall.md), [Nix](../languages/nix.md) | Integrity and dependency/evaluation boundaries | Pin identity separately from execution grants. |
| [Pkl](../languages/pkl.md) | Contextual errors | Preserve declaration and input locations. |
| [Uiua](../languages/uiua.md), [Racket](../languages/racket.md) | Live inspection and expansion tools | Explanations are product surfaces, not optional reports. |

```nomi
pub func register(raw: Value) -> Result[User, DecodeErrors]:
    return User.decode(raw)
```

A file is a module, declarations are private by default, and public functions
publish types/effects. Discovery must not execute module bodies. Manifests and
exact lockfiles define dependency identity. None of these principles imply a
finished package resolver or a settled generic/interface syntax today.

Tools should share versioned structured diagnostics, typed Surface/Core
artifacts, source maps, and capability metadata. A helpful browser experience
cannot rely on different semantics from the CLI. The current GitHub playground
is a migration surface, not evidence that target syntax is implemented.

**Experiment:** split the overall fixture into three modules; produce a proposed
public API diff, locked dependency graph, typed artifacts, and diagnostic JSON.
Change a variant, remove a grant, and make a lock hash stale. Require distinct
source-stable errors without discovery-time execution.

**User-facing gate:** only after conformance, add the smallest supported sample
to `samples/`, regenerate the manifest, and extend browser smoke coverage.
[Module target](../../design/targets/modules.nomi);
[tooling target](../../design/targets/tooling.nomi).

## Nominal Identity Across Package Instances

> Research extension checked 2026-10-04. Identity schemes below are challengers,
> not a settled package resolver, module-functor syntax, or compatibility promise.

### Existing Coverage And New Pressure

[Types/data](types_data.md) already distinguish nominal owned concepts from
structural boundary values. Open questions
[13/14](../open_questions.md#13-package-identity-and-federation) cover package
identity, federation, locks, editions and migration. The
[industrial model](../../design/industrial.md#modules-and-api-evolution)
allows independently declared editions to coexist through normalized Core
contracts. None of those facts alone determines which nominal types,
protocols, state instances, or re-exports are identical in one dependency graph.

The new pressure is the link between **artifact identity and semantic identity**.
A registry location is not package identity; a content hash is not by itself
a semantic equivalence proof; a matching qualified spelling is not necessarily
the same type. Conversely, rebuilding unchanged public declarations or moving
a verified artifact to a mirror should not accidentally create unrelated types.
The accepted file-module shape remains intact; this question extends open
questions 3/10/11/13/14/15 and the existing language-coherence D1-D3 agenda.

### Checked Primary Evidence

Sources checked 2026-10-04:

- [Cargo dependency resolution: version-incompatibility hazards](https://doc.rust-lang.org/cargo/reference/resolver.html#version-incompatibility-hazards),
  a rolling official reference, explains that different crate versions can
  expose distinct same-named types. It also describes re-exporting as part of
  the semver-trick workaround. This does not select Nomi's resolver or imply
  that arbitrary re-exports certify behavior compatibility.
- [OCaml 5.5 generative functors](https://ocaml.org/manual/5.5/generativefunctors.html)
  distinguishes fresh result types across generative applications from repeated
  application to the same defined module in the comparison it gives. This is
  evidence for a real type-identity fork, not a proposal for Nomi functor syntax.
- [Java SE 25 JVM specification section 5.3](https://docs.oracle.com/javase/specs/jvms/se25/html/jvms-5.html#jvms-5.3)
  makes a runtime class/interface's binary name and defining loader both relevant
  to identity. Loader isolation is one specified host model, not a portable
  rule Nomi should inherit through its JVM adapter.

These mechanisms differ. The experiment compares the user-visible guarantees
they motivate; it does not claim Rust crates, OCaml modules and JVM loaders are
one interchangeable package system.

### A Sharp Counterexample

Original dependency/type metalanguage, not accepted import syntax:

```text
application imports library A and library B
A exports Money from ledger package revision 1
B accepts Money from ledger package revision 2
both Money declarations display the fields amount and currency
revision 2 changes an admitted currency/amount constraint or codec policy
application passes A's Money to B
```

If identity is merely the display name or field shape, the crossing can erase
the constraint/owner difference. If every build-content change creates a new
type, even a private implementation repair may force unnecessary adapters.
If a stable public identifier always unifies the types, a changed contract can
be incorrectly treated as unchanged. Source, wire and behavior compatibility
must be checked separately; no digest settles all three.

A second pressure comes from two independently created graph/catalog stores.
Each issues a local `NodeId(1)`. The nominal NodeId declaration may be shared
while the issuing owner differs. Preventing wrong-store use can involve a
runtime owner check or a fresh branded type/region; making all module instances
generative is not the only solution, and would need substantial type machinery.

### Competing Contracts

| Candidate | Nominal declaration identity | State-instance identity | Cost or limit |
| --- | --- | --- | --- |
| Package-qualified revision identity | Resolved package identity/revision plus module and declaration owner | Ordinary values/handles carry their issuing owner separately | Clear duplicate-version rejection; harmless revisions may still require explicit adapters or re-exports |
| Stable public identity with checked compatibility | Stable declaration identity plus versioned public-contract/interface evidence | Separate state owner unless a protocol explicitly brands it | More reuse; requires enforceable evolution rules and honest treatment of non-projectable predicates |
| Explicit generative owner | An admitted factory/module boundary can create fresh type/brand identity | Fresh identity tracks each declared instance | Strong wrong-owner separation; first-class identity, quantification, storage and interface export are unresolved |

These are candidates for specific roles, not a requirement that every module
be dynamically instantiated or every package version be incompatible. Compare
an initial fixed nominal declaration with explicit runtime owner validation
against fresh brands on the store example. Ordinary factories and data adapters
remain the long form; no source-language module instantiation syntax is admitted.

For protocol dispatch, the contract must identify the protocol owner, target
type owner, implementation owner and any admitted compatibility mapping.
An imported extension cannot turn two distinct nominal types into one by
matching their spelling. A re-export may preserve the original declaration
owner; a new wrapper declaration intentionally creates another identity.
Which of these facts a future interface producer records is still open.

### Edge Matrix

| Case | Fact to preserve | Discriminator |
| --- | --- | --- |
| Diamond dependency resolves to one identical artifact | Both import paths reach one declaration owner | Do not duplicate identity merely from graph path or mirror location |
| Diamond dependency contains incompatible revisions | Two source/constraint owners despite similar spelling | Reject crossing or require a declared adapter/compatibility mapping |
| Re-export versus new wrapper | Original declaration owner versus newly created domain concept | Hover and diagnostics distinguish aliasing from nominal conversion |
| Private implementation changes | Public interface identity versus executable behavior | Do not equate stable interface identity with proved behavioral equivalence |
| Constraint calls a private helper whose meaning changes | The public contract depends on behavior not just field spelling | Track relevant contract dependency or invalidate its compatibility evidence |
| Two independently created stores issue the same local ID | Declaration type and issuing owner are separate | Runtime owner rejection or a checked brand; no accidental cross-store match |
| Two compatible editions normalize to Core | Syntax normalization versus type/codec/effect meaning | Compare resolved contracts; edition coexistence is not automatic nominal unification |
| Two extensions implement similarly named protocols | Exact protocol/type/implementation owners | Ambiguity reports both resolved owners, not order-dependent host dispatch |
| Loader or notebook session resets | Runtime incarnation versus stable declaration/reference | Reject stale instance handles without silently changing the nominal declaration |
| Wire payload carries a nominal-looking name | External text/schema is not trusted runtime type identity | Decode against a declared version/owner; do not deserialize type or capability authority |
| Registry transfer/fork or mirror replacement | Naming authority, artifact integrity and semantic owner | State when identity is preserved, transferred or deliberately new |
| Public type disappears or gains a closed variant | API identity versus compatibility of its inhabitants/matches | Report affected calls/matches independently of a successful lock resolution |

The private-helper row deliberately challenges a purely textual interface hash.
The [canonical module contract](../../design/semantics.md#modules-and-packages)
says private implementation changes do not affect public interface artifact
identity. A dependency that determines an exported constraint's meaning is not
therefore established to be semantically irrelevant. The experiment must name
what the interface exposes or records, and distinguish dependency invalidation
from renaming an otherwise unchanged declaration. This page does not weaken
or silently replace the target rule.

### Nomi Normal Form And Inspection

Placement: package resolution, core nominal/protocol identity, and versioned
module interfaces; data migration and store ownership remain ordinary library
contracts where sufficient. No new import punctuation or package grammar is
required to formulate the problem.

```text
resolve and verify the exact package graph
-> assign declaration/protocol owners under the candidate identity scheme
-> resolve imports and re-exports without executing module bodies
-> instantiate only explicitly admitted state/brand owners
-> compare public constraints, effects, codecs and type references
-> check crossings or apply an explicit declared adapter
-> report distinct source, artifact, interface, wire and runtime-instance facts
```

Inspection should display readable provenance for both same-spelled types,
the dependency paths that brought them into the program, and whether a name
is a re-export, wrapper, compatibility mapping or fresh owner. A public API
diff reports variant/constraint/effect changes, not only lock hashes. Cache keys
must use the relevant owner/edition/interface basis rather than rendered type
names. A formatter or source migration cannot promise a data migration simply
because both versions parse.

### Named Subexperiment Under Questions 13 And 14

**Subexperiment: diamond identity and fresh owners.** Compare revision-qualified
and stable-contract identities; retain explicit generativity as a challenger
only for the independently instantiated store pressure.

| Program level | Prepared inputs | Required observations |
| --- | --- | --- |
| Beginner | One package imported through two paths; re-export versus new wrapper; identical artifact moved to a mirror | Resolved owner identity, accepted same-type crossing, readable wrapper conversion and unchanged mirror result |
| Production | Application plus two libraries exposing Money across a diamond; public/private change; two independently created catalogs | Locked graph, interface dependencies, protocol owners, explicit crossing/adapters and issuing-store identity |
| Failure-heavy | Constraint helper changes; incompatible closed variant; same-spelled protocol collision; stale runtime instance after reload | Negative compatibility judgment with both origins, affected matches, no authority/type reconstruction from wire text |

First compare proposed interface records and manual positive/negative judgments
without running module initialization. Retain beginner/production/failure-heavy
source shapes using accepted imports and ordinary calls, with identity fields
kept as contract metalanguage. A later isolated resolver/interface spike should
compare cache reuse and clean re-analysis on those facts; it must not pretend
to prove arbitrary helper equivalence or execute a package to learn its API.

Falsifiers: registry location changes a verified artifact's identity; distinct
constraints are silently unified; a re-export invents a new wrapper; a stale
instance becomes valid solely because its numeric ID matches; or independently
checked libraries must inspect each other's private source to identify a type.
Remove a stable-identity candidate if its compatibility evidence cannot be
enforced at package boundaries. Remove generative machinery if ordinary owner
checks solve the measured pressure with less recognition/interface cost.

**Unperformed:** no package resolver, nominal identity implementation, interface
producer, compatibility proof, generative typechecker, loader integration or
reader study executed these cases. Existing lock/artifact infrastructure and
documentation validation do not settle this semantic identity contract.

## Definition Visibility During Interactive Change

> Research continuation 2026-10-10: questions 14/17 with identity from question
> 13; no live-reload semantics selected here.

[Julia's world-age review](../languages/julia.md) supplies primary evidence that
interactive redefinition needs a visibility model. This is a different question
from whether two package declarations share nominal identity. It also interacts
with Nomi's lexical capture and the existing
[representation/revision trial](../../design/interaction_model.md#paired-representation-and-revision-trial).

Compare three candidates: a run keeps a frozen definition revision; a running
computation explicitly adopts a newer revision at a named boundary; or calls
consult current definitions dynamically. Separate a closure's captured values
from its referenced definition versions. A stable displayed function name is
insufficient evidence that two executions used the same implementation.

**Prepared schedule:** revision A starts a task and creates a closure; revision
B changes a helper; the old task resumes, the old closure runs, a new call runs,
and an inspected cached result is requested. Fix the definition/input/context
identity expected at each observation under each candidate. Recompute authority
and resource validity where required; changing code must not renew an expired
handle or reuse a revoked grant. Include a change to a public variant/constraint
that makes an old value incompatible, without silently migrating it.

Inspection must distinguish a result produced under A from a fresh B result,
explain the dependency that invalidated a cache, and identify a suspended task's
version. Compare predictability, restart cost, edit-to-feedback time, retained
memory, and repair complexity. No method-table implementation, reload engine,
or usability study is established by these prepared comparisons.
