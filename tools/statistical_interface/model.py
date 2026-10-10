"""Closed, schema-only DAG checker and bounded definitional equivalence.

No data binding, engine discovery, evaluation, callbacks, or source resolution.
The tracked catalog describes ports; closed Python rules are the trusted theory.
"""

from collections import deque
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import re
from types import MappingProxyType


CATALOG_PATH = Path(__file__).resolve().parents[2] / "config/data_interface.json"
MAX_BYTES = 1_000_000
MAX_NODES = 512
MAX_DEPTH = 64
DTYPES = {"ExactInt", "ExactRational", "Float64", "Bool", "Text"}
NUMERIC = {"ExactInt", "ExactRational", "Float64"}
EXACT = {"ExactInt", "ExactRational"}
IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z_0-9.-]{0,127}\Z")


class PlanError(ValueError):
    """Invalid or unsupported interface contract, never a data failure."""


def _digest(value):
    return hashlib.sha256(_encode(value).encode()).hexdigest()


def _encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise PlanError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_document(path):
    with Path(path).open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise PlanError("document exceeds byte budget")
    try:
        return json.loads(
            data,
            object_pairs_hook=_pairs,
            parse_constant=lambda token: _reject_constant(token),
        )
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise PlanError(f"invalid JSON: {exc}") from exc


def _reject_constant(token):
    raise PlanError(f"non-JSON numeric constant: {token}")


def _plain(value, depth=0):
    if depth > MAX_DEPTH:
        raise PlanError("document exceeds nesting budget")
    if type(value) is dict:
        for key, child in value.items():
            if type(key) is not str:
                raise PlanError("object keys must be strings")
            _plain(child, depth + 1)
    elif type(value) is list:
        for child in value:
            _plain(child, depth + 1)
    elif type(value) not in (str, int, bool, type(None)):
        raise PlanError("only inert JSON objects, arrays, strings and integers allowed")


def _keys(value, required, optional=(), where="document"):
    if type(value) is not dict:
        raise PlanError(f"{where}: expected object")
    missing = set(required) - value.keys()
    extra = value.keys() - set(required) - set(optional)
    if missing or extra:
        raise PlanError(f"{where}: missing {sorted(missing)}, unknown {sorted(extra)}")


def _name(value, where):
    if type(value) is not str or not IDENTIFIER.fullmatch(value):
        raise PlanError(f"{where}: expected bounded identifier")
    return value


@dataclass(frozen=True)
class Field:
    name: str
    dtype: str
    nullable: bool


@dataclass(frozen=True)
class ObjectType:
    kind: str
    dtype: str | None = None
    nullable: bool = False
    domain: str | None = None
    fields: tuple[Field, ...] = ()


@dataclass(frozen=True)
class Node:
    id: str
    op: str
    args: tuple[str, ...]
    field: str | None = None
    schema: tuple[Field, ...] = ()


# The catalog can describe more families without making them executable.
RULES = {
    "input": (0, "input", ("schema",)),
    "column": (1, "column", ("field",)),
    "alias": (1, "alias", ()),
    "filter": (2, "filter", ()),
    "add": (2, "numeric", ()),
    "subtract": (2, "numeric", ()),
    "multiply": (2, "numeric", ()),
    "greater": (2, "compare", ()),
    "sum": (1, "sum", ()),
    "count_valid": (1, "count_valid", ()),
    "count_rows": (1, "count_rows", ()),
    "mean": (1, "mean", ()),
    "safe_divide": (2, "safe_divide", ()),
}


def catalog():
    result = load_document(CATALOG_PATH)
    if result.get("version") != 1:
        raise PlanError("unsupported catalog version")
    operations = result.get("operations", {})
    if set(operations) != set(RULES):
        raise PlanError("catalog/checker operation disagreement")
    for op, (arity, rule, attributes) in RULES.items():
        if operations[op] != {
            "arity": arity,
            "type_rule": rule,
            "attributes": list(attributes),
        }:
            raise PlanError(f"catalog/checker contract disagreement: {op}")
    return result


class Plan:
    """Immutable named graph. Construct with Plan.from_document(JSON object).

    A proof is relative to the declared schema and fixed theory, not evidence
    that future bindings or an execution engine satisfy either contract.
    """

    __slots__ = (
        "_document",
        "_nodes",
        "_types",
        "_terms",
        "_steps",
        "_order",
        "_outputs",
        "_profile",
        "_context",
        "_sealed",
    )

    def __setattr__(self, name, value):
        if getattr(self, "_sealed", False):
            raise AttributeError("plans are immutable; construct a new revision")
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        raise AttributeError("plans are immutable; construct a new revision")

    @classmethod
    def from_document(cls, document):
        _plain(document)
        _keys(document, ("version", "profile", "nodes", "outputs"))
        if type(document["version"]) is not int or document["version"] != 1:
            raise PlanError("unsupported plan version")
        if document["profile"] not in ("exact-rational-v1", "float64-opaque-v1"):
            raise PlanError("unsupported numeric profile")
        if (
            type(document["nodes"]) is not list
            or not 1 <= len(document["nodes"]) <= MAX_NODES
        ):
            raise PlanError(f"expected 1..{MAX_NODES} nodes")
        encoded = _encode(document)
        if len(encoded.encode()) > MAX_BYTES:
            raise PlanError("document exceeds byte budget")
        nodes = {}
        for raw in document["nodes"]:
            _keys(raw, ("id", "op", "args"), ("field", "schema"), "node")
            name = _name(raw["id"], "node id")
            op = raw["op"]
            if type(op) is not str or op not in RULES:
                raise PlanError(f"{name}: unsupported operation")
            if name in nodes:
                raise PlanError(f"{name}: duplicate node identity")
            arity, _, attributes = RULES[op]
            _keys(raw, ("id", "op", "args", *attributes), where=name)
            args = raw["args"]
            if type(args) is not list or len(args) != arity:
                raise PlanError(f"{name}: expected {arity} input references")
            args = tuple(_name(arg, name) for arg in args)
            schema = ()
            if op == "input":
                if (
                    type(raw["schema"]) is not list
                    or not 1 <= len(raw["schema"]) <= 128
                ):
                    raise PlanError(f"{name}: expected 1..128 fields")
                fields = []
                for field in raw["schema"]:
                    _keys(field, ("name", "dtype", "nullable"), where=name)
                    field_name = _name(field["name"], name)
                    if type(field["dtype"]) is not str or field["dtype"] not in DTYPES:
                        raise PlanError(f"{name}.{field_name}: unsupported dtype")
                    if type(field["nullable"]) is not bool:
                        raise PlanError(f"{name}.{field_name}: nullable must be Bool")
                    fields.append(Field(field_name, field["dtype"], field["nullable"]))
                if len({field.name for field in fields}) != len(fields):
                    raise PlanError(f"{name}: duplicate field name")
                schema = tuple(fields)
            field = _name(raw["field"], name) if op == "column" else None
            nodes[name] = Node(name, op, args, field, schema)
        outputs = document["outputs"]
        if type(outputs) is not list or not outputs:
            raise PlanError("outputs must be a nonempty reference list")
        for output in outputs:
            _name(output, "output")
            if output not in nodes:
                raise PlanError(f"unknown output: {output}")
        if len(set(outputs)) != len(outputs):
            raise PlanError("duplicate output reference")
        order = _topological(nodes)
        result = cls()
        result._document = encoded
        result._nodes = MappingProxyType(nodes)
        result._profile = document["profile"]
        result._outputs = tuple(outputs)
        result._order = tuple(order)
        result._context = _digest(
            {"plan": document, "catalog": catalog(), "checker": 1}
        )
        types, terms, steps = {}, {}, []
        for name in order:
            node = nodes[name]
            types[name] = _infer(node, [types[arg] for arg in node.args])
            term_args = [terms[arg] for arg in node.args]
            if node.op == "alias":
                terms[name] = term_args[0]
                steps.append({"node": name, "rule": "alias-reference-v1"})
            elif (
                node.op == "mean"
                and result._profile == "exact-rational-v1"
                and types[node.args[0]].dtype in EXACT
            ):
                terms[name] = _digest(
                    [
                        "safe_divide",
                        _digest(["sum", *term_args]),
                        _digest(["count_valid", *term_args]),
                    ]
                )
                steps.append({"node": name, "rule": "mean-valid-exact-v1"})
            elif node.op == "input":
                terms[name] = _digest(["input", name, [asdict(f) for f in node.schema]])
            elif node.op == "column":
                terms[name] = _digest(["column", *term_args, node.field])
            else:
                terms[name] = _digest([node.op, *term_args])
            # Relation identity is semantic, so aliases preserve alignment.
            if types[name].kind == "relation":
                types[name] = ObjectType(
                    "relation", domain=terms[name], fields=types[name].fields
                )
        result._types = MappingProxyType(types)
        result._terms = MappingProxyType(terms)
        result._steps = tuple(MappingProxyType(step) for step in steps)
        result._sealed = True
        return result

    @property
    def document(self):
        return json.loads(self._document)

    def inspect(self, name):
        if type(name) is not str or name not in self._nodes:
            raise PlanError(f"unknown node: {name}")
        node = self._nodes[name]
        return {
            "id": name,
            "op": node.op,
            "inputs": list(node.args),
            "type": asdict(self._types[name]),
            "normal_form": self._terms[name],
        }

    def check(self):
        return {
            "status": "checked",
            "context": self._context,
            "profile": self._profile,
            "theory": "statistical-interface-v1",
            "outputs": list(self._outputs),
            "nodes": [self.inspect(name) for name in self._order],
            "data_access": "none",
            "execution": "not implemented",
        }

    def prove(self, left, right):
        lhs, rhs = self.inspect(left), self.inspect(right)
        equivalent = (
            lhs["type"] == rhs["type"] and lhs["normal_form"] == rhs["normal_form"]
        )
        ancestors = set()
        pending = [left, right]
        while pending:
            name = pending.pop()
            if name not in ancestors:
                ancestors.add(name)
                pending.extend(self._nodes[name].args)
        return {
            "version": 1,
            "status": "equivalent" if equivalent else "unknown",
            "context": self._context,
            "profile": self._profile,
            "theory": "statistical-interface-v1",
            "left": left,
            "right": right,
            "normal_forms": [lhs["normal_form"], rhs["normal_form"]],
            "steps": [dict(step) for step in self._steps if step["node"] in ancestors],
            "reason": "same typed normal form"
            if equivalent
            else "closed rules do not establish equality",
        }

    def verify(self, certificate):
        _plain(certificate)
        if type(certificate) is not dict or certificate.get("status") != "equivalent":
            return False
        try:
            expected = self.prove(certificate.get("left"), certificate.get("right"))
        except PlanError:
            return False
        return _encode(certificate) == _encode(expected)


def _topological(nodes):
    indegree = {name: len(set(node.args)) for name, node in nodes.items()}
    users = {name: [] for name in nodes}
    for name, node in nodes.items():
        for arg in set(node.args):
            if arg not in nodes:
                raise PlanError(f"{name}: unknown reference {arg}")
            users[arg].append(name)
    pending = deque(name for name, degree in indegree.items() if degree == 0)
    order, depths = [], {}
    while pending:
        name = pending.popleft()
        depths[name] = 1 + max((depths[arg] for arg in nodes[name].args), default=0)
        if depths[name] > MAX_DEPTH:
            raise PlanError("graph exceeds depth budget")
        order.append(name)
        for user in users[name]:
            indegree[user] -= 1
            if indegree[user] == 0:
                pending.append(user)
    if len(order) != len(nodes):
        raise PlanError("cyclic graph: a lazy DAG cannot express this feedback")
    return order


def _infer(node, args):
    def require(condition, message):
        if not condition:
            raise PlanError(f"{node.id}: {message}")

    rule = RULES[node.op][1]
    if rule == "input":
        return ObjectType("relation", fields=node.schema)
    first = args[0]
    if rule == "alias":
        return first
    if rule == "column":
        require(first.kind == "relation", "column requires a relation")
        field = next(
            (field for field in first.fields if field.name == node.field), None
        )
        require(field is not None, f"unknown field {node.field}")
        return ObjectType("column", field.dtype, field.nullable, first.domain)
    if rule == "filter":
        mask = args[1]
        require(
            first.kind == "relation" and mask.kind == "column" and mask.dtype == "Bool",
            "filter requires a relation and Bool column",
        )
        require(
            first.domain == mask.domain, "mask belongs to another observation domain"
        )
        require(not mask.nullable, "nullable mask policy is not implemented")
        return ObjectType("relation", fields=first.fields)
    if rule == "count_rows":
        require(first.kind == "relation", "count_rows requires a relation")
        return ObjectType("scalar", "ExactInt")
    if rule in ("sum", "count_valid", "mean"):
        require(first.kind == "column", "aggregation requires a column")
        if rule == "count_valid":
            return ObjectType("scalar", "ExactInt")
        require(first.dtype in NUMERIC, "numeric aggregation excludes Bool and Text")
        dtype = "Float64" if first.dtype == "Float64" else "ExactRational"
        return ObjectType("scalar", dtype, rule == "mean")
    second = args[1]
    if rule == "safe_divide":
        require(
            first.kind == second.kind == "scalar"
            and first.dtype in NUMERIC
            and second.dtype in NUMERIC,
            "safe_divide requires two numeric scalars",
        )
        dtype = (
            "Float64" if "Float64" in (first.dtype, second.dtype) else "ExactRational"
        )
        return ObjectType("scalar", dtype, True)
    require(first.kind == second.kind == "column", "operation requires two columns")
    require(
        first.domain == second.domain, "columns belong to different observation domains"
    )
    require(
        first.dtype in NUMERIC and second.dtype in NUMERIC,
        "operation requires numeric columns",
    )
    require(
        (first.dtype == "Float64") == (second.dtype == "Float64"),
        "mixed exact/Float64 conversion must be explicit; conversion is not implemented",
    )
    dtype = (
        "Bool"
        if rule == "compare"
        else ("Float64" if first.dtype == "Float64" else "ExactRational")
    )
    return ObjectType("column", dtype, first.nullable or second.nullable, first.domain)
