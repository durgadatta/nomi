# Engine-Free Objects

> Status: designing framework, 2026-10-10. A bounded Python research implementation
> runs typed composition, inspection, closed definitions and explicit realization.
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
verification**. The existing statistical exact-law consumer remains a separate
independent checker for its own v1 theory.

The envelope supports nominal families with shallow codecs and parameter shapes.
It does not implement general parameterized types, predicate solving or Nomi's
full type system. Domain-specific structure stays in domain-owned contracts.
A model parameter record passing an inert shape check is still not a validated
model.

## Add A Domain Without Adding An Engine

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

## Limits And Next Discriminators

The lab permits 512 named objects, 512 expanded terms, graph/definition depth 64,
and 1 MB per artifact and retained execution values. The example numeric backend
refuses arithmetic operands/results exceeding 4096 bits. These are laboratory
capacities, not target-language number semantics. Cancellation is cooperative
between local operations; it cannot interrupt a running trusted callback.
No remote execution, resource scope or general scheduling is implemented.

| Next increment | Required evidence |
| --- | --- |
| Domain refinement protocol | One arithmetic and one non-numeric contract, including pending and rejected obligations; checkers cannot turn supplied assertions into proof. |
| More useful object composition | A small reusable parameterized workflow and a document specification; domain contracts survive inspection, serialization and rebinding. |
| Statistical computation adapter | Preserve observation domains, missingness, exact numeric theory and independent v1 replay while reusing the envelope and references. |
| Independent generic consumer | Reconstruct closed definitions, typing and context without importing this planner; reject altered definitions and forged claims. |
| Additional realization profiles | A second materially different implementation with explicit conversion/capacity refusal and independent value/error fixtures. |
| User-facing integration | Ordinary Nomi library calls plus a clear inspector; source/type/diagnostic/runtime contracts before source admission. |

Keep this framework removable until these comparisons earn generalization.
It shares identity and composition machinery, while domain packages keep their
own algebras and execution obligations. Do not turn it into a replacement for
Nomi Core or require every ordinary eager value to become a deferred graph.
