"""Small engine-free obligation protocol, separate from generic type checking.

Closed scalar and structural-path predicates are admitted in this lab. Literal and alias
evidence can discharge them without inputs. Explicit input snapshots can
discharge them at binding. Computed expressions stay pending: no evaluator,
solver, engine callback, or assertion is run to manufacture static evidence.
"""

from dataclasses import dataclass
import json

from .documents import (
    ContractError,
    Frozen,
    MAX_NODES,
    digest,
    encode,
    keys,
    name,
    snapshot,
    schema_at,
    value_at,
    value_check,
)
from .model import Graph

RULES = {
    "exact.positive-v1": ("ExactInt", {"kind": "int"}),
    "text.nonempty-v1": ("Text", {"kind": "text"}),
}
PATH_RULES = {
    "exact.positive-v1": ("int",),
    "text.nonempty-v1": ("text",),
    "array.nonempty-v1": ("array", "text_list"),
}
RELATION_RULES = {
    **{rule: (kinds,) for rule, kinds in PATH_RULES.items()},
    "exact.le-v1": (("int", "positive_int"), ("int", "positive_int")),
    "text.equal-v1": (("text",), ("text",)),
}
CHECKERS = {
    1: "literal-input-predicates-v1",
    2: "structural-path-predicates-v2",
    3: "structural-operand-relations-v3",
    4: "bounded-universal-conditions-v4",
}
SCOPES = {
    1: "closed representation predicates, not scientific assumptions or a general solver",
    2: "closed structural path predicates, not scientific assumptions or a general solver",
    3: "closed structural operand relations, not nominal equality, scientific assumptions or a general solver",
    4: "bounded structural universal conditions and relations, not scientific assumptions or a general solver",
}
MAX_ITEM_CHECKS = 4096
MAX_FAILURES = 128


class RequirementContractError(ContractError):
    """A required condition failed; its replayable evidence remains inspectable."""

    def __init__(self, message, report):
        self._report = snapshot(report)
        super().__init__(message)

    @property
    def report(self):
        return json.loads(self._report)


def _predicate(rule, values):
    if rule == "exact.le-v1":
        return values[0] <= values[1]
    if rule == "text.equal-v1":
        return values[0] == values[1]
    if rule == "exact.positive-v1":
        return values[0] > 0
    if rule in ("text.nonempty-v1", "array.nonempty-v1"):
        return len(values[0]) > 0
    raise ContractError("no reviewed predicate implementation for this rule")


@dataclass(frozen=True)
class Operand:
    subject: str
    path: tuple[str | int, ...] = ()


@dataclass(frozen=True)
class Obligation:
    id: str
    rule: str
    operands: tuple[Operand, ...]
    item_path: tuple[str | int, ...] | None = None


class Requirements(Frozen):
    __slots__ = ("_graph", "_document", "_obligations", "_context")

    @classmethod
    def from_document(cls, document, graph):
        if type(graph) is not Graph:
            raise ContractError("requirements need a checked object graph")
        encoded = snapshot(document)
        document = json.loads(encoded)
        keys(
            document,
            ("version", "graph", "owner", "revision", "requirements"),
            "requirements",
        )
        if type(document["version"]) is not int or document["version"] not in CHECKERS:
            raise ContractError("unsupported requirement envelope")
        if document["graph"] != graph.context:
            raise ContractError("requirements belong to a different graph context")
        name(document["owner"], "requirement owner")
        name(document["revision"], "requirement revision")
        raw = document["requirements"]
        if type(raw) is not list or not 1 <= len(raw) <= MAX_NODES:
            raise ContractError("expected bounded nonempty requirements")
        obligations = []
        identities = set()
        manifest = graph.vocabulary.document
        for requirement in raw:
            version = document["version"]
            keys(
                requirement,
                ("id", "rule", "subject")
                if version == 1
                else ("id", "rule", "subject", "path")
                if version == 2
                else ("id", "rule", "operands")
                if version == 3
                else ("id", "condition"),
                "requirement",
            )
            identity = name(requirement["id"], "requirement identity")
            if identity in identities:
                raise ContractError("duplicate requirement identity")
            identities.add(identity)
            if version == 4:
                condition = requirement["condition"]
                if type(condition) is not dict:
                    raise ContractError("expected a closed condition record")
                if condition.get("kind") == "every":
                    keys(
                        condition,
                        ("kind", "rule", "subject", "path", "item_path"),
                        "universal condition",
                    )
                    rule = condition["rule"]
                    if type(rule) is not str or rule not in PATH_RULES:
                        raise ContractError(
                            "universal condition requires a closed unary rule"
                        )
                    subject = graph.ref(condition["subject"])
                    codec = manifest["types"][graph._objects[subject.id].type]["value"]
                    if codec is None:
                        raise ContractError("universal subject has no value codec")
                    collection = schema_at(codec, condition["path"])
                    if collection["kind"] == "text_list":
                        item_codec = {"kind": "text"}
                    elif collection["kind"] == "array" and "items" in collection:
                        item_codec = collection["items"]
                    else:
                        raise ContractError(
                            "universal condition requires declared collection items"
                        )
                    if (
                        schema_at(item_codec, condition["item_path"])["kind"]
                        not in PATH_RULES[rule]
                    ):
                        raise ContractError(
                            "universal rule disagrees with the declared item kind"
                        )
                    obligations.append(
                        Obligation(
                            identity,
                            rule,
                            (Operand(subject.id, tuple(condition["path"])),),
                            tuple(condition["item_path"]),
                        )
                    )
                    continue
                keys(condition, ("kind", "rule", "operands"), "relation condition")
                if condition["kind"] != "relation":
                    raise ContractError("unknown condition composition")
                requirement = {
                    "id": identity,
                    "rule": condition["rule"],
                    "operands": condition["operands"],
                }
                version = 3
            rule = requirement["rule"]
            if type(rule) is not str or rule not in (
                RULES
                if version == 1
                else PATH_RULES
                if version == 2
                else RELATION_RULES
            ):
                raise ContractError("unknown refinement rule")
            if version == 3:
                raw_operands = requirement["operands"]
                kinds = RELATION_RULES[rule]
                if type(raw_operands) is not list or len(raw_operands) != len(kinds):
                    raise ContractError("relation requires its declared operand count")
                operands = []
                for raw_operand, admitted in zip(raw_operands, kinds):
                    keys(raw_operand, ("subject", "path"), "requirement operand")
                    subject = graph.ref(raw_operand["subject"])
                    family = graph._objects[subject.id].type
                    codec = manifest["types"][family]["value"]
                    if codec is None:
                        raise ContractError("relation operand has no value codec")
                    if schema_at(codec, raw_operand["path"])["kind"] not in admitted:
                        raise ContractError(
                            "relation disagrees with the declared operand kind"
                        )
                    operands.append(Operand(subject.id, tuple(raw_operand["path"])))
                obligations.append(Obligation(identity, rule, tuple(operands)))
                continue
            subject = graph.ref(requirement["subject"])
            actual_family = graph._objects[subject.id].type
            actual_codec = manifest["types"][actual_family]["value"]
            path = ()
            if version == 1:
                family, codec = RULES[rule]
                if actual_family != family or actual_codec != codec:
                    raise ContractError(
                        f"{identity}: refinement rule requires {family} with its declared value codec"
                    )
            else:
                if actual_codec is None:
                    raise ContractError("path requirement subject has no value codec")
                selected = schema_at(actual_codec, requirement["path"])
                if selected["kind"] not in PATH_RULES[rule]:
                    raise ContractError(
                        "refinement rule disagrees with the declared path kind"
                    )
                path = tuple(requirement["path"])
            obligations.append(Obligation(identity, rule, (Operand(subject.id, path),)))
        result = cls()
        result._graph, result._document = graph, encoded
        result._obligations = tuple(obligations)
        result._context = digest(
            {
                "requirements": document,
                "checker": CHECKERS[document["version"]],
            }
        )
        result._sealed = True
        return result

    @property
    def document(self):
        return json.loads(self._document)

    def check(self, bindings=None):
        version = self.document["version"]
        supplied = {} if bindings is None else json.loads(snapshot(bindings))
        if type(supplied) is not dict:
            raise ContractError("refinement bindings must be input-slot records")
        manifest = self._graph.vocabulary.document
        for identity, value in supplied.items():
            self._graph.ref(identity)
            obj = self._graph._objects[identity]
            if manifest["operations"][obj.op]["role"] != "input":
                raise ContractError(
                    "only abstract input slots accept refinement bindings"
                )
            codec = manifest["types"][obj.type]["value"]
            if codec is None:
                raise ContractError("refinement binding has no value codec")
            value_check(value, codec, f"refinement binding.{identity}")
        results = []
        item_checks = 0
        for obligation in self._obligations:
            evidence = [
                self._operand_evidence(operand, supplied, manifest)
                for operand in obligation.operands
            ]
            if obligation.item_path is not None:
                result, checked_items = self._every_result(
                    obligation, evidence[0], MAX_ITEM_CHECKS - item_checks
                )
                item_checks += checked_items
                results.append(result)
                continue
            if any(item[0] == "missing" for item in evidence):
                status = "refuted"
            elif any(item[0] == "pending" for item in evidence):
                status = "pending"
            else:
                values = [item[1] for item in evidence]
                passed = _predicate(obligation.rule, values)
                status = "satisfied" if passed else "refuted"
            result = {"id": obligation.id, "rule": obligation.rule, "status": status}
            if version >= 3:
                result["operands"] = [
                    {
                        "subject": operand.subject,
                        "path": list(operand.path),
                        "status": item[0],
                        "basis": item[2],
                    }
                    for operand, item in zip(obligation.operands, evidence)
                ]
                if version == 4:
                    result = {
                        "id": obligation.id,
                        "status": status,
                        "condition": {
                            "kind": "relation",
                            "rule": obligation.rule,
                            "operands": result["operands"],
                        },
                    }
            else:
                result.update(
                    subject=obligation.operands[0].subject, basis=evidence[0][2]
                )
                if version == 2:
                    result["path"] = list(obligation.operands[0].path)
            results.append(result)
        statuses = {item["status"] for item in results}
        status = (
            "refuted"
            if "refuted" in statuses
            else "pending"
            if "pending" in statuses
            else "satisfied"
        )
        receipt = {
            "version": version,
            "context": self._context,
            "graph": self._graph.context,
            "status": status,
            "evidence_phase": "static" if bindings is None else "binding",
            "binding_digest": None if bindings is None else digest(supplied),
            "requirements": results,
            "scope": SCOPES[version],
        }
        snapshot(receipt)
        return receipt

    def _every_result(self, obligation, evidence, budget):
        operand = obligation.operands[0]
        state, value, basis = evidence
        condition = {
            "kind": "every",
            "subject": operand.subject,
            "path": list(operand.path),
            "item_path": list(obligation.item_path),
            "rule": obligation.rule,
            "basis": basis,
            "checked_items": 0,
            "total_items": None,
            "failures": [],
            "failures_complete": True,
        }
        status = "pending"
        if state == "missing":
            status = "refuted"
            condition["failures"].append(
                {"path": list(operand.path), "code": "missing-collection-path"}
            )
        elif state == "known":
            if len(value) > budget:
                raise ContractError("universal condition item-check budget exceeded")
            condition["checked_items"] = condition["total_items"] = len(value)
            status = "satisfied"
            for index, item in enumerate(value):
                exists, selected = value_at(item, obligation.item_path)
                if not exists or not _predicate(obligation.rule, [selected]):
                    status = "refuted"
                    if len(condition["failures"]) < MAX_FAILURES:
                        condition["failures"].append(
                            {
                                "path": list(operand.path)
                                + [index]
                                + list(obligation.item_path),
                                "code": "predicate-refuted"
                                if exists
                                else "missing-item-path",
                            }
                        )
                    else:
                        condition["failures_complete"] = False
        return {
            "id": obligation.id,
            "status": status,
            "condition": condition,
        }, condition["checked_items"]

    def _operand_evidence(self, operand, supplied, manifest):
        term = self._graph._terms[self._graph._normal[operand.subject]]
        op, _, identity, _, attributes = term
        role = manifest["operations"][op]["role"]
        known, value, basis = False, None, "unresolved expression"
        if role == "literal":
            known, value, basis = (
                True,
                json.loads(attributes)["value"],
                "declared literal",
            )
        elif role == "input" and identity in supplied:
            known, value, basis = (
                True,
                supplied[identity],
                "explicit input snapshot",
            )
        if not known:
            return "pending", None, basis
        exists, selected = value_at(value, operand.path)
        return (
            ("known", selected, basis)
            if exists
            else ("missing", None, basis + "; missing path")
        )

    def inspect(self, identity):
        if type(identity) is not str:
            raise ContractError("unknown requirement identity")
        for obligation in self.check()["requirements"]:
            if obligation["id"] == identity:
                return {
                    "context": self._context,
                    "graph": self._graph.context,
                    **obligation,
                }
        raise ContractError("unknown requirement identity")

    def verify(self, receipt, bindings=None):
        snapshot(receipt)
        expected = self.check(bindings)
        if encode(receipt) != encode(expected):
            raise ContractError("requirement evidence does not replay in this context")
        return {
            "status": "verified",
            "verdict": expected["status"],
            "context": self._context,
            "independent_checker": False,
        }
