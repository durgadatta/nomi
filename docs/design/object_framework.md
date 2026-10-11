# Engine-Free Objects

> Status: designing framework, 2026-10-10. A bounded Python research implementation
> runs typed composition, inspection, closed definitions, independent lab replay
> and explicit realization with required input conditions.
> This does not admit Nomi syntax, a public package, or a universal domain IR.

An object should express **what something means and how it relates to other
objects**, independently of which engine might realize it. It may be a value
expression, an input contract, a model description, a document specification,
an operation definition, or an intended outcome. Some objects can be realized;
others remain useful descriptions with unresolved obligations.

This is broader than lazy evaluation. Delaying a calculation addresses *when*
an engine computes. Engine-free objects also separate meaning, identity,
composition, inspection, domain validation and realization. A document
description can exist without a renderer; an analysis can exist without data;
the same expression can have several explicit implementations. Describing an
object neither requests execution nor guarantees a realization exists.

The [vision](vision.md) owns the broader purpose. The
[primitive synthesis](synthesis.md#candidate-primitive-synthesis-and-integration-path)
supplies the language context. This framework is an ordinary library/artifact
experiment under the language-coherence packet, whose
[review](../review/2026-09-29-language-synthesis.md) records evidence and next work.
The [statistical interface](statistical_data.md) is a domain on top of this
direction. Its observation domains, masks and scientific laws retain their own
authority.

The [composition hierarchy](primitive_composition.md) connects this experiment
to the broader language. Its input/literal/alias/apply/derived/description roles
classify inert objects; they are not the six semantic families used to compare
language execution, authority and scope.

## Try A Composition Before Supplying Inputs

From a source checkout, with Python only:

```bash
python3 -m tools.object_interface check docs/research/object_framework/composition.json
python3 -m tools.object_interface inspect docs/research/object_framework/composition.json document
python3 -m tools.object_interface compare docs/research/object_framework/composition.json squared expanded_square
python3 -m tools.object_interface compile docs/research/object_framework/composition.json --backend python-exact-text
python3 -m tools.object_interface run docs/research/object_framework/composition.json docs/research/object_framework/bindings.json --backend python-exact-text
```

The [composition](../research/object_framework/composition.json) describes an
unknown quantity, its square, an explicitly expanded multiplication, twice the
square, a greeting, and a document description. Checking and comparison need
neither a quantity nor a name. `squared` and `expanded_square` compare as
`equivalent` through the declared definition of square. The document can be
inspected even though the example backend cannot render it.

Compilation explicitly selects the pure arithmetic/text adapter and checks its
capabilities without running its implementations. Binding then supplies
`quantity = 3` and `name = "Ada"`. Execution returns `doubled = 18` and
`published = "Hello, Ada"`. The original objects remain unbound and unchanged.
Exit codes: 0 for success/equivalence, 1 for unknown equality, 2 for refusal.

## A Small Shared Envelope

The [implementation](../../tools/object_interface/model.py) gives each object:

| Part | Meaning |
| --- | --- |
| Identity | A named reference qualified by its graph revision; unrelated inputs remain distinct even with equal types. |
| Nominal family | A vocabulary-owned contract name. Equal JSON representations do not erase family distinctions. |
| Operation | A vocabulary-owned constructor or composition, with explicit role and revision context. |
| Ports | Named typed references, including ordered repeated references where a port accepts many. |
| Attributes | Bounded inert metadata checked against declared shapes; no callbacks or engine handles. |
| Definition | An optional closed pure composition over declared parameter ports. |
| Context | The full graph and vocabulary fingerprint used by checks, comparisons and realizations. |

The six implemented roles organize objects within this experiment; they are
not new language primitives:

| Role | Contract |
| --- | --- |
| Input | A typed abstract binding slot identified by its object ID; acquiring a value is a separate step. |
| Literal | An inert value checked by its family's declared value codec. |
| Alias | Another name for exactly one reference of the same family. |
| Apply | Typed composition with declared effects; execution requires an implementation. |
| Derived | A checked pure definition in terms of other objects; no executable extension code. |
| Description | An inspectable intention or specification, with no promised realization. |

For example, `square(x)` is defined as `multiply(x, x)`. This definition lives
in the [lab vocabulary](../../config/object_interface.json), not a backend.
Checking validates its ports and result family and rejects recursive or
effectful definitions. Normalization retains a shared DAG and never expands a
diamond into an exponential tree. Aliases and derived forms preserve a mapping
from original names to physical terms.

An operation declaring effects remains distinguishable in the graph: two
similar writes are not merged into one. The current executor refuses effectful
operations. Future authority, resources and scheduling belong to explicit
realization contracts; an effect name alone cannot grant permission.

## Work With Objects From Python

```python
from tools.object_interface import Graph, load_document
from tools.object_interface.examples import lab_vocabulary, python_backend

objects = Graph.from_document(
    load_document("docs/research/object_framework/composition.json"),
    lab_vocabulary(),
)
quantity = objects.ref("quantity")
revised = objects.compose("twice_quantity", "exact.double", {"value": quantity})
print(revised.ref("twice_quantity").inspect())  # Still unbound.

compiled = python_backend(revised.vocabulary).compile(
    revised, [revised.ref("twice_quantity")],
)
result = compiled.bind({"quantity": 7}).execute()
assert result.get(revised.ref("twice_quantity")) == 14
```

Every intermediate is referable and can be requested independently. Only the
dependencies of selected outputs need bindings and backend capabilities.
All objects are checked, including those outside the selected outputs.
`compose` returns a new revision and adds the new object to its outputs;
old references continue to refer to the old graph. Python handles belong to a
particular checked graph instance. After reloading an artifact, resolve its
named references through the new graph rather than reusing old handles.

Public documents, inspection results, bindings and returned values are detached
snapshots. Each execution is a separate realization; it does not cache a result
inside an object or change that object's identity.

## Separate The Claims

| Stage | Implemented evidence | Limit |
| --- | --- | --- |
| Describe/check | Unique names, acyclic references, nominal port compatibility, inert attribute shapes | Does not establish domain refinements, actual input validity or scientific assumptions. |
| Compare | Structural identity after aliases and vocabulary-declared pure definitions | No arbitrary algebra, commutativity, solver, or backend conformance proof. `unknown` does not prove inequality. |
| Compile | Explicit backend identity/revision, exact vocabulary match, supported pure operations/codecs | Implementations are trusted supplied Python code; declared purity is not independently certified. |
| Bind | Exact required slots, inert snapshot, family value codecs, content digest | Does not verify external dataset provenance or deeper domain obligations. |
| Execute | Explicit invocation, output-codec checks, detached values, logical/physical mapping and receipt | Successful execution does not certify mathematical implementation correctness or scientific validity. |

`compare` is qualified by the full vocabulary content, including definitions.
Editing a definition changes its fingerprint and invalidates old graph and
backend claims. `verify` reconstructs the comparison and rejects a changed
receipt/context; it uses the same checker and is explicitly **not independent
verification**. A separate [lab consumer](../../tools/object_replay.py) now
rechecks the whole source graph, nominal types and closed definitions with only
the standard library, without importing the planner or backend:

```bash
python3 -m tools.object_interface compare docs/research/object_framework/composition.json squared expanded_square > /tmp/nomi-object-comparison.json
python3 -m tools.object_replay config/object_interface.json docs/research/object_framework/composition.json /tmp/nomi-object-comparison.json
```

The consumer independently admits the pinned arithmetic/text/document vocabulary.
It refuses changed vocabularies, altered sources and forged term/context records.
It does not automatically trust every definition supplied by a new domain.
The statistical exact-law consumer remains separate for its own v1 theory;
neither consumer certifies an engine's implementations.

The envelope supports nominal families with composable structural codecs and parameter shapes.
It does not implement general parameterized types, predicate solving or Nomi's
full type system. Domain-specific structure stays in domain-owned contracts.
A model parameter record passing an inert shape check is still not a validated
model.

### Structural Contracts Without A Domain Engine

A codec can compose a closed record from named field codecs and an array from
an item codec. These are inert declarations checked before a binding or literal
is accepted. For example, a document specification can declare a Text title and
an array of sections, each with a Text heading and an array of Text paragraphs.
Every nested part can be checked before selecting a renderer.

`{"kind": "record", "fields": {...}}` requires exactly the declared fields;
all are required. `{"kind": "array", "items": {...}}` checks every item in
order. Bare record/array codecs retain their original shallow meanings. There
are no hidden defaults, coercions, optional fields or inferred schemas. Missing,
null and an empty container remain distinct. Schema fields use the lab's bounded
identifiers, with at most 128 fields per record.

Validation accumulates up to 128 independent errors with field/index paths,
stable codes and expected kinds; it does not echo rejected values. Record fields
are visited in sorted name order, with extra fields afterward, and arrays in
input order. A report marks `complete: false` when more errors exist. The Python
`ValueContractError.report` and CLI expose detached error records. Structural
validity does not establish an object's scientific or documentary suitability.

## Add A Domain Without Adding An Engine

### Explicit Obligations Before Realization

The [obligation protocol](../../tools/object_interface/contracts.py) adds a
separate engine-free artifact: named conditions referring to objects in one
graph context, with an owner, revision and rule. The initial lab admits only
two version-1 representation predicates: a strictly positive ExactInt and a nonempty
Text. Version 2 additionally admits nonempty arrays and paths through declared
record fields and typed array items. These are witnesses for the protocol,
not a general constraint language.
Nonempty Text includes whitespace; no trim or normalization is implied.

A version-2 requirement carries an explicit `path`, including `[]` for the
whole value. Every segment must follow the subject family's declared codec;
unknown fields, negative indices and predicates of the wrong kind are refused.
A declared array item path can be absent in an actual value: that refutes the
condition, while an unknown root input remains pending. A fixed index checks
that item only; it does not quantify over every section or paragraph.

Each condition is `satisfied`, `refuted` or `pending`. Literals and aliases of
literals can supply static evidence without inputs. An unknown input remains
pending until an explicit typed snapshot is supplied. Computed expressions
remain pending even with inputs: this checker never calls an evaluator to
guess their result. Claims about populations, models, effects or scientific
truth cannot be represented as supplied satisfied statuses.

The [example conditions](../research/object_framework/requirements.json)
require a positive quantity and a name with content:

```bash
python3 -m tools.object_interface requirements docs/research/object_framework/composition.json docs/research/object_framework/requirements.json
python3 -m tools.object_interface requirements docs/research/object_framework/composition.json docs/research/object_framework/requirements.json --bindings docs/research/object_framework/bindings.json
python3 -m tools.object_interface run docs/research/object_framework/composition.json docs/research/object_framework/bindings.json --backend python-exact-text --requirements docs/research/object_framework/requirements.json
```

The first returns `pending` with exit code 1. The second checks the supplied
snapshot without invoking any backend and returns `satisfied`. The third
explicitly attaches those conditions as required preconditions. A zero or
negative quantity, or an empty name, refuses binding **before backend callbacks
run**. Compile-time attachment also refuses a refuted literal, an unrelated
subject outside the selected realization, or a computed precondition this
protocol cannot enforce. Conditions are required only when explicitly attached.

The Python path is:

```python
from tools.object_interface import Requirements

conditions = Requirements.from_document(
    load_document("docs/research/object_framework/requirements.json"), objects,
)
print(conditions.check())  # Pending; no assumptions become facts.
compiled = python_backend(objects.vocabulary).compile(objects).require(conditions)
result = compiled.bind({"quantity": 3, "name": "Ada"}).execute()
assert result.receipt["requirement_evidence"]["status"] == "satisfied"
```

The realization receipt retains the static checkpoint under `requirements`
and binding evidence under `requirement_evidence`, with distinct phase labels.
An evidence replay reports its actual verdict; verifying a pending receipt does
not make its conditions satisfied. `Requirements.verify` uses the same checker.
The separate standard-library consumer now also independently admits these two
predicates, reconstructing the source, rule, type, context and binding evidence:

```bash
python3 -m tools.object_interface requirements docs/research/object_framework/composition.json docs/research/object_framework/requirements.json --bindings docs/research/object_framework/bindings.json > /tmp/nomi-object-conditions.json
python3 -m tools.object_replay config/object_interface.json docs/research/object_framework/composition.json /tmp/nomi-object-conditions.json --requirements docs/research/object_framework/requirements.json --bindings docs/research/object_framework/bindings.json
```

It verifies satisfied, refuted and pending verdicts without changing them.
Supplying computed values as if they were input slots, an asserted satisfied
status, or a changed predicate definition is refused. Richer domain validators
and their independent consumers remain separate admission work.

### Relate Several Objects Without An Engine

Version 3 uses ordered `operands`, each naming a subject and an explicit codec
path. It retains the three unary rules and adds two closed relations:

| Rule | Operands | Meaning |
| --- | --- | --- |
| `exact.le-v1` | Two integer representations | The first is less than or equal to the second, using exact integer order. |
| `text.equal-v1` | Two text representations | Exact text equality, preserving case, whitespace and Unicode representation. |

These are representation requirements, not nominal object identity or domain
equality. Matching document titles does not identify two documents; an integer
order does not establish compatible units or a valid statistical population.
Neither rule installs an operation in a vocabulary or calls an implementation.
Version-1/2 artifacts and receipt contexts retain their earlier contracts.

The [ordered bounds example](../research/object_framework/ordered_bounds_requirements.json)
relates separately named inputs before their addition is realized:

```json
{
  "id": "ordered",
  "rule": "exact.le-v1",
  "operands": [
    {"subject": "lower", "path": []},
    {"subject": "upper", "path": []}
  ]
}
```

Operand order and repeated references are preserved. Every subject and path
must be declared even if another operand is pending. Operand evidence records
`known`, `missing` or `pending`, with its source and path but no copied value.
A known missing path refutes the requirement, including when its peer remains
unbound: the relation requires both operands to exist. Otherwise any pending
operand keeps the relation pending. Only all-known operands can satisfy or
refute the actual comparison. Comparing an unbound input with itself stays
pending; this protocol is an evidence check, not an identity-law prover.

```bash
python3 -m tools.object_interface requirements docs/research/object_framework/ordered_bounds.json docs/research/object_framework/ordered_bounds_requirements.json --bindings docs/research/object_framework/ordered_bounds_bindings.json
python3 -m tools.object_interface run docs/research/object_framework/ordered_bounds.json docs/research/object_framework/ordered_bounds_bindings.json --backend python-exact-text --requirements docs/research/object_framework/ordered_bounds_requirements.json
python3 -m tools.object_interface requirements docs/research/object_framework/ordered_bounds.json docs/research/object_framework/ordered_bounds_requirements.json --bindings docs/research/object_framework/ordered_bounds_bindings.json > /tmp/nomi-ordered-bounds.json
python3 -m tools.object_replay config/object_interface.json docs/research/object_framework/ordered_bounds.json /tmp/nomi-ordered-bounds.json --requirements docs/research/object_framework/ordered_bounds_requirements.json --bindings docs/research/object_framework/ordered_bounds_bindings.json
```

The example satisfies the input relation and returns `total = 5`. Omitting
bindings leaves it pending. Reversing the supplied bounds refutes it, and an
attached required condition stops execution before any backend callback. Every
operand must belong to the selected realization and normalize to an input or
literal; computed operands remain pending and cannot be attached as preconditions.
Inputs needed only by conditions can be included separately through the
explicit mechanism below.

Workflow substitution rewires **all** operands. A composition containing v3
conditions promotes older unary conditions to single-operand records in v3;
a composition containing only v1/v2 conditions retains v2. Component inspection
retains each source owner, revision and context. Independent replay checks the
promotion, reference substitution and evidence without importing the producer.

Keep three questions separate: vocabulary definitions can establish symbolic
composition equality without inputs; requirement artifacts can validate
explicit snapshots; backend executions produce values. Relations do not
generalize the first into a solver or the third into a proof of a domain law.

### Bind Inputs Used Only By A Condition

A requested title can constrain publication without becoming part of its
rendered content or returned values. The [publication example](../research/object_framework/publication.json)
has a `draft` computation input and a `requested` condition-only input. Their
[condition](../research/object_framework/publication_requirements.json) relates
the draft's title to that request.

```bash
python3 -m tools.object_interface --vocabulary config/document_interface.json compile docs/research/object_framework/publication.json --backend document-blocks --requirements docs/research/object_framework/publication_requirements.json --include-condition-inputs
python3 -m tools.object_interface --vocabulary config/document_interface.json run docs/research/object_framework/publication.json docs/research/object_framework/publication_bindings.json --backend document-blocks --requirements docs/research/object_framework/publication_requirements.json --include-condition-inputs
```

Python callers use `compiled.require(conditions, include_condition_inputs=True)`
or `instance.compile(backend, include_condition_inputs=True)`. This option extends
the exact binding interface with the underlying slots of condition-only inputs;
aliases and repeated operands bind one slot. Condition-only literals need no
binding. Inspection and realization receipts distinguish `computation_inputs`,
`condition_inputs` and the out-of-computation `condition_subjects`. Output
selection, executable terms and their logical-to-physical mapping stay the same.
Condition values do not enter backend arguments unless they also belong to the
selected computation. All bindings contribute to the binding digest and typed
requirement evidence.

The default remains the closed selected realization, which refuses omitted
subjects. Inclusion must be an explicit boolean and requires a contract. It
never admits computed or effectful conditions, adds callbacks, chooses an
engine, or drops an unsatisfied condition. Each added slot needs an exact typed
snapshot before any callback can run. This is a laboratory binding interface,
not ambient authority or a guarantee that arbitrary callers cannot bypass a
separately owned policy.

### Compose A Universal Condition From A Collection And A Rule

Version 4 adds two closed condition forms: `relation` wraps the ordered operand
protocol, and `every` applies an existing unary rule to a declared path within
each collection item. The collection's item codec supplies the local contract;
the checker needs no renderer, dataframe or other domain engine. For example:

```json
{
  "id": "all_headings",
  "condition": {
    "kind": "every",
    "subject": "draft",
    "path": ["sections"],
    "item_path": ["heading"],
    "rule": "text.nonempty-v1"
  }
}
```

`path` must select an array with declared items or a text list. `item_path`
starts at the item codec; `[]` checks the item itself. A bare shallow array does
not supply enough evidence to admit a predicate. The full path/rule contract is
checked before values, including when the eventual collection is empty. Only
the three existing unary representation rules are allowed in `every`.

| Situation | Evidence |
| --- | --- |
| Unbound or computed collection | Pending; no implicit evaluation. |
| Known empty collection | Satisfied, with zero checked items: universal truth is vacuous. |
| All known items pass | Satisfied, with the number of checked items. |
| One or more items fail | Refuted, with indexed counterexample paths. |
| Declared collection/item index missing in a known value | Refuted, with a missing-path witness. |
| Item or artifact capacity exceeded | Refused, without issuing a verdict. |

“Every section has a heading” and “there is at least one section” are separate
conditions. Requiring paragraph arrays to be nonempty also does not establish
that each paragraph's text has content. Fixed inner indices inspect only that
index; this lab has one universal traversal per condition, with no nested
quantifiers, item-to-item pairing or Cartesian products. Domain packages still
own any stronger meaning.

The [v4 publication contract](../research/object_framework/publication_requirements_v4.json)
composes matching titles, nonempty sections, content in every heading, and a
nonempty paragraph array in every section. It uses the same graph, bindings and
renderer as the preceding example:

```bash
python3 -m tools.object_interface --vocabulary config/document_interface.json run docs/research/object_framework/publication.json docs/research/object_framework/publication_bindings.json --backend document-blocks --requirements docs/research/object_framework/publication_requirements_v4.json --include-condition-inputs
python3 -m tools.object_interface --vocabulary config/document_interface.json requirements docs/research/object_framework/publication.json docs/research/object_framework/publication_requirements_v4.json --bindings docs/research/object_framework/publication_bindings.json > /tmp/nomi-publication-conditions.json
python3 -m tools.object_replay config/document_interface.json docs/research/object_framework/publication.json /tmp/nomi-publication-conditions.json --requirements docs/research/object_framework/publication_requirements_v4.json --bindings docs/research/object_framework/publication_bindings.json
```

Evidence records the rule, source, paths, checked/total item counts and up to
128 failure paths per universal condition, without echoing input values.
`failures_complete = false` means further counterexamples were omitted; every
item was still checked. The envelope permits at most 4096 item checks in total,
counting repeated traversals separately. Entire evidence receipts retain the
1 MB artifact limit. These are lab capacities; a resource refusal must not
become satisfied, refuted or a claimed scientific conclusion.

Workflows carrying v4 conditions promote older conditions to `relation` records
and rewire the collection subject or every relation operand. Source ownership
remains in component inspection. Earlier standalone envelopes and older-only
workflow compositions retain their existing formats. The independently admitted
consumer checks traversal, witnesses, limits, promotion and substitution.

### Repair A Refused Condition

Required conditions stop binding before any backend callback. A typed
`RequirementContractError` preserves the exact static or binding receipt under
its detached `.report` property. Its failed records identify subjects, rules
and paths; universal conditions retain indexed counterexamples and their
completeness flag. The report includes context and binding digests rather than
copies of rejected values.

```python
from tools.object_interface import Graph, RequirementContractError, Requirements, load_document
from tools.object_interface.documentary import document_backend, document_vocabulary

publication = Graph.from_document(
    load_document("docs/research/object_framework/publication.json"),
    document_vocabulary(),
)
required = Requirements.from_document(
    load_document("docs/research/object_framework/publication_requirements_v4.json"),
    publication,
)
compiled = document_backend(publication.vocabulary).compile(publication).require(
    required, include_condition_inputs=True,
)
inputs = load_document("docs/research/object_framework/publication_bindings.json")
inputs["draft"]["sections"][1]["heading"] = ""
try:
    compiled.bind(inputs)
except RequirementContractError as failure:
    failed = [r for r in failure.report["requirements"] if r["status"] == "refuted"]
    assert failed[0]["condition"]["failures"][0]["path"] == ["sections", 1, "heading"]
```

Repair that heading and bind again; neither the graph nor the compiled plan
changed during refusal. A refuted literal produces the same exception with
static evidence when attaching the contract. The CLI exits with code 2 and
writes `{status: "refused", kind: "requirement-contract", message, evidence}`
to stderr. Evidence retains its original `refuted` verdict and can be supplied
to the independent consumer with the matching source and snapshot; refusing an
execution is not an independent proof of the report. Shape, capability and
capacity refusals remain distinct from a condition's counterexample.

### Domain Integration Order

1. Define nominal families and inert constructors in a versioned vocabulary.
   Preserve domain-specific contracts, including unresolved obligations.
2. Give each constructor typed ports and bounded attribute shapes. Use the
   description role when realization meaning has not been defined.
3. Supply a domain validator for refinements the shared envelope cannot prove.
   Keep its verdict separate from generic composition checking.
4. Define only settled pure conveniences as closed compositions. Add independent
   examples and negative cases before extending equivalence claims.
5. Supply an explicit adapter with a pinned vocabulary and capability table.
   Refuse unsupported semantics or conversions before executing implementations.
6. Record bindings, requested references, implementation revision, values and
   failures. Test the adapter against independent domain oracles.

The [statistical descriptor adapter](../../tools/statistical_interface/engine_free.py)
derives 35 nominal description families from the existing catalog. It first
runs the statistical descriptor validator, then constructs generic objects with
the same IDs, parameters and dependencies. The derived generic fingerprint
pins port/shape metadata; the statistical catalog and its checker remain the
domain authority. These descriptions cannot execute merely because someone
provides a backend. Statistical computation graphs and their exact mean proof
still use the existing specialized checker; they have not been migrated into
generic arithmetic or weakened to nominal-family checking.

## A Document Domain With Explicit Rendering

The [document vocabulary](../../config/document_interface.json) owns a nominal
`DocumentSpec`: a title and ordered sections, each with a heading and ordered
text paragraphs. All fields are required; empty strings and arrays are
structurally valid. The separate [publication conditions](../research/object_framework/document_requirements.json)
require a nonempty title, a section and its first heading. Those optional,
explicit conditions do not claim every heading has content.

The [document graph](../research/object_framework/document.json) has named input,
description, title, paragraph count, render request, conversion and published
objects. None contains an engine. Describing a document remains passive;
`document.render_text` is a separate request returning nominal `RenderedText`.
An explicit `rendered.as_text` converts it to ordinary Text. Equal string
representations do not make these types interchangeable.

The bounded plain-text profile preserves all Unicode, whitespace, embedded
newlines and empty parts. It orders blocks as title, then each section heading
and its paragraphs; adjacent blocks have two newline separators and the result
has one added trailing newline. Paragraph count counts items, not lines.
The [two explicit renderers](../../tools/object_interface/documentary.py) use
block joining and incremental concatenation. They are trusted local callbacks,
tested against independent expected values; agreement is not a formal engine
conformance proof or evidence of equal performance.

```bash
python3 -m tools.object_interface --vocabulary config/document_interface.json check docs/research/object_framework/document.json
python3 -m tools.object_interface --vocabulary config/document_interface.json requirements docs/research/object_framework/document.json docs/research/object_framework/document_requirements.json --bindings docs/research/object_framework/document_bindings.json
python3 -m tools.object_interface --vocabulary config/document_interface.json run docs/research/object_framework/document.json docs/research/object_framework/document_bindings.json --backend document-blocks --requirements docs/research/object_framework/document_requirements.json
python3 -m tools.object_interface --vocabulary config/document_interface.json run docs/research/object_framework/document.json docs/research/object_framework/document_bindings.json --backend document-stream --output title
```

Both renderers return the fixture's complete text and `paragraph_count = 3`.
The last command selects only the `title` intermediate and returns
`"Research plan"`. `--output` is repeatable on compile/run; omitted outputs use
the graph's selection. Selecting the description for execution is refused.
The [independent consumer](../../tools/object_replay.py) separately pins this
document vocabulary and validates its nominal ports and nested values. It
reconstructs version-2 paths, predicates and verdicts without producer or engine
imports. Its admission remains bounded to two reviewed vocabularies; editing a
codec or definition creates a new unadmitted context.

```bash
python3 -m tools.object_interface --vocabulary config/document_interface.json requirements docs/research/object_framework/document.json docs/research/object_framework/document_requirements.json --bindings docs/research/object_framework/document_bindings.json > /tmp/nomi-document-conditions.json
python3 -m tools.object_replay config/document_interface.json docs/research/object_framework/document.json /tmp/nomi-document-conditions.json --requirements docs/research/object_framework/document_requirements.json --bindings docs/research/object_framework/document_bindings.json
```

## Reuse A Workflow With Several Outputs

The [workflow protocol](../../tools/object_interface/workflows.py) composes a
checked graph template through explicit reference arguments. A template declares
every abstract input exactly once, exposes its selected outputs under public
port names, and optionally carries a checked requirement artifact. It contains
no engine, callback or supplied input values. This is library/artifact reuse,
not Nomi function/module admission or a new executable instruction.

The [example template](../research/object_framework/workflow.json) exposes a
square and greeting while retaining a passive document intermediate:

```python
from tools.object_interface import Graph, Workflow, load_document
from tools.object_interface.examples import lab_vocabulary, python_backend

vocabulary = lab_vocabulary()
base = Graph.from_document(
    load_document("docs/research/object_framework/composition.json"), vocabulary,
)
base = base.compose("other_quantity", "exact.input", {})
base = base.compose("other_name", "text.input", {})
workflow = Workflow.from_document(
    load_document("docs/research/object_framework/workflow.json"), vocabulary,
)
first = workflow.compose(base, "first", {
    "quantity": base.ref("quantity"), "name": base.ref("name"),
})
second = workflow.compose(first, "second", {
    "quantity": first.graph.ref("other_quantity"),
    "name": first.graph.ref("other_name"),
})
outputs = [
    second.graph.ref("first.squared"), second.graph.ref("first.published"),
    second.outputs["square"], second.outputs["greeting"],
]
compiled = second.compile(python_backend(vocabulary), outputs)
result = compiled.bind({
    "quantity": 3, "name": "Ada", "other_quantity": 4, "other_name": "Bo",
}).execute()
assert result.get(second.outputs["square"]) == 16
assert result.get(second.outputs["greeting"]) == "Hello, Bo"
```

The first instance also returns 9 and `"Hello, Ada"`. Composition substitutes
only typed reference ports, including ordered repeated ports; strings inside
literal attributes remain literal strings. Local intermediates and conditions
receive namespace-qualified IDs. No name collision, wrong nominal argument,
stale/foreign reference or aggregate-budget overflow mutates the original graph.
Explicitly passing the same input reference to two instances shares that input;
equal input types or names do not cause implicit sharing. Descriptions retain
distinct source identities even when their pure dependencies are shared.

Passing the previous **instance** carries its conditions forward to the new
graph context, merging them with the new namespaced conditions. Source owner,
revision and requirement context remain in component inspection; the combined
artifact has the explicit `nomi.workflow-composition` owner. Export ports are
traversed in canonical name order when adding selected graph outputs; JSON
record insertion order is not part of the interface. Existing receipts
are not reused under a changed context. `instance.compile(backend)` attaches
all carried conditions before binding and refuses a selection that omits a
required subject. Computed arguments do not become static evidence merely
because they are passed through a template.

`instance.document` exports the expanded graph, requirements and passive
inspection. Restore the first two through `Graph.from_document` and
`Requirements.from_document`. Independent consumers already replay those
expanded graphs and predicate receipts. They also now independently reconstruct
template substitution, nominal argument checks, output selection, namespace
collisions and carried conditions for the two pinned vocabularies. Supplying
the original base graph and workflow definitions is required; component
inspection cannot install new laws or substitute for authoring-intent review.
Extracting `instance.graph` explicitly exposes the raw graph interface, which
does not carry separate requirements; use the instance when preserving the
workflow's required contract. No automatic backend selection or required-policy
enforcement outside this convenience API is implied.

Export the previous example explicitly to replay its composition separately
from binding or realization:

```python
import json
from pathlib import Path

Path("/tmp/nomi-workflow-base.json").write_text(json.dumps(base.document))
Path("/tmp/nomi-workflow-instance.json").write_text(json.dumps(second.document))
```

```bash
python3 -m tools.object_replay config/object_interface.json /tmp/nomi-workflow-base.json /tmp/nomi-workflow-instance.json --workflow docs/research/object_framework/workflow.json
```

The result is `verified` with a `pending` condition verdict: expansion is
established, while input values remain absent. `--workflow` is repeatable for
distinct explicitly supplied definitions. This mode refuses binding/evidence
flags that belong to a different replay operation. Whole exported bundles also
respect the 1 MB artifact limit. No renderer or arithmetic callback runs.

## Limits And Next Discriminators

The lab permits 512 named objects, 512 expanded terms, graph/definition depth 64,
and 1 MB per artifact and retained execution values. The example numeric backend
refuses arithmetic operands/results exceeding 4096 bits. These are laboratory
capacities, not target-language number semantics. Cancellation is cooperative
between local operations; it cannot interrupt a running trusted callback.
No remote execution, resource scope or general scheduling is implemented.

| Next increment | Required evidence |
| --- | --- |
| Richer domain refinement protocol | Nested paths, cross-object relations, condition-only bindings and bounded v4 universal rules now run with independent replay. Nested/correlated quantification and domain proofs need further laws; assertions cannot become proof. |
| More useful object composition | Parameterized multi-output workflows preserve reference arguments, namespaced intermediates and carried conditions, with independent pinned substitution replay. Compare authoring/repair costs with inline composition before generalizing the interface. |
| Statistical computation adapter | Preserve observation domains, missingness, exact numeric theory and independent v1 replay while reusing the envelope and references. |
| Wider independent consumers | Arithmetic/text and documentary vocabularies now have separately pinned replay. Admit further vocabulary/refinement rules separately, with changed-definition and forged-claim refusals. |
| Additional realization profiles | Two local documentary algorithms have independent expected-value fixtures. A foreign or remote adapter still needs explicit conversion/capacity, cancellation and failure evidence. |
| User-facing integration | Ordinary Nomi library calls plus a clear inspector; source/type/diagnostic/runtime contracts before source admission. |

Keep this framework removable until these comparisons earn generalization.
It shares identity and composition machinery, while domain packages keep their
own algebras and execution obligations. Do not turn it into a replacement for
Nomi Core or require every ordinary eager value to become a deferred graph.
