"""Explicit capability negotiation, binding, then realization of pure objects.

Backend implementations are trusted Python code supplied explicitly by the
caller. Vocabulary files never import modules or select executable callbacks.
"""

from dataclasses import dataclass
import json
from types import MappingProxyType

from .documents import (
    ContractError,
    Frozen,
    MAX_BYTES,
    digest,
    encode,
    name,
    snapshot,
    value_check,
)
from .model import Graph, Reference


class Cancelled(RuntimeError):
    """Local cooperative cancellation, distinct from a contract failure."""


class Cancellation:
    def __init__(self):
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def check(self):
        if self._cancelled:
            raise Cancelled("object realization cancelled")


@dataclass(frozen=True)
class BackendFailure(RuntimeError):
    object_ids: tuple[str, ...]
    operation: str

    def __str__(self):
        return f"backend failure at {self.object_ids}, operation {self.operation}"


class Backend(Frozen):
    __slots__ = ("_id", "_revision", "_vocabulary", "_implementations")

    def __init__(self, identity, revision, vocabulary_fingerprint, implementations):
        name(identity, "backend identity")
        name(revision, "backend revision")
        if type(vocabulary_fingerprint) is not str:
            raise ContractError("backend requires a vocabulary fingerprint")
        if type(implementations) is not dict or any(
            type(key) is not str or not callable(value)
            for key, value in implementations.items()
        ):
            raise ContractError(
                "backend requires an explicit operation implementation table"
            )
        self._id, self._revision, self._vocabulary = (
            identity,
            revision,
            vocabulary_fingerprint,
        )
        self._implementations = MappingProxyType(dict(implementations))
        self._sealed = True

    def compile(self, graph, outputs=None):
        if type(graph) is not Graph:
            raise ContractError("expected engine-free graph")
        if graph.vocabulary.fingerprint != self._vocabulary:
            raise ContractError("backend vocabulary fingerprint mismatch")
        if outputs is None:
            selected_ids = graph._outputs
        else:
            if (
                type(outputs) not in (list, tuple)
                or not outputs
                or any(
                    type(ref) is not Reference or ref._graph is not graph
                    for ref in outputs
                )
            ):
                raise ContractError("select references from this exact graph revision")
            selected_ids = tuple(ref.id for ref in outputs)
        if len(selected_ids) != len(set(selected_ids)):
            raise ContractError("duplicate requested output")
        roots = [graph._normal[identity] for identity in selected_ids]
        reachable = set()

        def visit(index):
            if index not in reachable:
                reachable.add(index)
                for _, refs in graph._terms[index][3]:
                    for ref in refs:
                        visit(ref)

        for root in roots:
            visit(root)
        manifest = graph.vocabulary.document
        input_ids = []
        for index in sorted(reachable):
            term = graph._terms[index]
            op, family, identity, _, _ = term
            contract = manifest["operations"][op]
            if contract["role"] == "description":
                raise ContractError(
                    f"{identity}: description has no realization contract"
                )
            if contract["effects"]:
                raise ContractError(
                    f"{op}: effectful realization is outside this pure backend protocol"
                )
            if manifest["types"][family]["value"] is None:
                raise ContractError(f"{op}: nominal family has no value codec")
            if contract["role"] == "apply" and op not in self._implementations:
                raise ContractError(f"unsupported backend operation: {op}")
            if contract["role"] == "input":
                input_ids.append(identity)
        result = Compiled()
        result._graph, result._backend = graph, self
        result._outputs = selected_ids
        result._terms = tuple(sorted(reachable))
        result._inputs = tuple(input_ids)
        result._requirements = None
        result._sealed = True
        return result


class Compiled(Frozen):
    __slots__ = ("_graph", "_backend", "_outputs", "_terms", "_inputs", "_requirements")

    def require(self, requirements):
        from .contracts import Requirements

        if (
            type(requirements) is not Requirements
            or requirements._graph is not self._graph
        ):
            raise ContractError("requirements need this exact graph revision")
        if self._requirements is not None:
            raise ContractError(
                "combine requirements explicitly before attaching a new set"
            )
        manifest = self._graph.vocabulary.document
        for obligation in requirements._obligations:
            for operand in obligation.operands:
                index = self._graph._normal[operand.subject]
                if index not in self._terms:
                    raise ContractError(
                        "requirement subject is outside selected realization"
                    )
                term = self._graph._terms[index]
                if manifest["operations"][term[0]]["role"] not in ("input", "literal"):
                    raise ContractError(
                        "computed preconditions need a richer validator; they cannot be enforced before execution"
                    )
        if requirements.check()["status"] == "refuted":
            raise ContractError("required literal condition is refuted")
        result = Compiled()
        result._graph, result._backend = self._graph, self._backend
        result._outputs, result._terms, result._inputs = (
            self._outputs,
            self._terms,
            self._inputs,
        )
        result._requirements = requirements
        result._sealed = True
        return result

    def origins(self, term):
        """Find source objects for a physical term introduced by a definition."""
        if type(term) is not int or term not in self._terms:
            raise ContractError("unknown compiled physical term")
        direct = tuple(
            identity
            for identity in self._graph._order
            if self._graph._normal[identity] == term
        )
        if direct:
            return direct

        def depends(root):
            visited, stack = set(), [root]
            while stack:
                current = stack.pop()
                if current == term:
                    return True
                if current not in visited:
                    visited.add(current)
                    stack.extend(
                        ref
                        for _, refs in self._graph._terms[current][3]
                        for ref in refs
                    )
            return False

        return tuple(
            identity
            for identity in self._graph._order
            if self._graph._normal[identity] in self._terms
            and depends(self._graph._normal[identity])
        )

    def inspect(self):
        return {
            "status": "capability-checked",
            "context": self._graph.context,
            "vocabulary": self._graph.vocabulary.fingerprint,
            "backend": {"id": self._backend._id, "revision": self._backend._revision},
            "outputs": list(self._outputs),
            "required_inputs": list(self._inputs),
            "logical_to_physical": {
                identity: self._graph._normal[identity]
                for identity in self._graph._order
                if self._graph._normal[identity] in self._terms
            },
            "execution": "not performed",
            "effects": [],
            "requirements": None
            if self._requirements is None
            else self._requirements.check(),
        }

    def bind(self, values):
        encoded = snapshot(values)
        values = json.loads(encoded)
        if type(values) is not dict or set(values) != set(self._inputs):
            raise ContractError(f"binding requires exactly {list(self._inputs)}")
        manifest = self._graph.vocabulary.document
        for identity in self._inputs:
            family = self._graph._objects[identity].type
            value_check(
                values[identity],
                manifest["types"][family]["value"],
                f"binding.{identity}",
            )
        if self._requirements is not None:
            evidence = self._requirements.check(values)
            failed = [
                item["id"]
                for item in evidence["requirements"]
                if item["status"] != "satisfied"
            ]
            if failed:
                raise ContractError(
                    f"required input conditions {failed} are not satisfied; backend was not invoked"
                )
        result = Bound()
        result._compiled, result._bindings = self, encoded
        result._sealed = True
        return result


class Bound(Frozen):
    __slots__ = ("_compiled", "_bindings")

    def execute(self, cancellation=None):
        if cancellation is not None and type(cancellation) is not Cancellation:
            raise ContractError("expected local cancellation token")
        token = cancellation or Cancellation()
        compiled = self._compiled
        graph, backend = compiled._graph, compiled._backend
        manifest = graph.vocabulary.document
        bindings, values, retained_bytes = json.loads(self._bindings), {}, 0
        for index in compiled._terms:
            token.check()
            op, family, identity, ports, attributes = graph._terms[index]
            role = manifest["operations"][op]["role"]
            if role == "input":
                value = bindings[identity]
            elif role == "literal":
                value = json.loads(attributes)["value"]
            else:
                arguments = {
                    port: json.loads(values[refs[0]])
                    if manifest["operations"][op]["ports"][port]["multiplicity"]
                    == "one"
                    else [json.loads(values[ref]) for ref in refs]
                    for port, refs in ports
                }
                try:
                    value = backend._implementations[op](
                        arguments, json.loads(attributes)
                    )
                except Cancelled:
                    raise
                except Exception as exc:
                    origins = compiled.origins(index)
                    raise BackendFailure(origins, op) from exc
            token.check()
            values[index] = snapshot(value)
            retained_bytes += len(values[index].encode())
            if retained_bytes > MAX_BYTES:
                raise ContractError("realization exceeds retained-value byte budget")
            value_check(value, manifest["types"][family]["value"], f"result.{op}")
        materialized = {
            identity: json.loads(values[graph._normal[identity]])
            for identity in compiled._outputs
        }
        receipt = compiled.inspect()
        receipt.update(
            {
                "status": "realized",
                "execution": "completed",
                "binding_digest": digest(bindings),
                "result_digest": digest(materialized),
                "authority": "trusted explicit backend implementation",
                "domain_validity": "not established",
                "requirement_evidence": None
                if compiled._requirements is None
                else compiled._requirements.check(bindings),
            }
        )
        result = Realization()
        result._graph, result._values, result._receipt = (
            graph,
            encode(materialized),
            snapshot(receipt),
        )
        result._sealed = True
        return result


class Realization(Frozen):
    __slots__ = ("_graph", "_values", "_receipt")

    @property
    def values(self):
        return json.loads(self._values)

    @property
    def receipt(self):
        return json.loads(self._receipt)

    def get(self, reference):
        if type(reference) is not Reference or reference._graph is not self._graph:
            raise ContractError(
                "result reference belongs to a different graph revision"
            )
        values = self.values
        if reference.id not in values:
            raise ContractError("reference was not requested for this realization")
        return values[reference.id]
