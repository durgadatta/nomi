# Current Support And Growth

> Status: user-oriented summary of prototype support and the target direction.

[User guide](README.md) / Current support and growth

Nomi has working tools and examples, a target language, and research into larger
uses. These are at different stages. This page explains what those stages mean
for someone trying the language. Detailed decisions remain in their linked owners.

## Reading Status Labels

| Label | What it means for you |
| --- | --- |
| Runnable prototype | You can run the named example on its stated execution path. Syntax can still change. |
| Experimental or bounded | A feature works within specific limits; it is not a general solution for every program. |
| Target design | The intended behavior is documented, but the complete feature may not be implemented. |
| Open design or research | Alternatives still need comparison or evidence; no final behavior is promised. |
| Historical | The document describes an earlier state. Use current guides and receipts before acting on it. |

An accepted target decision and a green prototype test establish different
things. A design can be accepted while its implementation is incomplete; a
prototype can support syntax that the target has rejected.

## What Works Now

| Capability | Try it | Boundary |
| --- | --- | --- |
| Values, ordinary functions, choices, and loops | [Language Basics](language_basics.md) | Verified small examples; not the entire target type system. |
| Collection transformations and ordered accumulation | [Data pipeline](examples.md#recommended-examples) | Prototype callback ordering and explicit materialization. |
| JSON validation, field repair, and report encoding | [Getting Started](getting_started.md#validate-a-json-report) | Two built-in schemas, batch size 128, host-specific capacity limits. |
| Browser editing, cells, diagnostics, and source download | [Browser tools](tools.md#browser-playground) | Drafts are browser-local; the default and legacy routes expose different inspection features. |
| CLI execution and structured output | [CLI tools](tools.md#command-line) | Python 3.12+ and the package's dependencies. |
| Source facts and selected checks | [Checking](getting_started.md#check-a-program-without-running-it) | Limited scalar/direct-function analysis; not general interface inference. |
| Notebook execution and local editor support | [Notebook and editor tools](tools.md#jupyter-notebooks) | Optional setup; regex-based editor navigation and prototype syntax tours. |

Defined bounds are not measured production-capacity guarantees. The report can
refuse oversized, overly complex, or unsupported numeric inputs; a capped error
list is marked incomplete. The [report walkthrough](getting_started.md#validate-a-json-report)
explains how to read its outcome, and the receipt linked there separates limits
from measured host behavior.

### Execution paths

The browser support above refers to the current local checkout. The October 10
published-site audit found an older nine-sample deployment without the new
calculation/report workflows and result views. Local conformance checks do not
establish what is deployed; see the [readiness audit](../orientation/project_roadmap.md#user-facing-readiness-audit).

The CLI and Jupyter use the Python-hosted prototype. The default browser uses a
Rust/WASM parser and JavaScript runtime. An optional legacy browser route runs
the Python prototype through Pyodide. These paths do not support every feature
equally. Having a Rust parser does not mean programs compile to native Rust-speed
executables.

The developer test modes `python`, `nomi`, and `reduced` are implementation
variants. They are not beginner/strict language levels. The current checker
offers independent `known-types` and `pure` requirements; broader checking
policies remain design work.

## Prototype And Target Differences

This table helps explain why a runnable sample can differ from a design example.
It is not a complete syntax migration guide.

| Area | Current prototype examples | Intended target |
| --- | --- | --- |
| Names and updates | Python-compatible assignment and rebinding remain on supported paths. | Ordinary names are immutable; `var` and `set` make mutation explicit. |
| Boolean and absent literals | Older examples use `True`, `False`, and `None`. | The target spells these `true`, `false`, and `none`; `()` represents Unit. |
| Functions | `func` works; older samples also use equation definitions and hole lambdas. | One named `func` form and explicit anonymous functions; equation and hole forms are rejected. |
| Collection calls | The beginner examples use callback-first `map`/`filter` and `list(...)`. | The target collection family is data-first with distinct strict, streaming, and table types. |
| Data validation | The report uses structural outcome maps and two manual schemas. | Owned immutable `data`, explicit typed decoding, and `Result` outcomes. |
| Pattern choice | Older samples have additional pattern shortcuts and match spellings. | A single structural `match` contract, with transactional captures and coverage checks. |
| Resources and concurrency | Historical samples explore block calls, `yield`, and host behavior. | Resource scopes and structured tasks have separate lifetime and failure contracts. |

See [Syntax](../design/syntax.md), [Semantics](../design/semantics.md), and
[Decisions](../design/decisions.md) for the actual target rules. Use the
[example catalog](examples.md#older-experimental-samples) to recognize the
experimental forms you may encounter.

### Text compatibility

Prototype `strip()` uses a Python-compatible whitespace set across hosted,
Python Core, and browser engines. It includes whitespace beyond ASCII and
preserves a byte-order-mark character. An optional text argument supplies a
set of characters to remove at the two ends; `None` selects whitespace.
Wrong argument types or extra arguments fail. This is a bounded prototype
library contract; target Unicode trimming remains a separate library decision.

Literal Unicode text is usually the clearest spelling. The current prototype
also decodes `\n`, `\r`, `\t`, `\a`, `\b`, `\f`, `\v`, escaped quotes/backslashes,
two-digit `\x`, four-digit `\u`, eight-digit `\U`, and up to three octal digits
consistently on the tested routes. For example, `"\u00e9"` contains `é`.
Raw text such as `r"\n"` preserves the backslash. Unknown escapes preserve it
too, but the hosted parser warns; use raw text or an escaped backslash instead.

The browser refuses malformed numeric escapes, surrogate/out-of-range scalar
escapes, and named Unicode escapes such as `\N{...}`. Named escapes remain a
hosted-only compatibility form. The browser refuses bytes (`b"..."`) and
formatted (`f"..."`) literals, including raw-prefix combinations; join ordinary
text explicitly instead of using a formatted literal. Multiline edge cases
are outside this bounded text guarantee. These are prototype
compatibility spellings, not acceptance of a complete target escape grammar.
The [escape repair receipt](../orientation/project_roadmap.md#source-text-escape-repair--october-10)
records the tested scope and remaining work.

## The Guarantees Being Built

These concepts describe the intended growth path. They do not claim that the
prototype already enforces them in every program.

### Types and constraints

A type describes the kind of value a program expects. A constraint adds a rule
such as a nonnegative age. Local code should remain easy to write with inferred
information; public reusable boundaries should expose complete checked contracts.
A written annotation is a promise to verify, not proof by itself.

### Data boundaries

Received JSON is not automatically a trusted customer. An explicit decoder
checks shape, types, and constraints and reports errors at the original paths.
Only successful decoding creates the program's owned data. The bounded report
demonstrates that workflow; general derived decoders still need implementation.

### Absence and failure

`Option` represents a value that may be absent. `Result` represents an expected
success or failure. An unexpected broken invariant is a different failure story.
Keeping these separate should let readers see which cases a function handles
and which ones it passes to its caller. The beginner report currently uses maps
with an `ok` field rather than the complete target Option/Result system.

### Effects and authority

An **effect** describes an operation that touches the outside world, such as
console output or a database call. A **capability** is the actual handle that
allows such an operation. Describing an effect does not grant permission to use
it. A pure calculation has no world effects, but purity alone does not prove
termination or the absence of every runtime error.

### Progressive checking

Start by exploring. Add particular checks when the task needs them. Requiring
known types and requiring purity answer different questions; neither should
silently change how a successful program evaluates. Checking, runtime authority,
and engine choice remain separate. The accepted direction and remaining inference
work are in [Progressive Assurance](../design/semantics.md#progressive-assurance).

### Lifetimes and structured concurrency

Resource management defines how files or other handles are released on every
exit path. Structured concurrency gives related tasks an owner so they cannot
silently outlive their scope. Neither guarantee follows merely from an indented
block or a browser Stop button. The detailed target remains in
[Resources](../design/resource_lifetime.md) and the
[industrial concurrency model](../design/industrial.md#concurrency-and-operations).

## Delivery Direction

The first useful language centers on small scripts and trustworthy local reports.
The delivery order closes each journey's required contracts before promoting it:

1. Keep calculation and report/repair workflows useful across CLI and browser.
2. Implement portable scalar behavior, owned data, typed decoding, Result/match,
   and checked callback contracts for those workflows.
3. Reuse the same logic through checked local module interfaces.
4. Extend into network jobs, resources, structured tasks, packages, and domain
   libraries once their contracts and tools are ready.

Existing prototype capabilities may sit outside this first release scope.
Research explores data, AI/ML, configuration, documents, interfaces, and other
domains; that breadth is not a promise that a universal domain engine exists.
No release dates are assigned here. The
[delivery roadmap](../orientation/project_roadmap.md#delivery-order-and-dependencies)
owns priorities and evidence; [research](../research/README.md) owns alternatives.

## Distribution Status

The Python package is currently `0.1.0`, marked pre-alpha, and requires Python
3.12 or newer. The guides describe installation from a repository checkout.
The package can be built into a wheel; that does not establish a stable public
release, package-registry availability, or a supported operating-system matrix.

The wheel includes runtime assets and a default demo, but repository `samples/`,
the browser workbench, and these guides are checkout content. Commands that name
`samples/...` require the checkout or a separately saved copy of the example.
You can create your own `.nomi` file and run it with an installed `nomi` command.

Developer retrieval entry points also need an explicitly supplied source
configuration or the checkout's `config/rag_sources.json`; that default file is
not shipped in the wheel. They are not part of the beginner language workflow.

License selection, a declared support matrix, artifact identity, hosted release
parity, and rollback remain release gates. Their current evidence and
user-facing findings are tracked in the
[distribution-readiness audit](../orientation/project_roadmap.md#user-facing-readiness-audit).
