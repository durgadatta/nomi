"""Explicit interpretation from scoped pure functions to exact polynomial maps.

Uses the existing formal algebra; no numerical inputs or new source syntax.
Optional independent SymPy replay follows qualified owners rather than the
producer's locally nameless evaluator. Formal tangents are not general AD.
"""

import argparse
from dataclasses import dataclass
import json
from fractions import Fraction

from tools import finite_inquiry as q
from tools import nomi_terms as n
from tools import reasoning_algebra as algebra
from tools import reasoning_structures as s
from tools import scoped_terms as t

PROFILE = "scoped-function-polynomial-interpretation-v1"


def coordinate_space(arity):
    return algebra.Space("formal-rational-product", tuple(f"arg:{i}" for i in range(arity)), str(arity))


def _context(source, space, budget):
    if type(source) is not s.Transformation or source.provider != s.RATIONAL:
        raise t.Refused("interpretation requires a closed rational transformation")
    if type(space) is not algebra.Space or space.base is not None or len(space.axes) != source.source.arity:
        raise t.Refused("interpretation requires matching formal affine coordinates")
    if type(budget) is not int or not 1 <= budget <= 10000:
        raise t.Refused("symbolic reduction budget is one to ten thousand visits")
    return q.fingerprint(PROFILE, source.fingerprint, space, budget)


@dataclass(frozen=True)
class Projection:
    context: str
    budget: int
    mapping: algebra.Mapping


def project(source, *, space=None, budget=10000):
    if type(source) is not s.Transformation or source.provider != s.RATIONAL:
        raise t.Refused("interpretation requires a closed rational transformation")
    space = coordinate_space(source.source.arity) if space is None else space
    context = _context(source, space, budget)
    visits = depth = 0

    def evaluate(node, local):
        nonlocal visits, depth
        visits += 1
        if visits > budget:
            raise t.Refused("symbolic reduction budget exhausted; no interpretation claim")
        depth += 1
        try:
            if depth > 64:
                raise t.Refused("symbolic reduction depth capacity exhausted")
            return evaluate_body(node, local)
        finally:
            depth -= 1

    def evaluate_body(node, local):
        tag = node[0]
        if tag == "literal":
            return algebra.constant(space, Fraction(node[1], node[2]))
        if tag == "bound":
            return local[node[1]]
        if tag == "lambda":
            return (node, local)
        if tag == "application":
            closure = evaluate(node[1], local)
            values = tuple(evaluate(x, local) for x in node[2])
            return invoke(closure, values)
        operands = tuple(evaluate(x, local) for x in node[2])
        if node[1] == "add":
            return operands[0] + operands[1]
        if node[1] == "sub":
            return operands[0] - operands[1]
        if node[1] == "mul":
            return operands[0] * operands[1]
        return -operands[0]

    def invoke(closure, values):
        node, captured = closure
        return evaluate(node[2], tuple(reversed(values)) + captured)

    polynomial = invoke(evaluate(t.lower(source.description), ()), algebra.coordinates(space))
    mapping = algebra.Mapping("source:" + context, space, coordinate_space(1), (polynomial,))
    return Projection(context, budget, mapping)


def _sympy():
    try:
        import sympy
    except ImportError as error:
        raise t.Refused("install the reasoning-check extra for independent SymPy replay") from error
    if sympy.__version__ != "1.14.0":
        raise t.Refused("independent symbolic adapter requires SymPy 1.14.0")
    return sympy


def _owner_expression(source, symbols, budget, sympy):
    visits = depth = 0

    def evaluate(node, environment):
        nonlocal visits, depth
        visits += 1
        if visits > budget:
            raise t.Refused("independent symbolic reduction budget exhausted")
        depth += 1
        try:
            if depth > 64:
                raise t.Refused("independent symbolic reduction depth capacity exhausted")
            return evaluate_body(node, environment)
        finally:
            depth -= 1

    def evaluate_body(node, environment):
        if type(node) is t.Reference:
            return environment[node.identity]
        if type(node) is t.Literal:
            return sympy.Rational(node.value.numerator, node.value.denominator)
        if type(node) is t.Lambda:
            return (node, environment)
        if type(node) is t.Application:
            closure = evaluate(node.function, environment)
            values = tuple(evaluate(x, environment) for x in node.arguments)
            return invoke(closure, values)
        values = tuple(evaluate(x, environment) for x in node.arguments)
        if node.name == "neg":
            return -values[0]
        if node.name == "mul":
            return sympy.Mul(*values)
        if node.name == "sub":
            return sympy.Add(values[0], -values[1])
        return sympy.Add(*values)

    def invoke(closure, values):
        node, captured = closure
        environment = captured | {parameter.identity: value for parameter, value in zip(node.parameters, values, strict=True)}
        return evaluate(node.body, environment)

    return invoke(evaluate(source.description, {}), symbols)


def _component(expression, symbols, sympy):
    return sum((
        sympy.Rational(coefficient.numerator, coefficient.denominator)
        * sympy.Mul(*(symbol ** exponent for symbol, exponent in zip(symbols, power, strict=True)))
        for power, coefficient in expression.terms
    ), sympy.Integer(0))


def verify(source, projection, *, space=None, budget=10000):
    """Independent established symbolic replay; never numeric example fit."""
    if type(source) is not s.Transformation or source.provider != s.RATIONAL:
        raise t.Refused("interpretation requires a closed rational transformation")
    space = coordinate_space(source.source.arity) if space is None else space
    context = _context(source, space, budget)
    if type(projection) is not Projection or projection.context != context or type(projection.budget) is not int or projection.budget != budget:
        raise t.Refused("stale polynomial interpretation")
    mapping = projection.mapping
    if type(mapping) is not algebra.Mapping or (mapping.identity, mapping.domain, mapping.codomain) != ("source:" + context, space, coordinate_space(1)):
        raise t.Refused("polynomial interpretation port/source mismatch")
    sympy = _sympy()
    variables = tuple(sympy.Dummy(f"input_{i}") for i in range(len(space.axes)))
    expected = _owner_expression(source, variables, budget, sympy)
    if sympy.expand(expected - _component(mapping.components[0], variables, sympy)) != 0:
        raise t.Refused("polynomial interpretation failed independent replay")
    return True


def verify_tangent(source, projection, tangent, *, space=None, budget=10000):
    verify(source, projection, space=space, budget=budget)
    mapping = projection.mapping
    if type(tangent) is not algebra.Mapping or (tangent.domain, tangent.codomain) != (algebra.tangent_space(mapping.domain), algebra.tangent_space(mapping.codomain)):
        raise t.Refused("tangent has wrong base/direction spaces")
    sympy = _sympy()
    size = len(mapping.domain.axes)
    variables = tuple(sympy.Dummy(f"tangent_{i}") for i in range(2 * size))
    expression = _owner_expression(source, variables[:size], budget, sympy)
    directional = sum((sympy.diff(expression, x) * delta for x, delta in zip(variables[:size], variables[size:], strict=True)), sympy.Integer(0))
    if any(sympy.expand(expected - _component(actual, variables, sympy)) != 0 for expected, actual in zip((expression, directional), tangent.components, strict=True)):
        raise t.Refused("formal tangent failed independent symbolic replay")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sympy", action="store_true", help="independently check interpretation and tangent")
    args = parser.parse_args()
    try:
        source = s.rational(n.parse(t.Source("force", "1", "(position, velocity) => -2 * position - velocity")))
        projection = project(source)
        tangent = algebra.tangent(projection.mapping)
        checked = False
        if args.sympy:
            checked = verify_tangent(source, projection, tangent)
        print(json.dumps({
            "profile": PROFILE, "source": s.describe(source),
            "context": projection.context, "mapping": algebra.describe(projection.mapping),
            "formal_tangent": algebra.describe(tangent), "independent_sympy_replay": checked,
            "numerical_inputs": [],
        }, indent=2))
    except (t.Refused, algebra.Refused) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
