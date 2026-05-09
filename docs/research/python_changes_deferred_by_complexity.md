# Python Language Changes Deferred By Complexity

> Status: source note for Nomi design review.
>
> Purpose: collect Python language ideas that are widely attractive, borrowed
> from other languages, or repeatedly proposed, but have not become ordinary
> Python partly because the implementation, compatibility, readability, or
> teaching cost is high.

## Reading This Note

This is not a list of "Python mistakes." Python is conservative for good
reasons: compatibility, simple mental models, debuggability, tooling, and
implementation diversity matter. Many rejected or deferred ideas are good in
isolation but expensive when placed inside Python's existing semantics.

For Nomi, these ideas are useful because they show pressure points:

- places where Python users want more expression but hit statement/expression
  boundaries;
- places where dynamic behavior makes static guarantees difficult;
- places where useful abstraction conflicts with local reasoning;
- places where implementation mechanisms leak into language design.

Each section below follows this shape:

```text
idea -> why it is attractive -> why Python has not simply added it -> Nomi note
```

## 1. Statement-Local Namespaces And Trailing Definitions

Python has had proposals for writing a one-off helper function or class near
the expression that uses it, without polluting the surrounding namespace. Two
important examples are PEP 3150's `given` clause and PEP 403's `@in` clause.

Sketch:

```python
sorted_data = sorted(data, key=?.sort_key) given:
    def sort_key(item):
        return item.last_name, item.first_name
```

Why it is attractive:

- It keeps one-use helpers close to the use site.
- It avoids temporary helper names leaking into the surrounding scope.
- It can replace awkward patterns like "define helper, call it once, delete
  helper."
- It resembles ideas from Haskell `where`, ML `let`, Ruby blocks, and local
  function forms in many languages.

Why Python has not simply added it:

- It introduces new local-scope rules.
- Forward references become visible in source before their definitions.
- `return`, `yield`, `break`, `continue`, `global`, and `nonlocal` need special
  rules inside the trailing block.
- Debugging and introspection get less direct because generated helper scopes
  are partly compiler-created.
- The feature competes with Python's preference for definitions before use.

Nomi note:

Nomi should study the need, not necessarily the syntax. The deeper primitive is
"local binding for a subexpression." If Nomi wants this, it should reduce to
ordinary binding, scope, and block rules rather than invent a special namespace
mechanism.

Sources:

- [PEP 3150 - Statement local namespaces](https://peps.python.org/pep-3150/)
- [PEP 403 - General purpose decorator clause](https://peps.python.org/pep-0403/)

## 2. User-Defined Block Control

Python adopted `with` as a narrow, successful form of block control. Earlier
and broader proposals, especially PEP 340, explored anonymous block statements
where generators could drive caller-side blocks more directly.

Sketch:

```python
block retry(3):
    do_unreliable_work()
```

or in Nomi-like form:

```python
retry(3):
    do_unreliable_work()
```

Why it is attractive:

- It lets libraries define readable control policies: retry, transaction,
  lock, cleanup, tracing, temporary state, and similar patterns.
- It reduces repeated `try/finally` and callback-shaped code.
- It is close to Ruby blocks and to structured control abstractions in several
  languages.

Why Python has not simply added the broad version:

- Hidden control flow is hard to explain and debug.
- A block may complete normally, raise, break, continue, return, or yield; each
  path needs exact semantics.
- Generator resumption across block boundaries creates subtle lifetime and
  cleanup rules.
- Python chose the narrower context manager protocol because it gives strong
  value with a simpler execution model.

Nomi note:

This is already a central Nomi design pressure. If Nomi adopts block calls, the
block should be an explicit control value with a visible `yield` story,
diagnostics for resumption and cleanup, and tests for normal and exceptional
paths.

Sources:

- [PEP 340 - Anonymous Block Statements](https://peps.python.org/pep-0340/)
- [PEP 343 - The "with" Statement](https://peps.python.org/pep-0343/)
- [Nomi block calls feature](../features/block_calls_feature.md)

## 3. Overloadable Boolean Operators

Python lets objects overload many operators, but not `and`, `or`, and `not` in
the ordinary dunder-method way. PEP 335 proposed overloadable boolean
operators.

Sketch:

```python
(table.age > 18) and (table.country == "CA")
```

could build a query expression instead of immediately requiring a truth value.

Why it is attractive:

- NumPy, symbolic algebra, query builders, dataframes, and constraint systems
  naturally want boolean expressions to produce expression values.
- Users expect `and`, `or`, and `not` to be the readable boolean operators.
- The current workaround, `&`, `|`, and `~`, has different precedence and reads
  less naturally.

Why Python has not simply added it:

- `and` and `or` short-circuit; the right operand may not even be evaluated.
- A normal binary dunder method is not enough because the first operand must be
  asked whether the second operand is needed.
- PEP 335 required a two-phase protocol, bytecode changes, type slots, and C
  API support.
- It risks making basic boolean control flow less locally obvious.

Nomi note:

Nomi should be careful about overloading control operators. Constraints and
query expressions may need an expression-building mode, but ordinary truth
should remain simple. A good design might distinguish "predicate evaluation"
from "predicate construction" at a clear boundary.

Source:

- [PEP 335 - Overloadable Boolean Operators](https://peps.python.org/pep-0335/)

## 4. None-Aware Operators

PEP 505 proposed `??`, `??=`, `?.`, and `?[]` for common `None` handling.
Similar operators exist in C#, Swift, Kotlin, PHP, Dart, and JavaScript.

Sketch:

```python
name = user?.profile?.display_name ?? "anonymous"
config.timeout ??= default_timeout()
```

Why it is attractive:

- It removes noisy repeated `is None` checks.
- It handles "missing value" distinctly from false values like `0`, `""`, and
  `[]`.
- It is especially helpful when traversing partially populated data.

Why Python has not simply added it:

- It adds several new operators and precedence rules.
- It makes `None` even more special in the expression grammar.
- Assignment targets and chained trailers need careful semantics.
- Exception-aware alternatives risk hiding real bugs inside properties or
  indexing methods.
- The feature is small at each use site but broad in grammar, tooling, and
  teaching impact.

Nomi note:

Nomi should decide whether "missing" is a first-class value story. If so, a
coherent `Option`/`Maybe`/`Result` design may be better than a cluster of
operators. If Nomi keeps Python-like `None`, then safe traversal should be
considered only after data, pattern, and diagnostic stories are stable.

Source:

- [PEP 505 - None-aware operators](https://peps.python.org/pep-0505/)

## 5. Late-Bound Function Defaults

Python default arguments are evaluated when the function is defined. PEP 671
proposes syntax for defaults evaluated when the function is called.

Sketch:

```python
def bisect_right(a, x, lo=0, hi=>len(a)):
    ...

def add_item(item, target=>[]):
    target.append(item)
    return target
```

Why it is attractive:

- It removes the common `None` sentinel pattern.
- Defaults can depend on earlier parameters.
- It makes documentation and `help()` show the real logical default.
- It fixes a frequent beginner trap around mutable default values without
  changing existing Python behavior.

Why Python has not simply added it:

- It adds a second timing model to parameter defaults.
- Evaluation order must be defined for positional, keyword, early-bound, and
  late-bound defaults.
- Function objects and introspection need extra metadata.
- Implementations need support for detecting omitted arguments and evaluating
  defaults in function runtime scope.
- Tooling must understand the new parameter semantics.

Nomi note:

Nomi's binding model should make default timing explicit from the beginning.
If parameter constraints, defaults, and dependent defaults all reduce to
"argument mapping -> tentative binding -> default evaluation -> validation,"
then the feature may be simpler than it is for Python.

Source:

- [PEP 671 - Syntax for late-bound function argument defaults](https://peps.python.org/pep-0671/)

## 6. Lazy Imports

PEP 690 proposed transparent lazy imports: top-level imports would be deferred
until the imported module or name was first used.

Why it is attractive:

- It can improve CLI startup time and memory use.
- It can reduce import-cycle pain.
- It lets code keep normal top-level imports while paying only for actually
  used dependencies.

Why Python has not simply added it:

- Import side effects may occur later than readers expect.
- Import errors may move far from the import statement.
- Transparent placeholder objects must not leak into Python or C extension
  code.
- Debugging, tests, dynamic import paths, per-module opt-outs, and C API
  behavior all become more complicated.
- A global lazy-import switch changes the meaning of ordinary-looking code.

Nomi note:

Laziness is powerful when it is visible. Nomi could consider explicit lazy
module bindings or demand-loaded packages later, but transparent global
laziness would work against local reasoning unless diagnostics are excellent.

Source:

- [PEP 690 - Lazy Imports](https://peps.python.org/pep-0690/)

## 7. Runtime Contracts And Enforced Annotations

Python type annotations are intentionally not runtime checks. PEP 484 states
that type checking is expected to be performed by separate tools. Earlier,
PEP 316 proposed programming by contract using docstring-embedded preconditions,
postconditions, and invariants.

Sketch:

```python
def transfer(amount: int):
    """pre: amount > 0"""
    ...
```

or in Nomi-like form:

```python
func transfer(amount:(int, amount > 0)):
    ...
```

Why it is attractive:

- Contracts document behavior in executable form.
- Runtime checks catch boundary failures close to their cause.
- Preconditions, postconditions, and invariants make APIs more trustworthy.
- Nomi's current constrained binding work is part of this family.

Why Python has not simply added it:

- Python's annotations are used by many tools and libraries, not just type
  checkers.
- Runtime type checking has performance, import-time, and compatibility costs.
- Generics, protocols, unions, forward references, gradual `Any`, and runtime
  values do not map cleanly to simple `isinstance` checks.
- Contracts under inheritance are semantically subtle: preconditions may be
  weakened, postconditions strengthened, and invariants combined.
- Deciding when checks run, how they are disabled, and what exception explains
  failure is part of the language contract.

Nomi note:

This is one of Nomi's strongest openings. Nomi should not merely "turn on"
Python type hints. It should define binding constraints as a runtime semantic
primitive with clear failure diagnostics and predictable cost.

Sources:

- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [PEP 316 - Programming by Contract for Python](https://peps.python.org/pep-0316/)
- [Nomi binding constraints feature](../features/binding_constraints_feature.md)

## 8. Exhaustive Pattern Matching And Algebraic Data

Python added structural pattern matching in Python 3.10, but the broader PEP
622 design included static checker ideas such as exhaustiveness checks and
sealed classes for algebraic-data-like modeling. The final runtime language is
more conservative.

Sketch:

```python
match account:
    case Admin(name=name):
        ...
    case User(level=Level.PRO):
        ...
    # checker can report: some User levels not handled
```

Why it is attractive:

- It catches missing cases when modeling variants.
- It gives data-oriented code a direct shape language.
- It borrows proven ideas from ML, Haskell, Scala, Erlang, Rust, and Swift.
- It makes refactoring safer when new variants are added.

Why Python has not simply added the whole version:

- Python classes are open; new subclasses can appear dynamically.
- Runtime exhaustiveness checks would change the meaning of unmatched cases.
- Static exhaustiveness depends on type checker knowledge that the interpreter
  usually does not have.
- Pattern matching already introduced a new syntax category with subtle binding
  and side-effect rules.
- Sealed class semantics would be a significant new contract in a dynamic
  language.

Nomi note:

Nomi can do better here if `data` variants are closed by default or explicitly
closed. Exhaustive `match` is much easier when the language owns the variant
model instead of retrofitting it over arbitrary Python classes.

Sources:

- [PEP 622 - Structural Pattern Matching](https://peps.python.org/pep-0622/)
- [PEP 634 - Structural Pattern Matching: Specification](https://peps.python.org/pep-0634/)
- [PEP 635 - Structural Pattern Matching: Motivation and Rationale](https://peps.python.org/pep-0635/)

## 9. Multi-Statement Function Expressions

Python has `lambda`, but it is expression-only. Many programmers have wanted a
lightweight way to write inline functions with statements, annotations,
multiple steps, and better local binding.

Sketch:

```python
button.on_click(func event:
    log(event)
    return save(event.value)
)
```

Why it is attractive:

- It reduces boilerplate for callbacks and higher-order functions.
- It makes function values feel as first-class syntactically as they are
  semantically.
- It removes the artificial split between `def` and `lambda`.
- It appears in many forms across JavaScript, Ruby, Scala, Swift, Kotlin, and
  functional languages.

Why Python has not simply added it:

- Python's indentation-sensitive block syntax does not compose easily inside
  expressions.
- `return`, `yield`, `await`, annotations, decorators, and closure scope need
  precise rules.
- Readability can suffer when complex blocks are nested inside calls.
- Earlier attempts overlap with statement-local namespaces and trailing
  function proposals rather than having one obvious spelling.

Nomi note:

Nomi's arrow functions already address the small case. The larger case should
probably be handled by ordinary `func` definitions, block calls, or a carefully
bounded function literal. The key is not "make everything expression-shaped";
the key is "make local function values cheap without hiding control flow."

Sources:

- [PEP 3150 - Statement local namespaces](https://peps.python.org/pep-3150/)
- [PEP 403 - General purpose decorator clause](https://peps.python.org/pep-0403/)
- [Nomi delta on Python](../language/delta_on_python.md)

## Nomi Design Heuristics From These Cases

1. If a feature needs hidden compiler temporaries, make the user-facing
   reduction explainable.
2. If a feature changes evaluation timing, expose that timing in syntax or
   diagnostics.
3. If a feature depends on closed-world knowledge, give the language a real
   closed-world construct instead of guessing.
4. If a feature makes simple expressions more powerful, check whether it also
   makes ordinary debugging harder.
5. If Python rejected a feature for complexity, ask whether Nomi's smaller core
   makes the feature simpler, or whether the same complexity will reappear.
6. Prefer one semantic primitive over several special-case conveniences.
7. Keep syntax admission tied to reduction, diagnostics, and tests.

## Highest-Value Ideas For Nomi To Revisit

These seem especially aligned with Nomi's direction:

- constrained binding and runtime contracts;
- block calls as explicit control values;
- late-bound defaults as part of argument binding;
- closed data variants with exhaustive matching;
- local helper bindings that do not leak names.

These should stay later-stage research:

- transparent lazy imports;
- overloadable boolean control operators;
- broad safe-navigation syntax before the data/missing-value model is settled;
- general multi-statement expression blocks without a clear block/value story.
