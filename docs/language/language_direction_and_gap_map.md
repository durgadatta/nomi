# Language Direction And Gap Map

> Status: active steering note.
>
> Scope: documentation-only. This document connects Nomi's long-horizon
> ambition, active language foundation, convenience research, and adoption
> risks. It is not an implementation plan.

## Purpose

Nomi's docs already contain a strong semantic spine:

- [Language Foundation](language_foundation.md) defines the current core.
- [Language Specification](language_spec.md) gives a concrete draft.
- [Language Coherence Model](../research/language_coherence_model.md) protects
  against feature collection.
- [Language Family Coverage Map](../research/language_family_coverage_map.md)
  tracks source-language traditions, under-covered dimensions, and follow-up
  research priorities.
- [Syntax Synthesis Matrix](../convenience/syntax_synthesis_matrix.md) groups
  cross-language syntax ideas by normal form.
- [Language Degrees Of Freedom](language_degrees_of_freedom.md) classifies how
  strict, flexible, library-led, or fenced each design area should be.
- [Target Program Fixtures](target_program_fixtures.md) keeps design pressure
  grounded in ordinary tasks before implementation.
- [Target Language Tour](target_language_tour.md) gives a larger aspirational
  program for testing whether Nomi syntax composes into one memorable whole.
- [Forward Implementation Plan](forward_implementation_plan.md) turns the
  design spine into staged work packages, gates, caveats, and open questions.
- [Cognitive Language Vision](../research/cognitive_language_vision.md) names
  the larger aspiration.

The missing layer is an adoption-oriented steering map:

```text
If Nomi wants Python-level everyday usefulness,
what gaps must be filled without losing coherence?
```

This document answers that question at the design level. It does not try to
make Nomi popular by adding more syntax. It asks what a broadly loved language
must make easy, predictable, teachable, and trustworthy.

## Product Aspiration

Nomi should aim to be a language that many ordinary programmers can use for
daily work, while also giving advanced programmers a cleaner path to modeling,
constraints, data transformation, symbolic structure, and explanation.

The target is not "Python, but with every good feature added." The target is:

```text
Python's approachability
+ ML-style data and pattern clarity
+ Ruby/Julia-style block expressiveness
+ SQL/APL-style whole-data thinking
+ CUE/Pydantic-style boundary confidence
+ Racket/Darklang-style explanation pressure
= one coherent everyday language
```

The central product promise:

```text
small script -> clear script -> checked data -> reusable model
-> readable transformation -> explainable result
```

If a design choice does not help that path, it should be delayed, demoted to a
library, or kept as research.

## Mainstream Adoption Lessons

The docs already acknowledge that semantic elegance is not enough. A language
used by many people needs:

- a tiny first lesson;
- obvious formatting;
- helpful errors;
- excellent documentation;
- a strong standard library story;
- interop with existing ecosystems;
- a package and tooling path;
- examples for boring real tasks;
- stable conventions that make code look familiar after time away.

Nomi should therefore treat adoption as a design surface, not a marketing
afterthought. Syntax pleasantness matters, but it is only one part of the
larger usability system.

## User Groups To Design For

Nomi should not begin with expert language designers as the primary user. The
first complete language should serve these groups in order:

| User | What they need | Nomi pressure |
| --- | --- | --- |
| Python-like beginner | Readable scripts, simple functions, useful errors | Keep the first lesson small and avoid theory-first surfaces. |
| Working scripter | Files, CLI args, JSON, CSV, env vars, HTTP, subprocesses | Make data boundaries and diagnostics excellent. |
| Notebook/data user | Pipelines, tables, charts, inspectable intermediate values | Make flow and explanation first-class. |
| App/API developer | Request validation, domain data, expected failures | Make `data`, `decode`, `Result`, and match coherent. |
| Library author | Blocks, policies, examples, docs, stable call conventions | Make block calls powerful but inspectable. |
| Language explorer | symbolic forms, effects, scoped notation, rewrites | Fence advanced power behind explicit boundaries. |
| AI-assisted programmer | clear expansions, traceable semantics, design fixtures | Make syntax explainable and machine-checkable. |

The beginner path and the expert path should not be separate languages. The
expert path should be a layered extension of the same normal forms.

## Gap Map

The table below names the most important design gaps. These are not all
implementation tasks. Many are documentation, teaching, standard library, or
design-decision gaps.

| Gap | Why it matters | Existing anchors | Needed next artifact |
| --- | --- | --- | --- |
| First-hour learning path | Broad adoption starts with the first useful program. | `README.md`, `language_foundation.md` | A tiny "first hour of Nomi" teaching note with only values, bindings, functions, calls, and diagnostics. |
| Standard library shape | Python succeeded partly because ordinary tasks are immediately available. | `language_spec.md` prelude section | A prelude/standard library design note: files, paths, text, JSON, CSV, HTTP, time, process, tables, tests. |
| Data boundary doctrine | Scripts and services spend much of their life cleaning external input. | `binding_constraints_feature.md`, `syntax_synthesis_matrix.md` | A focused `data_decode_boundary` feature spec covering provenance, defaults, optional fields, redaction, and source paths. |
| Failure taxonomy | `none`, `Err`, exceptions, failed constraints, and pattern failure must not blur. | `error_handling.md`, `null_handling.md`, `language_spec.md` | A focused result/failure design note with examples across parsing, IO, validation, and API boundaries. |
| Explanation model | Helpful diagnostics are a core language feature, not tooling garnish. | `language_foundation.md`, `meta_testing.md` | A diagnostic/trace/explain spec covering binding, match, pipeline, decode, block, and examples. |
| Collection/table vocabulary | Most real programs transform collections, records, rows, and tables. | `structured_collections_query_language.md`, `collections.md` | A vocabulary spec for `where`, `select`, `derive`, `group`, `join`, `sort`, `window`, `fold`, and plan values. |
| Module/package story | A language cannot scale if names, files, exports, and packages are vague. | `modules_imports.md`, `language_spec.md` | A modules/packages note focused on simple imports, explicit exports, package layout, and Python interop. |
| Interop and migration | Nomi's first ecosystem advantage is the Python world. | `delta_on_python.md`, `artifacts_and_usage.md` | A migration/interop note: what stays Python-like, where Nomi departs, how libraries are called, and where boundaries are visible. |
| Mutability and state | Everyday code mutates files, objects, caches, and collections. | `tractable_sophistication.md`, `language_coherence_model.md` | A state model note: rebinding, mutable containers, data updates, transactions, and future lenses/projections. |
| Effects and capabilities | File/network/time/randomness must be usable before effect theory is introduced. | `cognitive_language_vision.md`, `language_spec.md` | A practical capability note that starts with `world`, `using`, `transaction`, and traceable authority. |
| Concurrency posture | Async, tasks, cancellation, and streams can distort a first language. | `concurrency.md`, `block_calls_feature.md` | A staged concurrency note: keep first core synchronous, then add structured concurrency through block policies. |
| Syntax taste guide | Pleasant syntax requires consistent taste, not just local cleverness. | `syntax_synthesis_matrix.md` | A short style/taste guide for keyword choice, punctuation, placeholders, block shape, and examples. |
| Proposal process | Future ideas need a disciplined path from research to spec. | `ai_collaboration.md`, `implementation_todos.md` | `design_proposal_template.md`: need, precedents, normal form, rejected alternatives, examples, diagnostics. |
| Design fixtures | Future syntax needs examples before implementation pressure distorts it. | `target_program_fixtures.md`, `target_language_tour.md` | Keep expanding fixture coverage, then use the tour as the coherence check for syntax proposals. |

## Caveats

### No Language Is Best For Everyone

"Best language" is not a universal property. Systems programming, proof-heavy
work, hard real-time control, shader code, browser scripting, and large legacy
enterprise systems make different tradeoffs. Nomi's plausible ambition is more
specific:

```text
be one of the best languages for everyday high-level programming
where readability, data boundaries, transformation, and explanation matter.
```

This is still a large ambition. It is also more honest than claiming universal
dominance.

### Pleasant Syntax Can Become Noise

Every additional surface form has a memory cost. Syntax is worth adding only
when it makes a recurring operation easier to read and explains itself through
normal-form expansion.

The danger signs are:

- two ways to declare field-like things;
- several placeholders with different scopes;
- one operator that sometimes means absence, sometimes error, sometimes early
  return;
- query syntax that hides ordinary flow;
- macros or notation that ordinary tools cannot expand.

### Adoption Is Mostly Boring Work

Language design taste is not enough. A broadly used language needs boring
strength: installers, errors, docs, examples, package conventions, editor
support, formatting, testing, and interop. These are part of the language
experience even when they are not part of the grammar.

### Advanced Ideas Need Fences

Symbolic rewrite, effect handlers, scoped notation, dense array notation,
regions, capabilities, and type-level programming are all valuable. They should
enter only through visible boundaries:

- `quote:` for code-as-data;
- block policies for control and effects;
- plan values for query/backend lowering;
- explicit capability/world values for authority;
- scoped `use` for notation.

The first everyday layer must remain learnable without them.

## Deduplication Decisions To Preserve

These decisions should be treated as active design constraints until a later
doc explicitly replaces them:

- `data` is for owned program values; external structures cross through
  `Data.decode(...)` or patterns.
- `shape`, if ever admitted, means named structural pattern/constraint, not a
  second data declaration.
- `if-let`, `guard-let`, destructuring, and match cases share pattern plus
  tentative binding semantics.
- `?.` and `??` are absence-only. `Result` handles expected failure.
- Pipeline applies a value now. Composition builds a function for later.
- Query/table syntax must reduce to the same flow vocabulary as ordinary
  collection transforms.
- Blocks are caller-side code attached to calls. Resource, retry, transaction,
  trace, fixture, and structured concurrency policies should reuse that model.
- Examples, tests, traces, decode errors, and query plans are one explanation
  family.
- Dense array notation, global macros, effect handlers, and custom syntax are
  future layers, not the first everyday surface.

## Directional Design Sequence

For a design-only pass, the most valuable next sequence is:

1. **Everyday tasks**: keep refining target programs for files, JSON, CSV,
   CLI, HTTP, config, notebook transforms, and small APIs.
2. **Boundary confidence**: specify decode, constraints, provenance, defaults,
   redaction, and failure messages.
3. **Failure clarity**: specify absence, result, exceptions, pattern failure,
   constraint failure, and propagation.
4. **Readable flow**: specify collection/table verbs and how `explain` shows
   pipeline stages.
5. **Block policies**: specify `using`, `retry`, `transaction`, `trace`, and
   `test` as one block-call family.
6. **Teaching surface**: define the first-hour path and a style guide for
   pleasant code.
7. **Advanced fences**: document quote/rewrite, capabilities, scoped notation,
   and array/rank ideas as future layers with clear boundaries.

This sequence keeps aspiration alive while making the next documents concrete.

## Target Everyday Shape

The docs should converge on examples that look like ordinary work, not language
feature demos:

```nomi
data ImportConfig:
    input:Path, exists(input)
    min_age:int, min_age >= 0 = 13

data Person:
    name:str, len(name) > 0
    email:str, contains(email, "@")
    age:int, age >= 0

func load_people(raw_config:dict) -> Result[list[Person], Error]:
    config = ImportConfig.decode(raw_config)

    trace "load people":
        rows =
            read_csv(config.input)
            |> where(_.age >= config.min_age)
            |> select(Person.decode)

        match collect_results(rows):
            case Ok(people):
                return Ok(people)
            case Err(error):
                return Err(explain(error))
```

This example is useful because it combines the major pillars without needing
exotic notation:

- `data` names owned values;
- `decode` marks external boundaries;
- constraints make assumptions executable;
- `|>` keeps transformation readable;
- `Result` and `match` keep expected failure visible;
- `trace` and `explain` keep the runtime inspectable.

## Documentation Cleanup Priorities

To improve coherence across all docs:

- Keep `docs/language/` as the decision surface.
- Keep `docs/features/` as focused specs for one pillar at a time.
- Keep `docs/convenience/` as comparative syntax research reduced to normal
  forms.
- Keep `docs/research/` as source notes and synthesis, not competing specs.
- Keep `docs/notes/` as philosophical context and risk framing.
- Treat `docs/drafts/` as scratch/reference unless a task points there.

When a research note becomes canonical, move the decision into
`docs/language/` or `docs/features/`, then link back to the source note rather
than duplicating the whole argument.

## Open Questions

These are the highest-leverage unanswered questions:

1. What is the smallest first-hour Nomi lesson that feels better than Python
   without requiring theory?
2. What belongs in the standard prelude versus ordinary libraries?
3. How should decode diagnostics represent source paths across JSON, CSV,
   config files, environment variables, CLI args, and HTTP requests?
4. What exact distinction should users learn between `none`, `Err`,
   exceptions, failed constraints, and pattern non-match?
5. Can table/query work stay as pipeline verbs and plan values, or does it need
   scoped row/group syntax?
6. What mutation model keeps everyday code easy without undermining local
   reasoning?
7. What is the minimum capability/effect story that helps users without making
   daily code academic?
8. How should Nomi explain desugaring to both humans and AI tools?
9. What syntax should be permanently refused because it creates a second mental
   model?
10. What examples would make a Python programmer feel the language is worth
    trying in one sitting?

## Success Standard

Nomi is moving in the right direction if a medium-sized program lets a reader
answer:

```text
Where did this value come from?
What was checked?
What data model owns it now?
What branch or pattern was chosen?
What transformation stages ran?
What policy controls this block?
What failure kind happened?
What can the runtime explain?
```

The long-term ambition is large, but the daily test is small: the program
should feel easier to understand after it becomes more precise.
