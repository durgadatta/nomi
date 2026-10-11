"""Two binder representations for a closed, pure rational expression profile.

The Python-expression producer is a replaceable research adapter, not Nomi syntax.
Descriptions, type checking and capture-free substitution never realize values.
"""

import ast
from dataclasses import asdict, dataclass, field
from fractions import Fraction
import hashlib
import json

PROFILE = "pure-scoped-rational-terms-v1"
MAX_NODES = 256
MAX_DEPTH = 32
MAX_SOURCE_BYTES = 8192
OPERATIONS = {"add": 2, "sub": 2, "mul": 2, "neg": 1}


class Refused(ValueError):
    """A description does not satisfy the closed profile."""


def _name(value):
    if type(value) is not str or not value or len(value) > 128:
        raise Refused("expected bounded nonempty identity")


@dataclass(frozen=True, order=True)
class Identity:
    owner: str
    revision: str
    slot: str

    def __post_init__(self):
        for value in (self.owner, self.revision, self.slot):
            _name(value)


@dataclass(frozen=True)
class FunctionType:
    parameters: tuple
    result: object


RATIONAL = "Rational"


def _type(value, depth=0):
    if depth > MAX_DEPTH:
        raise Refused("type exceeds depth capacity")
    if value == RATIONAL and type(value) is str:
        return
    if type(value) is not FunctionType or type(value.parameters) is not tuple:
        raise Refused("unsupported type")
    if not 1 <= len(value.parameters) <= 8:
        raise Refused("callable requires 1..8 parameters")
    for parameter in value.parameters:
        _type(parameter, depth + 1)
    _type(value.result, depth + 1)


@dataclass(frozen=True)
class Binding:
    identity: Identity
    label: str = field(compare=False)
    sort: object = RATIONAL

    def __post_init__(self):
        if type(self.identity) is not Identity:
            raise Refused("binding requires qualified identity")
        _name(self.label)
        _type(self.sort)


@dataclass(frozen=True)
class Source:
    identity: str
    revision: str
    text: str

    def __post_init__(self):
        _name(self.identity)
        _name(self.revision)
        if type(self.text) is not str or len(self.text.encode()) > MAX_SOURCE_BYTES:
            raise Refused("source exceeds byte capacity")

    @property
    def digest(self):
        return hashlib.sha256(self.text.encode()).hexdigest()


@dataclass(frozen=True)
class Origin:
    source: str
    revision: str
    digest: str
    start_byte: int
    end_byte: int


@dataclass(frozen=True)
class Reference:
    identity: Identity
    origin: Origin | None = field(default=None, compare=False)


@dataclass(frozen=True)
class Literal:
    value: Fraction
    origin: Origin | None = field(default=None, compare=False)


@dataclass(frozen=True)
class Operation:
    name: str
    arguments: tuple
    origin: Origin | None = field(default=None, compare=False)


@dataclass(frozen=True)
class Lambda:
    parameters: tuple[Binding, ...]
    body: object
    origin: Origin | None = field(default=None, compare=False)


@dataclass(frozen=True)
class Application:
    function: object
    arguments: tuple
    origin: Origin | None = field(default=None, compare=False)


def literal(value):
    if type(value) not in (int, Fraction):
        raise Refused("exact rationals only; no Bool or Float")
    value = Fraction(value)
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > 256:
        raise Refused("rational exceeds bit capacity")
    return Literal(value)


def _children(term):
    if type(term) in (Reference, Literal):
        return ()
    if type(term) is Operation:
        if term.name not in OPERATIONS or type(term.arguments) is not tuple:
            raise Refused("unsupported operation or mutable arguments")
        if len(term.arguments) != OPERATIONS[term.name]:
            raise Refused("operation arity mismatch")
        return term.arguments
    if type(term) is Lambda:
        if type(term.parameters) is not tuple or not 1 <= len(term.parameters) <= 8:
            raise Refused("lambda requires immutable parameters")
        if any(type(x) is not Binding for x in term.parameters):
            raise Refused("invalid parameter")
        if len({x.identity for x in term.parameters}) != len(term.parameters):
            raise Refused("duplicate parameter identity")
        return (term.body,)
    if type(term) is Application:
        if type(term.arguments) is not tuple or len(term.arguments) > 8:
            raise Refused("invalid application arguments")
        return (term.function, *term.arguments)
    raise Refused("unsupported term")


def validate(term):
    pending = [(term, 0, frozenset())]
    count = 0
    while pending:
        node, depth, owners = pending.pop()
        count += 1
        if count > MAX_NODES or depth > MAX_DEPTH:
            raise Refused("term exceeds node/depth capacity")
        if type(node) is Reference and type(node.identity) is not Identity:
            raise Refused("invalid reference identity")
        if type(node) is Literal:
            if type(node.value) is not Fraction:
                raise Refused("literal must be a canonical Fraction")
            literal(node.value)
        children = _children(node)
        if type(node) is Lambda:
            introduced = frozenset(x.identity for x in node.parameters)
            if introduced & owners:
                raise Refused("binder identity reused; shadow labels, not owners")
            owners = owners | introduced
        pending.extend((child, depth + 1, owners) for child in children)


def _context(bindings):
    if type(bindings) is not tuple or any(type(x) is not Binding for x in bindings):
        raise Refused("context requires immutable declarations")
    if len(bindings) > 64 or len({x.identity for x in bindings}) != len(bindings):
        raise Refused("duplicate or excessive context declarations")
    return {x.identity: x.sort for x in bindings}


def infer(term, context=()):
    validate(term)
    free = _context(context)

    def visit(node, local):
        if type(node) is Literal:
            return RATIONAL
        if type(node) is Reference:
            if node.identity not in local:
                raise Refused("unresolved or stale reference")
            return local[node.identity]
        if type(node) is Operation:
            if any(visit(x, local) != RATIONAL for x in node.arguments):
                raise Refused("rational operation requires scalar operands")
            return RATIONAL
        if type(node) is Lambda:
            if any(x.identity in local for x in node.parameters):
                raise Refused("binder identity reused; shadow labels, not owners")
            nested = local | {x.identity: x.sort for x in node.parameters}
            return FunctionType(
                tuple(x.sort for x in node.parameters), visit(node.body, nested)
            )
        function = visit(node.function, local)
        arguments = tuple(visit(x, local) for x in node.arguments)
        if type(function) is not FunctionType or function.parameters != arguments:
            raise Refused("call contract mismatch")
        return function.result

    return visit(term, free)


def lower(term):
    """Locally nameless form: bound indices, qualified free references, no labels."""
    validate(term)

    def visit(node, local):
        if type(node) is Reference:
            return (
                ("bound", local.index(node.identity))
                if node.identity in local
                else ("free", node.identity)
            )
        if type(node) is Literal:
            return ("literal", node.value.numerator, node.value.denominator)
        if type(node) is Operation:
            return (
                "operation",
                node.name,
                tuple(visit(x, local) for x in node.arguments),
            )
        if type(node) is Lambda:
            nested = tuple(x.identity for x in reversed(node.parameters)) + local
            return (
                "lambda",
                tuple(x.sort for x in node.parameters),
                visit(node.body, nested),
            )
        return (
            "application",
            visit(node.function, local),
            tuple(visit(x, local) for x in node.arguments),
        )

    return visit(term, ())


def alpha_equivalent(left, right):
    return lower(left) == lower(right)


def free_references(term):
    validate(term)

    def visit(node, local):
        if type(node) is Reference:
            return {node.identity} - local
        if type(node) is Lambda:
            return visit(node.body, local | {x.identity for x in node.parameters})
        return set().union(*(visit(x, local) for x in _children(node)))

    return frozenset(visit(term, set()))


def substitute(term, replacements):
    """Simultaneous, capture-free substitution; inserted terms are not rewritten."""
    validate(term)
    if type(replacements) is not dict or any(
        type(x) is not Identity for x in replacements
    ):
        raise Refused("substitution requires qualified reference keys")
    for value in replacements.values():
        validate(value)
    occupied = set(replacements) | set(free_references(term))

    def reserve(node):
        if type(node) is Lambda:
            occupied.update(x.identity for x in node.parameters)
        if type(node) is Reference:
            occupied.add(node.identity)
        for child in _children(node):
            reserve(child)

    reserve(term)
    for value in replacements.values():
        reserve(value)

    def fresh(binding):
        for i in range(MAX_NODES * 2):
            identity = Identity(
                binding.identity.owner, binding.identity.revision, f"fresh:{i}"
            )
            if identity not in occupied:
                occupied.add(identity)
                return Binding(identity, binding.label, binding.sort)
        raise Refused("fresh binder capacity exhausted")

    def visit(node, substitutions, renames):
        if type(node) is Reference:
            if node.identity in renames:
                return Reference(renames[node.identity], node.origin)
            return substitutions.get(node.identity, node)
        if type(node) is Literal:
            return node
        if type(node) is Lambda:
            keys = {x.identity for x in node.parameters}
            active = {k: v for k, v in substitutions.items() if k not in keys}
            captures = set().union(*(free_references(x) for x in active.values()))
            parameters = tuple(
                fresh(x) if x.identity in captures else x for x in node.parameters
            )
            nested = {k: v for k, v in renames.items() if k not in keys}
            nested.update(
                {
                    old.identity: new.identity
                    for old, new in zip(node.parameters, parameters)
                }
            )
            return Lambda(parameters, visit(node.body, active, nested), node.origin)
        if type(node) is Operation:
            return Operation(
                node.name,
                tuple(visit(x, substitutions, renames) for x in node.arguments),
                node.origin,
            )
        return Application(
            visit(node.function, substitutions, renames),
            tuple(visit(x, substitutions, renames) for x in node.arguments),
            node.origin,
        )

    result = visit(term, dict(replacements), {})
    validate(result)
    return result


def beta(application, context=()):
    if type(application) is not Application or type(application.function) is not Lambda:
        raise Refused("beta requires a described lambda application")
    expected = infer(application, context)
    result = substitute(
        application.function.body,
        {
            x.identity: value
            for x, value in zip(application.function.parameters, application.arguments)
        },
    )
    if infer(result, context) != expected:
        raise Refused("substitution changed type")
    return result


def parse(source, context=()):
    """Lower a restricted Python expression without eval or host name lookup."""
    if type(source) is not Source:
        raise Refused("producer requires a source revision")
    _context(context)
    names = {x.label: x for x in context}
    if len(names) != len(context):
        raise Refused("ambiguous imported label")
    try:
        root = ast.parse(source.text, mode="eval")
    except (SyntaxError, RecursionError) as error:
        raise Refused("invalid expression draft") from error
    offsets = [0]
    for line in source.text.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line.encode()))
    serial = 0
    count = 0

    def visit(node, local, depth=0):
        nonlocal serial, count
        count += 1
        if depth > MAX_DEPTH or count > MAX_NODES:
            raise Refused("source term exceeds capacity")
        origin = Origin(
            source.identity,
            source.revision,
            source.digest,
            offsets[node.lineno - 1] + node.col_offset,
            offsets[node.end_lineno - 1] + node.end_col_offset,
        )
        if type(node) is ast.Constant:
            result = literal(node.value)
            return Literal(result.value, origin)
        if type(node) is ast.Name:
            if node.id not in local:
                raise Refused("unresolved source name")
            return Reference(local[node.id].identity, origin)
        if type(node) is ast.Lambda:
            args = node.args
            if (
                args.defaults
                or args.kw_defaults
                or args.vararg
                or args.kwarg
                or args.kwonlyargs
                or args.posonlyargs
            ):
                raise Refused("only closed positional lambda contracts")
            parameters = []
            for argument in args.args:
                serial += 1
                parameters.append(
                    Binding(
                        Identity(source.identity, source.revision, f"binder:{serial}"),
                        argument.arg,
                    )
                )
            if len({x.label for x in parameters}) != len(parameters):
                raise Refused("duplicate source parameter")
            return Lambda(
                tuple(parameters),
                visit(node.body, local | {x.label: x for x in parameters}, depth + 1),
                origin,
            )
        if type(node) is ast.BinOp and type(node.op) in (ast.Add, ast.Sub, ast.Mult):
            operation = {ast.Add: "add", ast.Sub: "sub", ast.Mult: "mul"}[type(node.op)]
            return Operation(
                operation,
                (
                    visit(node.left, local, depth + 1),
                    visit(node.right, local, depth + 1),
                ),
                origin,
            )
        if type(node) is ast.UnaryOp and type(node.op) is ast.USub:
            return Operation("neg", (visit(node.operand, local, depth + 1),), origin)
        if type(node) is ast.Call and not node.keywords:
            return Application(
                visit(node.func, local, depth + 1),
                tuple(visit(x, local, depth + 1) for x in node.args),
                origin,
            )
        raise Refused("source form outside pure rational profile")

    term = visit(root.body, names)
    infer(term, context)
    return term


def source_slice(origin, source):
    if type(origin) is not Origin or type(source) is not Source:
        raise Refused("source view requires an origin and source")
    if (origin.source, origin.revision, origin.digest) != (
        source.identity,
        source.revision,
        source.digest,
    ):
        raise Refused("stale source view")
    data = source.text.encode()
    if (
        type(origin.start_byte) is not int
        or type(origin.end_byte) is not int
        or not 0 <= origin.start_byte <= origin.end_byte <= len(data)
    ):
        raise Refused("invalid source byte range")
    try:
        return data[origin.start_byte : origin.end_byte].decode()
    except UnicodeDecodeError as error:
        raise Refused("source span splits a UTF-8 scalar") from error


def describe(term, context=()):
    """Detached source/binder inspection; origins are provenance, not rewritten text."""
    sort = infer(term, context)
    nodes = []

    def visit(node, path):
        item = {"path": path, "kind": type(node).__name__}
        if node.origin is not None:
            if type(node.origin) is not Origin:
                raise Refused("invalid origin metadata")
            item["origin"] = asdict(node.origin)
        if type(node) is Lambda:
            item["parameters"] = [asdict(x) for x in node.parameters]
        nodes.append(item)
        for i, child in enumerate(_children(node)):
            visit(child, path + [i])

    visit(term, [])

    def wire(value):
        if type(value) in (Identity, FunctionType):
            return asdict(value)
        raise Refused("unsupported inspection value")

    record = json.loads(
        json.dumps(
            {
                "profile": PROFILE,
                "type": sort,
                "normal_form": lower(term),
                "context": [asdict(x) for x in context],
                "nodes": nodes,
            },
            default=wire,
            sort_keys=True,
        )
    )
    record["fingerprint"] = hashlib.sha256(
        json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return record


def realize(term, arguments=(), context=(), bindings=None):
    """Explicit exact adapter over the locally nameless form, not Python eval."""
    sort = infer(term, context)
    bindings = {} if bindings is None else bindings
    if type(bindings) is not dict or set(bindings) != set(_context(context)):
        raise Refused("adapter bindings must match context exactly")
    if any(x.sort != RATIONAL for x in context):
        raise Refused("adapter admits scalar free bindings only")
    values = {key: literal(value).value for key, value in bindings.items()}

    def evaluate(node, local):
        tag = node[0]
        if tag == "literal":
            return Fraction(node[1], node[2])
        if tag == "bound":
            return local[node[1]]
        if tag == "free":
            return values[node[1]]
        if tag == "lambda":
            return (node, local)
        if tag == "application":
            closure = evaluate(node[1], local)
            args = tuple(evaluate(x, local) for x in node[2])
            return invoke(closure, args)
        operands = tuple(evaluate(x, local) for x in node[2])
        if node[1] == "add":
            result = operands[0] + operands[1]
        elif node[1] == "sub":
            result = operands[0] - operands[1]
        elif node[1] == "mul":
            result = operands[0] * operands[1]
        else:
            result = -operands[0]
        return literal(result).value

    def invoke(closure, args):
        node, captured = closure
        if len(node[1]) != len(args):
            raise Refused("adapter call arity mismatch")
        return evaluate(node[2], tuple(reversed(args)) + captured)

    if type(arguments) is not tuple:
        raise Refused("adapter arguments must be immutable")
    result = evaluate(lower(term), ())
    if type(sort) is FunctionType:
        if any(x != RATIONAL for x in sort.parameters):
            raise Refused("adapter admits scalar inputs only")
        result = invoke(result, tuple(literal(x).value for x in arguments))
    elif arguments:
        raise Refused("scalar term takes no arguments")
    if type(result) is not Fraction:
        raise Refused("adapter does not export closures")
    return result


def main():
    records = {}
    for name, source in (
        ("report-line", "lambda quantity, price: quantity * price + 5"),
        ("scientific-map", "lambda x: x * x"),
        ("nested-capture", "lambda x: (lambda y: x + y)(3)"),
    ):
        term = parse(Source(name, "1", source))
        records[name] = describe(term)
    print(
        json.dumps(
            {
                "examples": records,
                "scope": {
                    "nomi_source": False,
                    "supplied_inputs": False,
                    "realization": False,
                    "effects": "not-admitted",
                    "binder_choice": "not-selected",
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
