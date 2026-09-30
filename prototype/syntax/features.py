"""Syntax feature manifest registry.

Each syntax feature declares its grammar, parse-tree transforms, desugar
passes, docs, and lifecycle status in one place.  The core registries
(grammar layer order, layer transforms, desugar pipeline) are derived from
this list, so adding a feature means adding one entry here plus the
implementation module — not editing 4 separate registries.

Feature order matters: it determines the order grammar layers are assembled
and desugar passes run.  Dependencies between passes (e.g. WhereClause
needs PiecewiseFunction to have already merged adjacent definitions) are
expressed through this order.

Target direction is independent docs-owned metadata for migration inspection.
It never selects grammar, lowering, desugar passes, or runtime coverage.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import PurePosixPath
from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from prototype.parser.nomi.desugar.base import BaseDesugarer


ALLOWED_LAYERS = ("L0", "L1", "L2", "L3", "L4", "L5", "L6", "L7")
SUGAR_LAYER = "L4"
DEFAULT_DESUGAR_PROFILE = "default"
REDUCED_DESUGAR_PROFILE = "reduced"
ALLOWED_DESUGAR_PROFILES = (DEFAULT_DESUGAR_PROFILE, REDUCED_DESUGAR_PROFILE)

SAMPLE_BLOCK = "samples/block.nomi"
SAMPLE_COLLECTIONS = "samples/collections.nomi"
SAMPLE_COMPREHENSIVE = "samples/comprehensive.nomi"
SAMPLE_CONSTRAINT = "samples/constraint.nomi"
SAMPLE_DEMO = "samples/demo.nomi"
SAMPLE_DEMO_TERSE = "samples/demo_terse.nomi"
SAMPLE_DEMO_VERBOSE = "samples/demo_verbose.nomi"
SAMPLE_OTHERS = "samples/others.nomi"


@dataclass(frozen=True)
class TargetDirection:
    """Docs-owned design direction, independent of prototype execution coverage."""

    disposition: str
    contract: str
    normal_form: str
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.disposition, str) or self.disposition not in {
            "retain",
            "rework",
            "retire",
            "open",
        }:
            raise ValueError(f"Unknown target disposition: {self.disposition!r}")
        for name in ("contract", "normal_form", "reason"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Target direction {name} must be non-empty text")
        path = PurePosixPath(self.contract.split("#", 1)[0])
        if (
            not path.is_relative_to("docs/design")
            or ".." in path.parts
            or path.suffix != ".md"
        ):
            raise ValueError(
                "Target direction contract must be a docs/design Markdown path"
            )


@dataclass(frozen=True)
class SyntaxFeature:
    """A named language capability with its implementation pieces.

    Each feature can contribute grammar fragments, parse-tree transforms,
    lowering mixins, and/or AST-level desugar passes.  Every contribution is
    optional — a feature that only needs a desugar pass (like ``assert``
    desugaring) does not need to declare grammar layers.
    """

    name: str
    description: str
    status: str = "implemented"
    layer: str = ""
    semantic_forms: tuple[str, ...] = ()
    reduces_to: tuple[str, ...] = ()
    runtime_hooks_allowed: str = "none"
    backend_requirements: tuple[str, ...] = ()
    docs: tuple[str, ...] = ()
    tests: tuple[str, ...] = ()
    sample_files: tuple[str, ...] = ()
    soft_keywords: tuple[str, ...] = ()
    coverage: FeatureCapabilityAxes | None = None
    grammar_layers: tuple[str, ...] = ()
    layer_transforms: tuple = ()
    lowering_mixins: tuple[str, ...] = ()
    desugar_passes: tuple = ()
    desugar_profiles: tuple[str, ...] = ()
    target_direction: TargetDirection | None = None

    # Lifecycle statuses:
    #   implemented      — runs by default, tested
    #   prototype-ready  — runs behind a feature flag, tests present
    #   design-needed    — semantics not settled, parse-only or hidden
    #   research-only    — aspirational, may not parse yet
    #   rejected-for-now — kept for reference, not active


@dataclass(frozen=True)
class FeatureCapabilityAxes:
    """Current implementation exposure for one feature."""

    target_only: bool = False
    parse: bool = False
    lower: bool = False
    run: bool = False
    reduce: bool = False
    explain: bool = False
    docs: bool = False
    tests: bool = False
    samples: bool = False
    web: bool = False
    notebook: bool = False


def implemented_coverage(
    *,
    docs: bool = False,
    tests: bool = False,
    samples: bool = False,
    web: bool = False,
    notebook: bool = False,
) -> FeatureCapabilityAxes:
    """Return explicit coverage for implemented current-runtime features."""
    return FeatureCapabilityAxes(
        parse=True,
        lower=True,
        run=True,
        reduce=True,
        docs=docs,
        tests=tests,
        samples=samples,
        web=web,
        notebook=notebook,
    )


def target_only_coverage(*, docs: bool = False) -> FeatureCapabilityAxes:
    """Return explicit coverage for docs-owned target/design feature packets."""
    return FeatureCapabilityAxes(target_only=True, docs=docs)


def _retire_target(normal_form: str, reason: str) -> TargetDirection:
    return TargetDirection(
        disposition="retire",
        contract="docs/design/decisions.md#syntax-simplification-decisions",
        normal_form=normal_form,
        reason=reason,
    )


# ── expression-precedence ────────────────────────────────────────────
# Not a user-visible "feature" but a parse-tree transform that the
# ExpressionLayer applies.  Registered as a feature so the layer-transform
# registry can be derived from this list.

_expression_precedence = SyntaxFeature(
    name="expression-precedence",
    description="Reorganise flat bin_expr parse tree into correct precedence/associativity",
    layer="L3",
    semantic_forms=("expression",),
    reduces_to=("precedence-normalized-expression-tree",),
    docs=("docs/design/industrial.md",),
    layer_transforms=(
        # Lazy-imported in assemble.py to break circular dependency.
        "prototype.parser.nomi.desugar.parse_tree_precedence.ExpressionLayer",
    ),
)


# ── piecewise-functions ──────────────────────────────────────────────

_piecewise_functions = SyntaxFeature(
    name="piecewise-functions",
    description="Haskell-style f(p)=e piecewise function definitions via match dispatch",
    layer=SUGAR_LAYER,
    semantic_forms=("function", "pattern", "match"),
    reduces_to=("canonical-function", "match-dispatch"),
    docs=("docs/design/decisions.md",),
    tests=("prototype/tests/features/functions/test_equations_runtime.py",),
    sample_files=(SAMPLE_DEMO, SAMPLE_DEMO_TERSE, SAMPLE_DEMO_VERBOSE, SAMPLE_COMPREHENSIVE),
    coverage=implemented_coverage(docs=True, tests=True),
    desugar_passes=("prototype.parser.nomi.desugar.piecewise.PiecewiseFunction",),
    desugar_profiles=(DEFAULT_DESUGAR_PROFILE, REDUCED_DESUGAR_PROFILE),
    target_direction=_retire_target(
        "func with exhaustive match",
        "Equation dispatch duplicates canonical function and choice forms.",
    ),
)


# ── where-clauses ────────────────────────────────────────────────────

_where_clauses = SyntaxFeature(
    name="where-clauses",
    description="Postfix where: blocks that bind local definitions after an expression",
    layer=SUGAR_LAYER,
    semantic_forms=("binding", "function"),
    reduces_to=("local-binding-rewrite",),
    docs=("docs/design/decisions.md",),
    tests=("prototype/tests/features/functions/test_where_runtime.py",),
    sample_files=(
        SAMPLE_DEMO,
        SAMPLE_DEMO_TERSE,
        SAMPLE_DEMO_VERBOSE,
        SAMPLE_OTHERS,
        "prototype/tests/data/sample_sources/interpreter/func_styles.nomi",
        SAMPLE_COMPREHENSIVE,
    ),
    coverage=implemented_coverage(docs=True, tests=True),
    desugar_passes=("prototype.parser.nomi.desugar.where_clause.WhereClause",),
    desugar_profiles=(DEFAULT_DESUGAR_PROFILE, REDUCED_DESUGAR_PROFILE),
    target_direction=_retire_target(
        "local binding or local func",
        "Reserve where for constraints, not postfix helper definitions.",
    ),
)


# ── underscore-lambdas ───────────────────────────────────────────────

_underscore_lambdas = SyntaxFeature(
    name="underscore-lambdas",
    description="Scala-style _.attr and _ + 1 anonymous function shorthand",
    layer=SUGAR_LAYER,
    semantic_forms=("function",),
    reduces_to=("canonical-function-literal",),
    docs=("docs/design/decisions.md",),
    tests=("prototype/tests/features/functions/test_holes_runtime.py",),
    sample_files=(SAMPLE_DEMO, SAMPLE_DEMO_TERSE, SAMPLE_DEMO_VERBOSE, SAMPLE_COMPREHENSIVE),
    coverage=implemented_coverage(docs=True, tests=True),
    desugar_passes=("prototype.parser.nomi.desugar.underscore_lambda.UnderscoreLambda",),
    desugar_profiles=(DEFAULT_DESUGAR_PROFILE, REDUCED_DESUGAR_PROFILE),
    target_direction=_retire_target(
        "explicit (argument) => expression",
        "Underscore remains a pattern wildcard, never a generated parameter.",
    ),
)


# ── positional-holes ─────────────────────────────────────────────────

_positional_holes = SyntaxFeature(
    name="positional-holes",
    description="$1, $name positional hole syntax for implicit lambda parameters",
    layer=SUGAR_LAYER,
    semantic_forms=("function",),
    reduces_to=("canonical-function-literal",),
    docs=("docs/design/decisions.md",),
    tests=("prototype/tests/features/functions/test_holes_runtime.py",),
    sample_files=(SAMPLE_DEMO, SAMPLE_DEMO_VERBOSE, SAMPLE_OTHERS, SAMPLE_COMPREHENSIVE),
    coverage=implemented_coverage(docs=True, tests=True),
    desugar_passes=("prototype.parser.nomi.desugar.positional_hole.PositionalHole",),
    desugar_profiles=(DEFAULT_DESUGAR_PROFILE, REDUCED_DESUGAR_PROFILE),
    target_direction=_retire_target(
        "explicit (argument) => expression",
        "Positional/name holes hide callback inputs.",
    ),
)


# ── aug-assign-desugar ───────────────────────────────────────────────

_augassign = SyntaxFeature(
    name="aug-assign-desugar",
    target_direction=_retire_target(
        "set name = name + value",
        "Mutation is explicit and distinct from binding creation.",
    ),
    description="Desugar x += 1 into x = x + 1 in the AST",
    layer=SUGAR_LAYER,
    semantic_forms=("binding",),
    reduces_to=("assignment", "binary-operation"),
    desugar_passes=("prototype.parser.nomi.desugar.augassign.AugAssign",),
    desugar_profiles=(REDUCED_DESUGAR_PROFILE,),
)


# ── assert-desugar ───────────────────────────────────────────────────

_assert = SyntaxFeature(
    name="assert-desugar",
    description="Desugar assert cond into if not cond: raise AssertionError",
    layer=SUGAR_LAYER,
    semantic_forms=("diagnostic", "branch"),
    reduces_to=("branch", "raise"),
    desugar_passes=("prototype.parser.nomi.desugar.assert_.Assert",),
    desugar_profiles=(REDUCED_DESUGAR_PROFILE,),
)


# ── decorator-desugar ────────────────────────────────────────────────

_decorator = SyntaxFeature(
    name="decorator-desugar",
    target_direction=_retire_target(
        "ordinary declarations, protocols or explicit metadata",
        "Decorators do not silently define core semantics.",
    ),
    description="Desugar @d f() into f = d(f) after the function definition",
    layer=SUGAR_LAYER,
    semantic_forms=("function", "call", "binding"),
    reduces_to=("function-definition", "call", "binding"),
    desugar_passes=("prototype.parser.nomi.desugar.decorator.Decorator",),
    desugar_profiles=(REDUCED_DESUGAR_PROFILE,),
)


# ── pass-desugar ─────────────────────────────────────────────────────

_pass = SyntaxFeature(
    name="pass-desugar",
    description="Desugar pass into Expr(Constant(0))",
    layer=SUGAR_LAYER,
    semantic_forms=("statement",),
    reduces_to=("no-op-expression",),
    desugar_passes=("prototype.parser.nomi.desugar.pass_.Pass",),
    desugar_profiles=(REDUCED_DESUGAR_PROFILE,),
)


# ── with-desugar ─────────────────────────────────────────────────────

_with = SyntaxFeature(
    name="with-desugar",
    target_direction=TargetDirection(
        disposition="rework",
        contract="docs/design/semantics.md#resources-and-scope",
        normal_form="exactly-once acquisition, body and lexical cleanup",
        reason="Host try/exit conventions do not establish target completion semantics.",
    ),
    description="Desugar with ctx as x: B into try/except/else",
    layer=SUGAR_LAYER,
    semantic_forms=("resource-policy", "branch", "exception"),
    reduces_to=("try-finally-resource-protocol",),
    desugar_passes=("prototype.parser.nomi.desugar.with_.With",),
    desugar_profiles=(REDUCED_DESUGAR_PROFILE,),
)


# ── fstring-desugar ──────────────────────────────────────────────────

_fstring = SyntaxFeature(
    name="fstring-desugar",
    target_direction=TargetDirection(
        disposition="rework",
        contract="docs/design/syntax.md#literals",
        normal_form="ordinary quoted interpolation; raw text opts out",
        reason="Keep interpolation but remove the ordinary-text/f-string syntax split.",
    ),
    description="Desugar f'{x}' into string concatenation and format() calls",
    layer=SUGAR_LAYER,
    semantic_forms=("string", "call"),
    reduces_to=("string-concatenation", "format-call"),
    desugar_passes=("prototype.parser.nomi.desugar.fstring.FString",),
    desugar_profiles=(REDUCED_DESUGAR_PROFILE,),
)


# ── conditional-flow lowering ────────────────────────────────────────

_unless_lowering = SyntaxFeature(
    name="unless-lowering",
    target_direction=_retire_target(
        "if not condition",
        "One Bool choice form avoids a parallel conditional vocabulary.",
    ),
    description="Lower unless cond: body to if not cond: body",
    layer=SUGAR_LAYER,
    semantic_forms=("branch",),
    reduces_to=("branch", "boolean-negation"),
    docs=("docs/design/decisions.md",),
    tests=("prototype/tests/features/flow/test_conditionals_runtime.py",),
    sample_files=(SAMPLE_DEMO, SAMPLE_DEMO_TERSE, SAMPLE_DEMO_VERBOSE, SAMPLE_OTHERS, SAMPLE_COMPREHENSIVE),
    coverage=implemented_coverage(docs=True, tests=True),
)

_postfix_conditionals = SyntaxFeature(
    name="postfix-conditionals-lowering",
    target_direction=_retire_target(
        "inline or block if",
        "Conditional control stays in the canonical if form.",
    ),
    description="Lower flow statements with postfix if/unless guards to branches",
    layer=SUGAR_LAYER,
    semantic_forms=("branch", "flow"),
    reduces_to=("branch",),
    docs=("docs/design/decisions.md",),
    tests=("prototype/tests/features/flow/test_conditionals_runtime.py",),
    coverage=implemented_coverage(docs=True, tests=True),
)


# ── lowering mixins ───────────────────────────────────────────────────
# Each Lark grammar rule that needs AST lowering declares its mixin here.
# Order: mixins are composed left-to-right into FunctionsMixin, so later
# mixins can override earlier ones if needed.

_implicit_mul = SyntaxFeature(
    name="implicit-multiplication",
    target_direction=_retire_target(
        "left * right",
        "Ordinary modules use explicit multiplication; scoped notation remains separate.",
    ),
    description="Lower implicit multiplication (2x → 2 * x) in the Lark tree",
    layer=SUGAR_LAYER,
    semantic_forms=("expression",),
    reduces_to=("binary-multiplication",),
    docs=("docs/design/decisions.md",),
    tests=("prototype/tests/features/math/test_implicit_mul_runtime.py",),
    coverage=implemented_coverage(docs=True, tests=True),
    lowering_mixins=("prototype.parser.nomi.lowering.implicit_multiplication.ImplicitMulMixin",),
)

_type_alias = SyntaxFeature(
    name="type-alias-lowering",
    target_direction=TargetDirection(
        disposition="rework",
        contract="docs/design/syntax.md#data",
        normal_form="transparent type alias in the checked interface",
        reason="An AST assignment alone does not establish target type-alias metadata.",
    ),
    description="Lower type X = Y to an AST assignment",
    layer="L3",
    semantic_forms=("type-alias", "binding"),
    reduces_to=("binding",),
    docs=("docs/design/syntax.md",),
    tests=("prototype/tests/features/data/test_type_alias_runtime.py",),
    sample_files=(SAMPLE_DEMO, SAMPLE_CONSTRAINT, SAMPLE_COMPREHENSIVE),
    soft_keywords=("type",),
    coverage=implemented_coverage(docs=True, tests=True),
    lowering_mixins=("prototype.parser.nomi.lowering.type_alias.TypeAliasMixin",),
)

_range_expressions = SyntaxFeature(
    name="range-expressions",
    target_direction=_retire_target(
        "range(start, end, step=value)",
        "Range construction is library-owned; remainder punctuation stays in patterns.",
    ),
    description="Lower inclusive/exclusive range expressions and optional by-step to range()",
    layer=SUGAR_LAYER,
    semantic_forms=("collection",),
    reduces_to=("range-call",),
    docs=("docs/design/decisions.md",),
    tests=("prototype/tests/features/flow/test_range_runtime.py",),
    sample_files=(SAMPLE_DEMO, SAMPLE_DEMO_TERSE, SAMPLE_COLLECTIONS, SAMPLE_DEMO_VERBOSE, SAMPLE_COMPREHENSIVE),
    soft_keywords=("by",),
    coverage=implemented_coverage(docs=True, tests=True),
)

_if_let = SyntaxFeature(
    name="if-let-lowering",
    target_direction=_retire_target(
        "exhaustive match or loop plus match",
        "Refutable choice is not a binding shortcut.",
    ),
    description="Lower if pat = expr: body into a match statement",
    layer=SUGAR_LAYER,
    semantic_forms=("pattern", "match", "branch"),
    reduces_to=("match-statement",),
    docs=("docs/design/decisions.md",),
    sample_files=(SAMPLE_DEMO, SAMPLE_CONSTRAINT, SAMPLE_DEMO_VERBOSE, SAMPLE_COMPREHENSIVE),
    soft_keywords=("guard",),
    coverage=implemented_coverage(docs=True),
    lowering_mixins=("prototype.parser.nomi.lowering.if_let.IfLetMixin",),
)

_try_expr = SyntaxFeature(
    name="try-expr-lowering",
    target_direction=_retire_target(
        "Result, match and explicit propagation",
        "Expected failure does not borrow host exception-expression control.",
    ),
    description="Lower try body except E: handler into an IIFE",
    layer=SUGAR_LAYER,
    semantic_forms=("absence-result", "exception"),
    reduces_to=("try-statement", "function-call"),
    docs=("docs/design/decisions.md",),
    tests=("prototype/tests/features/absence_result/test_try_expr_runtime.py",),
    sample_files=(SAMPLE_DEMO, SAMPLE_DEMO_VERBOSE, SAMPLE_OTHERS, SAMPLE_COMPREHENSIVE),
    coverage=implemented_coverage(docs=True, tests=True),
    lowering_mixins=("prototype.parser.nomi.lowering.try_expr.TryExprMixin",),
)

_match_expr = SyntaxFeature(
    name="match-expr-lowering",
    target_direction=TargetDirection(
        disposition="rework",
        contract="docs/design/pattern_matching.md",
        normal_form="transactional exhaustive match without case keyword",
        reason="The host match/IIFE encoding is not the accepted Pattern Surface contract.",
    ),
    description="Lower match value: case pat => expr into an IIFE",
    layer=SUGAR_LAYER,
    semantic_forms=("match", "pattern"),
    reduces_to=("match-statement", "function-call"),
    docs=("docs/design/syntax.md",),
    sample_files=(SAMPLE_DEMO, SAMPLE_DEMO_TERSE, SAMPLE_CONSTRAINT, SAMPLE_DEMO_VERBOSE, SAMPLE_COMPREHENSIVE),
    soft_keywords=("match", "case"),
    coverage=implemented_coverage(docs=True),
    lowering_mixins=("prototype.parser.nomi.lowering.match_expr.MatchExprMixin",),
)

_where_clause_lowering = SyntaxFeature(
    name="where-clause-lowering",
    target_direction=_retire_target(
        "local binding or local func",
        "Reserve where for constraints, not postfix helper definitions.",
    ),
    description="Lower where: blocks by tagging _nomi_where_body for the desugar pass",
    layer=SUGAR_LAYER,
    semantic_forms=("binding", "function"),
    reduces_to=("local-binding-rewrite",),
    docs=("docs/design/decisions.md",),
    tests=("prototype/tests/features/functions/test_where_runtime.py",),
    sample_files=(
        SAMPLE_DEMO,
        SAMPLE_DEMO_TERSE,
        SAMPLE_DEMO_VERBOSE,
        SAMPLE_OTHERS,
        "prototype/tests/data/sample_sources/interpreter/func_styles.nomi",
        SAMPLE_COMPREHENSIVE,
    ),
    coverage=implemented_coverage(docs=True, tests=True),
    lowering_mixins=("prototype.parser.nomi.lowering.where_clause.WhereClauseMixin",),
)

_positional_hole_lowering = SyntaxFeature(
    name="positional-hole-lowering",
    target_direction=_retire_target(
        "explicit (argument) => expression",
        "Positional/name holes hide callback inputs.",
    ),
    description="Lower $1, $name hole syntax in expressions",
    layer=SUGAR_LAYER,
    semantic_forms=("function",),
    reduces_to=("canonical-function-literal",),
    docs=("docs/design/decisions.md",),
    tests=("prototype/tests/features/functions/test_holes_runtime.py",),
    sample_files=(SAMPLE_DEMO, SAMPLE_DEMO_VERBOSE, SAMPLE_OTHERS, SAMPLE_COMPREHENSIVE),
    coverage=implemented_coverage(docs=True, tests=True),
    lowering_mixins=("prototype.parser.nomi.lowering.positional_hole.PositionalHoleMixin",),
)

_compose_lowering = SyntaxFeature(
    name="compose-lowering",
    target_direction=_retire_target(
        "ordinary compose function or explicit lambda",
        "Composition does not need additional core operators.",
    ),
    description="Lower >>> and <<< composition operators",
    layer=SUGAR_LAYER,
    semantic_forms=("function", "call"),
    reduces_to=("canonical-function-literal", "nested-call"),
    docs=("docs/design/decisions.md",),
    tests=("prototype/tests/features/functions/test_composition_runtime.py",),
    sample_files=(SAMPLE_DEMO, SAMPLE_COLLECTIONS, SAMPLE_DEMO_VERBOSE, SAMPLE_OTHERS, SAMPLE_COMPREHENSIVE),
    coverage=implemented_coverage(docs=True, tests=True),
    lowering_mixins=("prototype.parser.nomi.lowering.compose.ComposeMixin",),
)

_defer_lowering = SyntaxFeature(
    name="defer-lowering",
    target_direction=TargetDirection(
        disposition="rework",
        contract="docs/design/semantics.md#resources-and-scope",
        normal_form="lexical LIFO cleanup on every exit",
        reason="Function-wide defer storage is not the target lexical scope contract.",
    ),
    description="Lower defer stmt to _nomi_defer attribute on statements",
    layer=SUGAR_LAYER,
    semantic_forms=("block", "resource-policy"),
    reduces_to=("function-body-cleanup-policy",),
    docs=("docs/design/syntax.md", "docs/design/semantics.md"),
    tests=("prototype/tests/features/block_calls/test_defer_runtime.py",),
    sample_files=(SAMPLE_DEMO, SAMPLE_DEMO_VERBOSE, SAMPLE_OTHERS, SAMPLE_COMPREHENSIVE),
    coverage=implemented_coverage(docs=True, tests=True),
    lowering_mixins=("prototype.parser.nomi.lowering.defer.DeferMixin",),
)

_func_equation_lowering = SyntaxFeature(
    name="func-equation-lowering",
    target_direction=_retire_target(
        "func; exhaustive match for alternatives",
        "Equation declarations duplicate the canonical named function form.",
    ),
    description="Lower f(p)=e equation definitions to FunctionDef",
    layer=SUGAR_LAYER,
    semantic_forms=("function", "pattern", "match"),
    reduces_to=("canonical-function", "match-dispatch"),
    docs=("docs/design/decisions.md",),
    tests=("prototype/tests/features/functions/test_equations_runtime.py",),
    sample_files=(SAMPLE_DEMO, SAMPLE_DEMO_TERSE, SAMPLE_DEMO_VERBOSE, SAMPLE_COMPREHENSIVE),
    coverage=implemented_coverage(docs=True, tests=True),
    lowering_mixins=("prototype.parser.nomi.lowering.func_equation.FuncEquationMixin",),
)

_section_lowering = SyntaxFeature(
    name="sections-lowering",
    target_direction=_retire_target(
        "explicit (argument) => expression",
        "Operator sections create another implicit callback form.",
    ),
    description="Lower (+2), (2*), (+) operator sections to lambdas",
    layer=SUGAR_LAYER,
    semantic_forms=("function",),
    reduces_to=("canonical-function-literal",),
    docs=("docs/design/decisions.md",),
    tests=("prototype/tests/features/functions/test_composition_runtime.py",),
    sample_files=(SAMPLE_DEMO, SAMPLE_DEMO_VERBOSE, SAMPLE_OTHERS, SAMPLE_COMPREHENSIVE),
    coverage=implemented_coverage(docs=True, tests=True),
    lowering_mixins=("prototype.parser.nomi.lowering.sections.SectionMixin",),
)

_func_expr_lowering = SyntaxFeature(
    name="func-expr-lowering",
    target_direction=TargetDirection(
        disposition="retain",
        contract="docs/design/syntax.md#functions-and-calls",
        normal_form="explicit (arguments) => expression",
        reason="Retain the explicit source form; typing/capture conformance remains open.",
    ),
    description="Lower (x, y) => expr arrow functions to FunctionDef",
    layer="L3",
    semantic_forms=("function",),
    reduces_to=("canonical-function-literal",),
    docs=("docs/design/syntax.md",),
    sample_files=(
        SAMPLE_DEMO,
        SAMPLE_DEMO_TERSE,
        SAMPLE_COLLECTIONS,
        SAMPLE_CONSTRAINT,
        SAMPLE_DEMO_VERBOSE,
        "prototype/tests/data/sample_sources/interpreter/functions.nomi",
        SAMPLE_COMPREHENSIVE,
    ),
    coverage=implemented_coverage(docs=True),
    lowering_mixins=("prototype.parser.nomi.lowering.func_expr.FuncExprMixin",),
)

_block_call_lowering = SyntaxFeature(
    name="block-call-lowering",
    target_direction=_retire_target(
        "with for resources; explicit function for other callbacks",
        "Universal block policy conflates return, retry, resource and task control.",
    ),
    description="Lower f(x): body block-call syntax to BlockCall surface node",
    layer="L3",
    semantic_forms=("block", "call"),
    reduces_to=("block-call",),
    runtime_hooks_allowed="semantic",
    docs=("docs/design/decisions.md",),
    tests=("prototype/tests/features/block_calls/test_defer_runtime.py",),
    sample_files=(
        SAMPLE_BLOCK,
        SAMPLE_DEMO,
        SAMPLE_DEMO_VERBOSE,
        "prototype/tests/data/sample_sources/interpreter/blocks.nomi",
        SAMPLE_COMPREHENSIVE,
    ),
    coverage=implemented_coverage(docs=True, tests=True),
    lowering_mixins=("prototype.parser.nomi.lowering.block_call.BlockCallMixin",),
)

_data_decl_lowering = SyntaxFeature(
    name="data-decl-lowering",
    target_direction=TargetDirection(
        disposition="rework",
        contract="docs/design/semantics.md#data",
        normal_form="immutable nominal product/variant data with checked construction",
        reason="Generated host classes do not establish the full target data contract.",
    ),
    description="Lower data Name: fields... to a ClassDef with __init__, __repr__, __eq__",
    layer="L3",
    semantic_forms=("data", "binding"),
    reduces_to=("data-constructor", "field-bindings"),
    runtime_hooks_allowed="backend-compat",
    docs=("docs/design/syntax.md", "docs/design/semantics.md"),
    tests=("prototype/tests/features/data/test_declarations_runtime.py",),
    sample_files=(SAMPLE_DEMO, SAMPLE_CONSTRAINT, SAMPLE_DEMO_VERBOSE, SAMPLE_COMPREHENSIVE),
    soft_keywords=("data",),
    coverage=implemented_coverage(docs=True, tests=True),
    lowering_mixins=("prototype.parser.nomi.lowering.data_decl.DataDeclMixin",),
)


# ── integration feature packets ──────────────────────────────────────

_pattern_surface_schema = SyntaxFeature(
    name="pattern-surface-schema",
    target_direction=TargetDirection(
        disposition="retain",
        contract="docs/design/pattern_matching.md#surface-and-core-contract",
        normal_form="versioned frontend-neutral Pattern Surface fragment",
        reason="Retain the fragment boundary without claiming full match execution.",
    ),
    description=(
        "Target-only, versioned Pattern Surface nodes, diagnostics, and "
        "equivalent Lark/Rust fragment producers"
    ),
    status="prototype-ready",
    layer="L2",
    semantic_forms=("pattern", "binding", "diagnostic"),
    reduces_to=("transactional-pattern-core",),
    docs=(
        "docs/design/pattern_matching.md",
        "docs/design/schemas/pattern_surface.schema.json",
    ),
    tests=(
        "prototype/tests/unit/parser/test_pattern_surface_frontend_parity.py",
    ),
    coverage=FeatureCapabilityAxes(
        target_only=True,
        parse=True,
        explain=True,
        docs=True,
        tests=True,
    ),
)

_binding_data_pattern_integration = SyntaxFeature(
    name="binding-data-pattern-integration",
    target_direction=TargetDirection(
        disposition="open",
        contract="docs/design/semantics.md#binding",
        normal_form="shared checked binding/data/pattern metadata",
        reason="The integration representation remains open despite accepted behavior.",
    ),
    description=(
        "Target integration contract for shared BindingTarget, constraints, "
        "decode diagnostics, pattern captures, and explanation events"
    ),
    status="design-needed",
    layer="L2",
    semantic_forms=("binding", "data-boundary", "pattern", "absence-result", "explanation"),
    runtime_hooks_allowed="semantic",
    docs=("docs/design/semantics.md",),
    coverage=target_only_coverage(docs=True),
)

_collection_table_rank_integration = SyntaxFeature(
    name="collection-table-rank-integration",
    target_direction=TargetDirection(
        disposition="open",
        contract="docs/design/decisions.md#open-experiments",
        normal_form="typed collections, streams and explicit table/array plans",
        reason="Rank, protocols and scoped query admission need concrete experiments.",
    ),
    description=(
        "Target integration contract for collection flow, table values, "
        "plans, row/group contexts, shape/rank, and query admission"
    ),
    status="design-needed",
    layer="L5",
    semantic_forms=("flow", "data-boundary", "pattern", "absence-result", "explanation"),
    runtime_hooks_allowed="semantic",
    docs=("docs/design/semantics.md",),
    coverage=target_only_coverage(docs=True),
)

_block_policy_prelude = SyntaxFeature(
    name="block-policy-prelude",
    target_direction=TargetDirection(
        disposition="rework",
        contract="docs/design/decisions.md#syntax-simplification-decisions",
        normal_form="distinct resource, retry, transaction and task contracts",
        reason="The old unified block-policy agenda must split by semantic owner.",
    ),
    description=(
        "Target prelude contract for using, retry, timeout, transaction, "
        "trace, test, world, cleanup, capabilities, and policy events"
    ),
    status="design-needed",
    layer="L5",
    semantic_forms=("block", "binding", "absence-result", "capability", "explanation"),
    runtime_hooks_allowed="semantic",
    docs=("docs/design/decisions.md", "docs/design/semantics.md"),
    coverage=target_only_coverage(docs=True),
)


# ── registry ─────────────────────────────────────────────────────────

BUILTIN_FEATURES: list[SyntaxFeature] = [
    _expression_precedence,
    _piecewise_functions,
    _where_clauses,
    _underscore_lambdas,
    _positional_holes,
    _augassign,
    _assert,
    _decorator,
    _pass,
    _with,
    _fstring,
    _unless_lowering,
    _postfix_conditionals,
    # ── lowering mixins (order: grammar rule order in statements.lark / expressions.lark) ──
    _implicit_mul,
    _type_alias,
    _range_expressions,
    _if_let,
    _try_expr,
    _match_expr,
    _where_clause_lowering,
    _positional_hole_lowering,
    _compose_lowering,
    _defer_lowering,
    _func_equation_lowering,
    _section_lowering,
    _func_expr_lowering,
    _block_call_lowering,
    _data_decl_lowering,
    _pattern_surface_schema,
    _binding_data_pattern_integration,
    _collection_table_rank_integration,
    _block_policy_prelude,
]


def get_layer_transforms() -> list:
    """Return ordered LayerTransform instances derived from builtin features.

    Dotted-string references are lazy-resolved and instantiated so the
    feature list does not force early imports.
    """
    from prototype.utils import resolve_dotted

    transforms = []
    for feature in BUILTIN_FEATURES:
        for ref in feature.layer_transforms:
            transform_cls = resolve_dotted(ref)
            transforms.append(transform_cls())
    return transforms


def get_lowering_mixins() -> list[type]:
    """Return ordered lowering mixin classes derived from builtin features.

    These are composed into ``FunctionsMixin`` so the Lark→AST transformer
    finds the right lowering method for each grammar rule.
    """
    from prototype.utils import resolve_dotted

    mixins = []
    for feature in BUILTIN_FEATURES:
        for ref in feature.lowering_mixins:
            mixins.append(resolve_dotted(ref))
    return mixins


def get_extra_grammar_layers() -> list[str]:
    """Return extra grammar layer filenames derived from builtin features.

    Base layers (terminals, expressions, etc.) are always included.
    Features that declare ``grammar_layers`` add their fragments after
    the base, in feature-registry order.
    """
    extra = []
    for feature in BUILTIN_FEATURES:
        extra.extend(feature.grammar_layers)
    return extra


def get_declared_soft_keywords(
    features: list[SyntaxFeature] | None = None,
) -> tuple[str, ...]:
    """Return feature-owned soft keywords in deterministic registry order."""
    keywords = []
    for feature in features or BUILTIN_FEATURES:
        for keyword in feature.soft_keywords:
            if keyword not in keywords:
                keywords.append(keyword)
    return tuple(keywords)


def get_desugar_passes(
    profile: str | None = None,
) -> list[Type[BaseDesugarer]]:
    """Return ordered desugar-pass classes derived from builtin features.

    Classes (not instances) are returned because desugar_module
    instantiates them fresh for each module.  When *profile* is provided,
    only passes declared for that desugar profile are returned.
    """
    from prototype.utils import resolve_dotted

    if profile is not None and profile not in ALLOWED_DESUGAR_PROFILES:
        raise ValueError(f"Unknown desugar profile: {profile!r}")

    passes = []
    for feature in BUILTIN_FEATURES:
        if profile is not None and profile not in feature.desugar_profiles:
            continue
        for ref in feature.desugar_passes:
            passes.append(resolve_dotted(ref))
    return passes


def render_feature_layer_table(features: list[SyntaxFeature] | None = None) -> str:
    """Return a compact, deterministic feature/layer inspection table."""
    rows = [
        "| feature | layer | semantic forms | reduces to | runtime hooks |",
        "| --- | --- | --- | --- | --- |",
    ]
    for feature in features or BUILTIN_FEATURES:
        rows.append(
            "| {name} | {layer} | {semantic} | {reduces} | {hooks} |".format(
                name=feature.name,
                layer=feature.layer,
                semantic=", ".join(feature.semantic_forms) or "-",
                reduces=", ".join(feature.reduces_to) or "-",
                hooks=feature.runtime_hooks_allowed,
            )
        )
    return "\n".join(rows)


def get_feature_capabilities(feature: SyntaxFeature) -> FeatureCapabilityAxes:
    """Return a conservative capability matrix row for one feature."""
    if feature.coverage is not None:
        return replace(feature.coverage, samples=bool(feature.sample_files))
    target_only = feature.status in {"research-only", "design-needed"}
    parse = feature.status not in {"research-only", "rejected-for-now"}
    lower = bool(
        feature.layer_transforms
        or feature.lowering_mixins
        or feature.desugar_passes
        or feature.reduces_to
    )
    run = feature.status == "implemented"
    return FeatureCapabilityAxes(
        target_only=target_only,
        parse=parse,
        lower=lower,
        run=run,
        reduce=bool(feature.reduces_to),
        explain=False,
        docs=bool(feature.docs),
        tests=bool(feature.tests),
        samples=bool(feature.sample_files),
        web=False,
        notebook=False,
    )


def render_feature_capability_table(
    features: list[SyntaxFeature] | None = None,
) -> str:
    """Return a current feature capability/spec matrix."""

    def mark(value: bool) -> str:
        return "yes" if value else "no"

    rows = [
        "| feature | target-only | parse | lower | run | reduce | explain | "
        "docs | tests | samples | web | notebook |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for feature in features or BUILTIN_FEATURES:
        capabilities = get_feature_capabilities(feature)
        rows.append(
            "| {name} | {target} | {parse} | {lower} | {run} | {reduce} | "
            "{explain} | {docs} | {tests} | {samples} | {web} | {notebook} |".format(
                name=feature.name,
                target=mark(capabilities.target_only),
                parse=mark(capabilities.parse),
                lower=mark(capabilities.lower),
                run=mark(capabilities.run),
                reduce=mark(capabilities.reduce),
                explain=mark(capabilities.explain),
                docs=mark(capabilities.docs),
                tests=mark(capabilities.tests),
                samples=mark(capabilities.samples),
                web=mark(capabilities.web),
                notebook=mark(capabilities.notebook),
            )
        )
    return "\n".join(rows)


def get_features_by_layer(layer: str) -> list[SyntaxFeature]:
    """Return builtin features that belong to a core-layer bucket."""
    if layer not in ALLOWED_LAYERS:
        raise ValueError(f"Unknown feature layer: {layer!r}")
    return [feature for feature in BUILTIN_FEATURES if feature.layer == layer]


def render_feature_target_table(features: list[SyntaxFeature] | None = None) -> str:
    """Inspect target intent without selecting or disabling prototype behavior."""

    def cell(value: str) -> str:
        return value.replace("|", "\\|").replace("\n", "<br>")

    rows = [
        "| feature | prototype status | target direction | target normal form | contract | reason |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    selected = BUILTIN_FEATURES if features is None else features
    for feature in selected:
        target = feature.target_direction
        values = (
            feature.name,
            feature.status,
            target.disposition if target else "unreviewed",
            target.normal_form if target else "-",
            target.contract if target else "-",
            target.reason if target else "No target direction recorded.",
        )
        rows.append("| " + " | ".join(cell(value) for value in values) + " |")
    return "\n".join(rows)
