"""Bounded typed program induction over the shared pure-function descriptions.

Search returns example-fitting proposals, never universal replacements. Its
grammar, examples, ordering, budget and retention limit are captured inputs.
"""

from dataclasses import dataclass
from fractions import Fraction as F
import itertools
import json

from tools import finite_inquiry as q
from tools import reasoning_structures as s
from tools import scoped_terms as t

PROFILE = "bounded-rational-program-search-v1"


def _number(value):
    if type(value) is not F or max(value.numerator.bit_length(), value.denominator.bit_length()) > 16:
        raise t.Refused("search examples/constants require exact rationals within 16 bits")


@dataclass(frozen=True)
class Grammar:
    identity: t.Identity
    arity: int
    constants: tuple[F, ...] = ()
    operators: tuple[str, ...] = ("add", "sub", "mul", "neg")
    max_nodes: int = 5

    def __post_init__(self):
        if type(self.identity) is not t.Identity:
            raise t.Refused("grammar requires a qualified identity")
        if type(self.arity) is not int or not 1 <= self.arity <= 3:
            raise t.Refused("search admits one to three rational parameters")
        if type(self.max_nodes) is not int or not 1 <= self.max_nodes <= 7:
            raise t.Refused("search body capacity is one to seven nodes")
        if type(self.constants) is not tuple or len(self.constants) > 4:
            raise t.Refused("grammar requires bounded immutable constants")
        for value in self.constants:
            _number(value)
        if len(set(self.constants)) != len(self.constants):
            raise t.Refused("duplicate grammar constant")
        if (
            type(self.operators) is not tuple or len(self.operators) > 4
            or any(type(x) is not str or x not in t.OPERATIONS for x in self.operators)
            or len(set(self.operators)) != len(self.operators)
        ):
            raise t.Refused("grammar requires distinct admitted operation names")

    @property
    def parameters(self):
        revision = q.fingerprint(PROFILE, self)
        return tuple(t.Binding(t.Identity("program-search", revision, f"arg:{i}"), f"arg{i}") for i in range(self.arity))


@dataclass(frozen=True)
class Example:
    identity: t.Identity
    inputs: tuple[F, ...]
    output: F

    def __post_init__(self):
        if type(self.identity) is not t.Identity or type(self.inputs) is not tuple:
            raise t.Refused("example requires qualified identity and immutable inputs")
        if not 1 <= len(self.inputs) <= 3:
            raise t.Refused("example input capacity exceeded")
        for value in (*self.inputs, self.output):
            _number(value)


@dataclass(frozen=True)
class Task:
    grammar: Grammar
    examples: tuple[Example, ...]
    budget: int = 5000
    retain: int = 8

    def __post_init__(self):
        if type(self.grammar) is not Grammar or type(self.examples) is not tuple or len(self.examples) > 16:
            raise t.Refused("task requires captured grammar and up to sixteen examples")
        if any(type(x) is not Example or len(x.inputs) != self.grammar.arity for x in self.examples):
            raise t.Refused("example callable contract mismatch")
        if len({x.identity for x in self.examples}) != len(self.examples):
            raise t.Refused("duplicate example identity")
        if type(self.budget) is not int or not 1 <= self.budget <= 5000:
            raise t.Refused("search budget must be one to five thousand candidates")
        if type(self.retain) is not int or not 1 <= self.retain <= 8:
            raise t.Refused("retention must be one to eight proposals")

    @property
    def fingerprint(self):
        return q.fingerprint(PROFILE, self)


@dataclass(frozen=True)
class Result:
    profile: str
    context: str
    coverage: str
    examined: int
    matches: int
    proposals: tuple[s.Transformation, ...]
    costs: tuple[int, ...]
    retention: str


def _bodies(grammar):
    """Nondecreasing node count; declared leaf/operator/split order breaks ties."""
    layers = {}
    parameters = grammar.parameters
    for size in range(1, grammar.max_nodes + 1):
        layer = []

        def candidates():
            if size == 1:
                yield from (t.Reference(x.identity) for x in parameters)
                yield from (t.literal(x) for x in grammar.constants)
            for name in grammar.operators:
                if t.OPERATIONS[name] == 1 and size > 1:
                    for child in layers[size - 1]:
                        yield t.Operation(name, (child,))
                elif t.OPERATIONS[name] == 2:
                    for left_size in range(1, size - 1):
                        for left, right in itertools.product(layers[left_size], layers[size - 1 - left_size]):
                            yield t.Operation(name, (left, right))

        for body in candidates():
            yield size, body
            layer.append(body)
        layers[size] = layer


def search(task):
    if type(task) is not Task:
        raise t.Refused("search requires a captured task")
    proposals, costs = [], []
    examined = matches = 0
    stream = _bodies(task.grammar)
    for cost, body in itertools.islice(stream, task.budget):
        term = t.Lambda(task.grammar.parameters, body)
        examined += 1
        if all(t.realize(term, x.inputs) == x.output for x in task.examples):
            matches += 1
            if len(proposals) < task.retain:
                proposals.append(s.rational(term))
                costs.append(cost)
    coverage = "complete" if next(stream, None) is None else "incomplete"
    return Result(
        PROFILE, task.fingerprint, coverage, examined, matches, tuple(proposals),
        tuple(costs), "all-matches" if matches <= task.retain else "truncated",
    )


def describe(result):
    if type(result) is not Result:
        raise t.Refused("expected search result")
    return {
        "profile": result.profile, "context": result.context,
        "coverage": result.coverage, "examined": result.examined,
        "matches": result.matches, "retention": result.retention,
        "selection": "body-node-count-then-declared-grammar-order",
        "evidence": "supplied-examples-only",
        "proposals": [s.describe(x) for x in result.proposals], "costs": list(result.costs),
    }


def example():
    grammar = Grammar(t.Identity("square-or-line", "1", "grammar"), 1, (), ("mul",), 3)
    examples = tuple(Example(t.Identity("teaching", "1", f"example:{x}"), (F(x),), F(x)) for x in (0, 1))
    return Task(grammar, examples)


def main():
    from tools.program_search_replay import verify

    task = example()
    result = search(task)
    verify(task, result)
    print(json.dumps(describe(result), indent=2))


if __name__ == "__main__":
    main()
