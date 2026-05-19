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
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from prototype.grammar.layer import LayerTransform
    from prototype.parser.nomi.desugar.base import BaseDesugarer


ALLOWED_LAYERS = ("L0", "L1", "L2", "L3", "L4", "L5", "L6", "L7")
SUGAR_LAYER = "L4"
DEFAULT_DESUGAR_PROFILE = "default"
REDUCED_DESUGAR_PROFILE = "reduced"
ALLOWED_DESUGAR_PROFILES = (DEFAULT_DESUGAR_PROFILE, REDUCED_DESUGAR_PROFILE)


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
    grammar_layers: tuple[str, ...] = ()
    layer_transforms: tuple = ()
    lowering_mixins: tuple[str, ...] = ()
    desugar_passes: tuple = ()
    desugar_profiles: tuple[str, ...] = ()

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
    docs=("docs/language/core_layer_separation_plan.md",),
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
    docs=("docs/convenience/functions.md",),
    tests=("prototype/tests/features/functions/test_equations_runtime.py",),
    desugar_passes=("prototype.parser.nomi.desugar.piecewise.PiecewiseFunction",),
    desugar_profiles=(DEFAULT_DESUGAR_PROFILE, REDUCED_DESUGAR_PROFILE),
)


# ── where-clauses ────────────────────────────────────────────────────

_where_clauses = SyntaxFeature(
    name="where-clauses",
    description="Postfix where: blocks that bind local definitions after an expression",
    layer=SUGAR_LAYER,
    semantic_forms=("binding", "function"),
    reduces_to=("local-binding-rewrite",),
    docs=("docs/convenience/functions.md",),
    tests=("prototype/tests/features/functions/test_where_runtime.py",),
    desugar_passes=("prototype.parser.nomi.desugar.where_clause.WhereClause",),
    desugar_profiles=(DEFAULT_DESUGAR_PROFILE, REDUCED_DESUGAR_PROFILE),
)


# ── underscore-lambdas ───────────────────────────────────────────────

_underscore_lambdas = SyntaxFeature(
    name="underscore-lambdas",
    description="Scala-style _.attr and _ + 1 anonymous function shorthand",
    layer=SUGAR_LAYER,
    semantic_forms=("function",),
    reduces_to=("canonical-function-literal",),
    docs=("docs/convenience/functions.md",),
    tests=("prototype/tests/features/functions/test_holes_runtime.py",),
    desugar_passes=("prototype.parser.nomi.desugar.underscore_lambda.UnderscoreLambda",),
    desugar_profiles=(DEFAULT_DESUGAR_PROFILE, REDUCED_DESUGAR_PROFILE),
)


# ── positional-holes ─────────────────────────────────────────────────

_positional_holes = SyntaxFeature(
    name="positional-holes",
    description="$1, $name positional hole syntax for implicit lambda parameters",
    layer=SUGAR_LAYER,
    semantic_forms=("function",),
    reduces_to=("canonical-function-literal",),
    docs=("docs/convenience/functions.md",),
    tests=("prototype/tests/features/functions/test_holes_runtime.py",),
    desugar_passes=("prototype.parser.nomi.desugar.positional_hole.PositionalHole",),
    desugar_profiles=(DEFAULT_DESUGAR_PROFILE, REDUCED_DESUGAR_PROFILE),
)


# ── aug-assign-desugar ───────────────────────────────────────────────

_augassign = SyntaxFeature(
    name="aug-assign-desugar",
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
    description="Lower unless cond: body to if not cond: body",
    layer=SUGAR_LAYER,
    semantic_forms=("branch",),
    reduces_to=("branch", "boolean-negation"),
    docs=("docs/convenience/syntax_design_rules.md",),
    tests=("prototype/tests/features/flow/test_conditionals_runtime.py",),
)

_postfix_conditionals = SyntaxFeature(
    name="postfix-conditionals-lowering",
    description="Lower flow statements with postfix if/unless guards to branches",
    layer=SUGAR_LAYER,
    semantic_forms=("branch", "flow"),
    reduces_to=("branch",),
    docs=("docs/convenience/review_and_roadmap.md",),
    tests=("prototype/tests/features/flow/test_conditionals_runtime.py",),
)


# ── lowering mixins ───────────────────────────────────────────────────
# Each Lark grammar rule that needs AST lowering declares its mixin here.
# Order: mixins are composed left-to-right into FunctionsMixin, so later
# mixins can override earlier ones if needed.

_implicit_mul = SyntaxFeature(
    name="implicit-multiplication",
    description="Lower implicit multiplication (2x → 2 * x) in the Lark tree",
    layer=SUGAR_LAYER,
    semantic_forms=("expression",),
    reduces_to=("binary-multiplication",),
    docs=("docs/convenience/functions.md",),
    tests=("prototype/tests/features/math/test_implicit_mul_runtime.py",),
    lowering_mixins=("prototype.parser.nomi.lowering.implicit_multiplication.ImplicitMulMixin",),
)

_type_alias = SyntaxFeature(
    name="type-alias-lowering",
    description="Lower type X = Y to an AST assignment",
    layer="L3",
    semantic_forms=("type-alias", "binding"),
    reduces_to=("binding",),
    docs=("docs/convenience/data_and_types.md",),
    tests=("prototype/tests/features/data/test_type_alias_runtime.py",),
    lowering_mixins=("prototype.parser.nomi.lowering.type_alias.TypeAliasMixin",),
)

_if_let = SyntaxFeature(
    name="if-let-lowering",
    description="Lower if pat = expr: body into a match statement",
    layer=SUGAR_LAYER,
    semantic_forms=("pattern", "match", "branch"),
    reduces_to=("match-statement",),
    docs=("docs/convenience/patterns.md",),
    lowering_mixins=("prototype.parser.nomi.lowering.if_let.IfLetMixin",),
)

_try_expr = SyntaxFeature(
    name="try-expr-lowering",
    description="Lower try body except E: handler into an IIFE",
    layer=SUGAR_LAYER,
    semantic_forms=("absence-result", "exception"),
    reduces_to=("try-statement", "function-call"),
    docs=("docs/convenience/absence_and_result.md",),
    tests=("prototype/tests/features/absence_result/test_try_expr_runtime.py",),
    lowering_mixins=("prototype.parser.nomi.lowering.try_expr.TryExprMixin",),
)

_match_expr = SyntaxFeature(
    name="match-expr-lowering",
    description="Lower match value: case pat => expr into an IIFE",
    layer=SUGAR_LAYER,
    semantic_forms=("match", "pattern"),
    reduces_to=("match-statement", "function-call"),
    docs=("docs/convenience/patterns.md",),
    lowering_mixins=("prototype.parser.nomi.lowering.match_expr.MatchExprMixin",),
)

_where_clause_lowering = SyntaxFeature(
    name="where-clause-lowering",
    description="Lower where: blocks by tagging _nomi_where_body for the desugar pass",
    layer=SUGAR_LAYER,
    semantic_forms=("binding", "function"),
    reduces_to=("local-binding-rewrite",),
    docs=("docs/convenience/functions.md",),
    tests=("prototype/tests/features/functions/test_where_runtime.py",),
    lowering_mixins=("prototype.parser.nomi.lowering.where_clause.WhereClauseMixin",),
)

_positional_hole_lowering = SyntaxFeature(
    name="positional-hole-lowering",
    description="Lower $1, $name hole syntax in expressions",
    layer=SUGAR_LAYER,
    semantic_forms=("function",),
    reduces_to=("canonical-function-literal",),
    docs=("docs/convenience/functions.md",),
    tests=("prototype/tests/features/functions/test_holes_runtime.py",),
    lowering_mixins=("prototype.parser.nomi.lowering.positional_hole.PositionalHoleMixin",),
)

_compose_lowering = SyntaxFeature(
    name="compose-lowering",
    description="Lower >>> and <<< composition operators",
    layer=SUGAR_LAYER,
    semantic_forms=("function", "call"),
    reduces_to=("canonical-function-literal", "nested-call"),
    docs=("docs/convenience/functions.md",),
    tests=("prototype/tests/features/functions/test_composition_runtime.py",),
    lowering_mixins=("prototype.parser.nomi.lowering.compose.ComposeMixin",),
)

_defer_lowering = SyntaxFeature(
    name="defer-lowering",
    description="Lower defer stmt to _nomi_defer attribute on statements",
    layer=SUGAR_LAYER,
    semantic_forms=("block", "resource-policy"),
    reduces_to=("function-body-cleanup-policy",),
    docs=("docs/convenience/absence_and_result.md", "docs/features/block_calls_feature.md"),
    tests=("prototype/tests/features/block_calls/test_defer_runtime.py",),
    lowering_mixins=("prototype.parser.nomi.lowering.defer.DeferMixin",),
)

_func_equation_lowering = SyntaxFeature(
    name="func-equation-lowering",
    description="Lower f(p)=e equation definitions to FunctionDef",
    layer=SUGAR_LAYER,
    semantic_forms=("function", "pattern", "match"),
    reduces_to=("canonical-function", "match-dispatch"),
    docs=("docs/convenience/functions.md",),
    tests=("prototype/tests/features/functions/test_equations_runtime.py",),
    lowering_mixins=("prototype.parser.nomi.lowering.func_equation.FuncEquationMixin",),
)

_section_lowering = SyntaxFeature(
    name="sections-lowering",
    description="Lower (+2), (2*), (+) operator sections to lambdas",
    layer=SUGAR_LAYER,
    semantic_forms=("function",),
    reduces_to=("canonical-function-literal",),
    docs=("docs/convenience/functions.md",),
    tests=("prototype/tests/features/functions/test_composition_runtime.py",),
    lowering_mixins=("prototype.parser.nomi.lowering.sections.SectionMixin",),
)

_func_expr_lowering = SyntaxFeature(
    name="func-expr-lowering",
    description="Lower (x, y) => expr arrow functions to FunctionDef",
    layer="L3",
    semantic_forms=("function",),
    reduces_to=("canonical-function-literal",),
    docs=("docs/convenience/functions.md",),
    lowering_mixins=("prototype.parser.nomi.lowering.func_expr.FuncExprMixin",),
)

_block_call_lowering = SyntaxFeature(
    name="block-call-lowering",
    description="Lower f(x): body block-call syntax to BlockCall surface node",
    layer="L3",
    semantic_forms=("block", "call"),
    reduces_to=("block-call",),
    runtime_hooks_allowed="semantic",
    docs=("docs/features/block_calls_feature.md",),
    tests=("prototype/tests/features/block_calls/test_defer_runtime.py",),
    lowering_mixins=("prototype.parser.nomi.lowering.block_call.BlockCallMixin",),
)

_data_decl_lowering = SyntaxFeature(
    name="data-decl-lowering",
    description="Lower data Name: fields... to a ClassDef with __init__, __repr__, __eq__",
    layer="L3",
    semantic_forms=("data", "binding"),
    reduces_to=("data-constructor", "field-bindings"),
    runtime_hooks_allowed="backend-compat",
    docs=("docs/convenience/data_and_types.md",),
    tests=("prototype/tests/features/data/test_declarations_runtime.py",),
    lowering_mixins=("prototype.parser.nomi.lowering.data_decl.DataDeclMixin",),
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
        samples=False,
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
