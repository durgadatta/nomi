"""Independent tuple-grammar enumeration and arithmetic replay of search claims.

Shares contract validation; does not call producer enumeration, realization or
search. This checks bounded completeness and example fit, not scientific truth.
"""

from itertools import islice

from tools import program_search as p
from tools import reasoning_structures as s
from tools import scoped_terms as t


def _enumerate(grammar):
    levels = [[] for _ in range(grammar.max_nodes + 1)]
    for size in range(1, grammar.max_nodes + 1):
        if size == 1:
            for i in range(grammar.arity):
                tree = ("var", i)
                yield size, tree
                levels[size].append(tree)
            for constant in grammar.constants:
                tree = ("number", constant)
                yield size, tree
                levels[size].append(tree)
        for operation in grammar.operators:
            if operation == "neg":
                pairs = ((child,) for child in levels[size - 1])
            else:
                pairs = (
                    (left, right)
                    for split in range(1, size - 1)
                    for left in levels[split]
                    for right in levels[size - split - 1]
                )
            for children in pairs:
                tree = (operation, *children)
                yield size, tree
                levels[size].append(tree)


def _evaluate(tree, inputs):
    if tree[0] == "var":
        return inputs[tree[1]]
    if tree[0] == "number":
        return tree[1]
    left = _evaluate(tree[1], inputs)
    if tree[0] == "neg":
        return -left
    right = _evaluate(tree[2], inputs)
    if tree[0] == "add":
        return left + right
    if tree[0] == "sub":
        return left - right
    return left * right


def _proposal_tree(proposal, grammar):
    if type(proposal) is not s.Transformation or proposal.provider != s.RATIONAL:
        raise t.Refused("invalid search proposal provider")
    term = proposal.description
    if term.parameters != grammar.parameters:
        raise t.Refused("search proposal has stale binder context")
    parameters = {x.identity: i for i, x in enumerate(term.parameters)}

    def read(node):
        if node.origin is not None:
            raise t.Refused("search proposal invents source provenance")
        if type(node) is t.Reference and node.identity in parameters:
            return ("var", parameters[node.identity])
        if type(node) is t.Literal:
            return ("number", node.value)
        if type(node) is t.Operation:
            return (node.name, *(read(x) for x in node.arguments))
        raise t.Refused("proposal outside declared expression grammar")

    if term.origin is not None:
        raise t.Refused("search proposal invents source provenance")
    return read(term.body)


def verify(task, result):
    if type(task) is not p.Task or type(result) is not p.Result:
        raise t.Refused("invalid search replay context")
    if result.profile != p.PROFILE or result.context != task.fingerprint:
        raise t.Refused("stale search assessment")
    if (
        type(result.examined) is not int or type(result.matches) is not int
        or type(result.proposals) is not tuple or type(result.costs) is not tuple
        or any(type(x) is not int for x in result.costs)
    ):
        raise t.Refused("malformed search assessment")
    expected, costs = [], []
    examined = matches = 0
    stream = _enumerate(task.grammar)
    for cost, tree in islice(stream, task.budget):
        examined += 1
        if all(_evaluate(tree, x.inputs) == x.output for x in task.examples):
            matches += 1
            if len(expected) < task.retain:
                expected.append(tree)
                costs.append(cost)
    coverage = "complete" if next(stream, None) is None else "incomplete"
    if (
        (result.examined, result.matches, result.coverage, result.retention)
        != (examined, matches, coverage, "all-matches" if matches <= task.retain else "truncated")
        or result.costs != tuple(costs)
        or tuple(_proposal_tree(x, task.grammar) for x in result.proposals) != tuple(expected)
    ):
        raise t.Refused("search counts, coverage or ranked proposals failed replay")
    return True
