# Mathematica And Wolfram Language

> Status: comparative evidence, deepened 2026-10-10; no symbolic Nomi semantics accepted.

Mathematica supplies the notebook/product setting; this review studies selected
Wolfram Language mechanisms. Living official references were checked on October
10. No Wolfram kernel, notebook, benchmark or comparative user trial ran here.
The earlier expression-evaluation review is retained within this broader scope.

## Evaluation Is An Extensible Semantic System

Expressions have heads and elements. Evaluation can evaluate the head, evaluate
arguments, apply attributes and definitions, then restart when an expression
changes. Attributes such as `HoldAll`, `Listable` and `Orderless` influence
argument evaluation or structure. Immediate assignment evaluates its right-hand
side when defining it; delayed assignment retains it for later use.
[Evaluation sequence](https://reference.wolfram.com/language/tutorial/Evaluation.html.en).

This is more than a conventional function library. A new head can participate
in evaluation, matching and transformation. Nomi can learn from that integration
without making an ordinary call's evaluation depend on mutable symbol attributes.
The existing eager, once-before-binding call law conflicts with an ambient held
argument. A quotation boundary must preserve code before ordinary evaluation;
passing an already computed number cannot recover its expression or dependencies.

## Rules, Strategy And Assumptions

Delayed rules hold their right-hand side and evaluate it when the rule is used;
conditions evaluate a test to determine whether a rule/pattern applies. Thus
`x :> RandomReal[]` and a rule whose replacement was already computed have
different invocation semantics. Domain matching is coupled to evaluation, not
only to inert shape inspection.
[Delayed rules](https://reference.wolfram.com/language/ref/RuleDelayed.html),
[conditions](https://reference.wolfram.com/language/ref/Condition.html).

For Nomi, distinguish a pattern that binds structure, a pure guard, and an
explicit rewrite callback. If a replacement generates a fresh value or fails,
count each invocation and identify its authority. Do not transfer Wolfram's
pattern-driven definitions into the accepted ordinary function or match model
without a complete alternative law.

`ReplaceRepeated` repeatedly applies rules until the expression stops changing,
with an explicit maximum-iteration option. A stopped rewrite is not a proof of
a unique mathematical normal form.
[Repeated replacement](https://reference.wolfram.com/language/ref/ReplaceRepeated.html).

`Assuming` extends `$Assumptions` during an expression; functions supporting an
assumptions option can use that context. Assumptions are supplied premises, not
measurements or facts proved by the simplifier.
[Assuming](https://reference.wolfram.com/language/ref/Assuming.html).

**Nomi hypothesis:** represent an expression, rule set, theory, strategy,
assumptions and budget explicitly. Return a transformed expression with qualified
status and provenance. Separate directed rewriting, equivalence exploration and
solving. An arithmetic identity over exact reals need not hold over IEEE values,
partial operations or effectful calls. A library or scoped tool remains a
candidate; this does not accept a universal expression type or quotation syntax.

## Binding And Local Context

`Module` creates fresh symbols for its locals; `Block` temporarily localizes
symbol values. These solve different scoping problems.
[Module](https://reference.wolfram.com/language/ref/Module.html),
[Block](https://reference.wolfram.com/language/ref/Block.html).

**Nomi implication:** an expression variable needs binding identity, not only
text. Substitution must distinguish a free symbol from a same-named bound one.
Freshening binders and changing a dynamic assumption context are separate
operations. A scoped symbolic model may require its own explicit binder algebra;
it cannot silently replace ordinary lexical capture or inherit the notebook's
current global definitions as unrecorded dependencies.

## Exactness And Precision

`SetPrecision` can expose stored binary digits and then append zeros when raising
precision. It cannot recover an original exact input from an approximation.
[Precision adjustment](https://reference.wolfram.com/language/ref/SetPrecision.html).

**Nomi implication:** distinguish exact input, representation precision, numerical
error and measurement uncertainty. A larger precision annotation does not prove
more information. Assumptions, units and correlated observations belong to the
model and its evidence, rather than a single generic numeric confidence field.
The accepted exact Int subset does not settle Rational, Decimal or Float.

## What To Integrate And What It Costs

### Live Expressions Need Execution Ownership

`Dynamic` connects an expression's displayed value to updates and can connect
interactive edits to assignment or supplied update functions. Its options include
which symbol changes trigger refresh. This is language-level evidence for an
expression connected to an evolving interaction, rather than a static printed
result.
[Dynamic](https://reference.wolfram.com/language/ref/Dynamic.html).

**Nomi hypothesis:** compare explicit refresh with a declared reactive description.
Name dependency identity, reevaluation count, failure state, and whether refreshing
is allowed to perform effects. Editing a view, committing owned data, and
executing a calculation are separate transitions. Test a changed assumption,
a failing callback, and a refresh that attempts network access. This feeds the
existing dependency/time and interaction comparisons; it does not admit ambient
reactive bindings or a notebook execution policy.

### Integration Map

| Mechanism | Nomi candidate | Coherence obligation and cost |
| --- | --- | --- |
| Expressions as data | Explicit typed domain nodes; compare scoped quotation | Verbose constructors versus binding-aware, source-mapped quotation; never second-evaluate ordinary text |
| Rewriting | Ordinary transformation with declared theory and strategy | Termination, branch conditions, budget and retained side conditions; avoid a global mutable rule database |
| Assumption context | Explicit model input or scoped context value | Context must travel through caches, exports and explanations; extra plumbing buys reproducibility |
| Uniform symbolic/numeric work | A deliberate conversion/evaluation boundary | Preserve exactness and unsupported operations; ordinary runtime values and syntax trees are not interchangeable |
| Notebook exploration | Definitions and results tied to an explicit revision | Session convenience versus recoverable meaning after rerun/handoff; no automatic authority from a cell |

These are research judgments. The old recommendation to keep ordinary calls
eager stands until an explicit target revision chooses otherwise. Symbolic
convenience is a real cost of that choice, not evidence that Wolfram's model is
wrong for its audience.

## Discriminating Cases

| Supplied case | Required distinction | Alternatives to compare |
| --- | --- | --- |
| A definition refers to a changing value | Definition-time snapshot versus later lookup | Explicit capture; declared symbolic environment; held source |
| Substitute `y` for free `x` inside a binder named `y` | Avoid accidental capture; preserve free/bound identity | Freshened syntax tree versus an explicit domain binder |
| Rewrite `x/x` at `x = 0` | Cancellation needs a nonzero premise | Retain side condition; refuse; return qualified expression |
| Rules `a -> b` and `b -> a` | Budget exhaustion differs from normal form | Directed strategy; cycle detection; bounded equivalence search |
| Simplify `sqrt(x*x)` for a real negative `x` | The sign/domain assumption matters | `abs(x)` over reals; `x` only under a suitable premise |
| Raise a machine approximation's precision | Representation changes do not restore exact provenance | Preserve original exact token; explicit approximation; qualified precision change |

The cases are prepared expectations, not executed Wolfram results. Use
[metaprogramming](../features/metaprogramming.md),
[numerics](../features/numerics.md) and
[orthogonal symbolic models](../dsls/orthogonal_models.md) as owners. The
[maintainer guide](../synthesis_guide.md) joins them to the whole-language comparison.
