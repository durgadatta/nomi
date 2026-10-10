"""Small engine-free obligation protocol, separate from generic type checking.

Only two representation predicates are admitted in this lab. Literal and alias
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
    value_check,
)
from .model import Graph

RULES = {
    "exact.positive-v1": ("ExactInt", {"kind": "int"}),
    "text.nonempty-v1": ("Text", {"kind": "text"}),
}


@dataclass(frozen=True)
class Obligation:
    id: str
    rule: str
    subject: str


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
        if type(document["version"]) is not int or document["version"] != 1:
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
            keys(requirement, ("id", "rule", "subject"), "requirement")
            identity = name(requirement["id"], "requirement identity")
            if identity in identities:
                raise ContractError("duplicate requirement identity")
            identities.add(identity)
            rule = requirement["rule"]
            if type(rule) is not str or rule not in RULES:
                raise ContractError("unknown refinement rule")
            subject = graph.ref(requirement["subject"])
            family, codec = RULES[rule]
            if (
                graph._objects[subject.id].type != family
                or manifest["types"][family]["value"] != codec
            ):
                raise ContractError(
                    f"{identity}: refinement rule requires {family} with its declared value codec"
                )
            obligations.append(Obligation(identity, rule, subject.id))
        result = cls()
        result._graph, result._document = graph, encoded
        result._obligations = tuple(obligations)
        result._context = digest(
            {"requirements": document, "checker": "literal-input-predicates-v1"}
        )
        result._sealed = True
        return result

    @property
    def document(self):
        return json.loads(self._document)

    def check(self, bindings=None):
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
        for obligation in self._obligations:
            term = self._graph._terms[self._graph._normal[obligation.subject]]
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
            if known:
                passed = (
                    value > 0
                    if obligation.rule == "exact.positive-v1"
                    else len(value) > 0
                )
                status = "satisfied" if passed else "refuted"
            else:
                status = "pending"
            results.append(
                {
                    "id": obligation.id,
                    "subject": obligation.subject,
                    "rule": obligation.rule,
                    "status": status,
                    "basis": basis,
                }
            )
        statuses = {item["status"] for item in results}
        status = (
            "refuted"
            if "refuted" in statuses
            else "pending"
            if "pending" in statuses
            else "satisfied"
        )
        return {
            "version": 1,
            "context": self._context,
            "graph": self._graph.context,
            "status": status,
            "evidence_phase": "static" if bindings is None else "binding",
            "binding_digest": None if bindings is None else digest(supplied),
            "requirements": results,
            "scope": "closed representation predicates, not scientific assumptions or a general solver",
        }

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
