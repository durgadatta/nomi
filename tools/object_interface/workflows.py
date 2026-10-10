"""Engine-free multi-output graph reuse through explicit reference substitution.

This is artifact composition, not callable execution, generic inference or a
new normalizer. Expanded graphs and conditions use the existing contracts.
"""

import json

from .contracts import Requirements
from .documents import ContractError, Frozen, digest, keys, name, snapshot
from .model import Graph, Reference


class Workflow(Frozen):
    __slots__ = ("_document", "_graph", "_requirements", "_context")

    @classmethod
    def from_document(cls, document, vocabulary):
        encoded = snapshot(document)
        document = json.loads(encoded)
        keys(
            document,
            ("version", "id", "revision", "graph", "inputs", "outputs", "requirements"),
            "workflow",
        )
        if type(document["version"]) is not int or document["version"] != 1:
            raise ContractError("unsupported workflow envelope")
        name(document["id"], "workflow identity")
        name(document["revision"], "workflow revision")
        graph = Graph.from_document(document["graph"], vocabulary)
        manifest = vocabulary.document
        source_inputs = {
            identity
            for identity, obj in graph._objects.items()
            if manifest["operations"][obj.op]["role"] == "input"
        }
        for direction in ("inputs", "outputs"):
            ports = document[direction]
            if type(ports) is not dict:
                raise ContractError("workflow interfaces require named references")
            for port, identity in ports.items():
                name(port, "workflow port")
                graph.ref(identity)
        inputs = list(document["inputs"].values())
        if len(inputs) != len(set(inputs)) or set(inputs) != source_inputs:
            raise ContractError(
                "workflow inputs must expose every abstract slot exactly once"
            )
        if not document["outputs"] or set(document["outputs"].values()) != set(
            graph._outputs
        ):
            raise ContractError(
                "workflow outputs must expose the selected template outputs"
            )
        requirements = (
            None
            if document["requirements"] is None
            else Requirements.from_document(document["requirements"], graph)
        )
        result = cls()
        result._document, result._graph, result._requirements = (
            encoded,
            graph,
            requirements,
        )
        result._context = digest(
            {"workflow": document, "envelope": "nomi.object-workflow-1"}
        )
        result._sealed = True
        return result

    @property
    def document(self):
        return json.loads(self._document)

    @property
    def context(self):
        return self._context

    def compose(self, base, namespace, arguments):
        """Expand into a new graph; a prior instance carries its conditions forward."""
        previous = base if type(base) is WorkflowInstance else None
        graph = previous.graph if previous is not None else base
        if (
            type(graph) is not Graph
            or graph.vocabulary.fingerprint != self._graph.vocabulary.fingerprint
        ):
            raise ContractError(
                "workflow composition needs the same checked vocabulary"
            )
        name(namespace, "workflow namespace")
        if previous is not None and any(
            c["namespace"] == namespace for c in previous.inspect()["components"]
        ):
            raise ContractError("workflow namespace is already instantiated")
        document = self.document
        if type(arguments) is not dict or set(arguments) != set(document["inputs"]):
            raise ContractError(
                "supply exactly the declared workflow reference arguments"
            )
        substitutions = {}
        for port, local in document["inputs"].items():
            reference = arguments[port]
            if type(reference) is not Reference or reference._graph is not graph:
                raise ContractError("workflow arguments need this exact graph revision")
            if graph._objects[reference.id].type != self._graph._objects[local].type:
                raise ContractError("workflow argument nominal family mismatch")
            substitutions[local] = reference.id
        for identity in self._graph._objects:
            if identity not in substitutions:
                target = name(
                    namespace + "." + identity, "instantiated object identity"
                )
                if target in graph._objects:
                    raise ContractError(
                        "instantiated workflow object identity collision"
                    )
                substitutions[identity] = target
        expanded = graph.document
        for raw in document["graph"]["objects"]:
            if raw["id"] in document["inputs"].values():
                continue
            expanded["objects"].append(
                {
                    **raw,
                    "id": substitutions[raw["id"]],
                    "ports": {
                        port: [substitutions[r] for r in refs]
                        if type(refs) is list
                        else substitutions[refs]
                        for port, refs in raw["ports"].items()
                    },
                }
            )
        exports = {
            port: substitutions[identity]
            for port, identity in document["outputs"].items()
        }
        for identity in exports.values():
            if identity not in expanded["outputs"]:
                expanded["outputs"].append(identity)
        revised = Graph.from_document(expanded, graph.vocabulary)
        conditions = (
            []
            if previous is None or previous.requirements is None
            else previous.requirements.document["requirements"]
        )
        version = (
            max(2, previous.requirements.document["version"])
            if previous is not None and previous.requirements is not None
            else 2
        )
        if self._requirements is not None:
            source = self._requirements.document
            version = max(version, source["version"])
            for condition in source["requirements"]:
                copied = {
                    **condition,
                    "id": name(
                        namespace + "." + condition["id"],
                        "instantiated requirement identity",
                    ),
                }
                if source["version"] == 4:
                    body = condition["condition"]
                    copied["condition"] = {**body}
                    if body["kind"] == "every":
                        copied["condition"]["subject"] = substitutions[body["subject"]]
                    else:
                        copied["condition"]["operands"] = [
                            {**operand, "subject": substitutions[operand["subject"]]}
                            for operand in body["operands"]
                        ]
                elif source["version"] == 3:
                    copied["operands"] = [
                        {**operand, "subject": substitutions[operand["subject"]]}
                        for operand in condition["operands"]
                    ]
                else:
                    copied.update(
                        subject=substitutions[condition["subject"]],
                        path=condition.get("path", []),
                    )
                conditions.append(copied)
        if version >= 3:
            conditions = [
                condition
                if "operands" in condition or "condition" in condition
                else {
                    "id": condition["id"],
                    "rule": condition["rule"],
                    "operands": [
                        {"subject": condition["subject"], "path": condition["path"]}
                    ],
                }
                for condition in conditions
            ]
        if version == 4:
            conditions = [
                condition
                if "condition" in condition
                else {
                    "id": condition["id"],
                    "condition": {
                        "kind": "relation",
                        "rule": condition["rule"],
                        "operands": condition["operands"],
                    },
                }
                for condition in conditions
            ]
        required = (
            None
            if not conditions
            else Requirements.from_document(
                {
                    "version": version,
                    "graph": revised.context,
                    "owner": "nomi.workflow-composition",
                    "revision": "v1",
                    "requirements": conditions,
                },
                revised,
            )
        )
        components = [] if previous is None else previous.inspect()["components"]
        components.append(
            {
                "workflow": self.context,
                "id": document["id"],
                "revision": document["revision"],
                "namespace": namespace,
                "inputs": {port: reference.id for port, reference in arguments.items()},
                "outputs": exports,
                "requirement_source": None
                if self._requirements is None
                else {
                    "owner": self._requirements.document["owner"],
                    "revision": self._requirements.document["revision"],
                    "context": self._requirements.check()["context"],
                },
            }
        )
        result = WorkflowInstance()
        result._graph, result._requirements = revised, required
        result._exports, result._components = snapshot(exports), snapshot(components)
        result._sealed = True
        return result


class WorkflowInstance(Frozen):
    __slots__ = ("_graph", "_requirements", "_exports", "_components")

    @property
    def graph(self):
        return self._graph

    @property
    def requirements(self):
        return self._requirements

    @property
    def outputs(self):
        return {
            port: self._graph.ref(identity)
            for port, identity in json.loads(self._exports).items()
        }

    def inspect(self):
        return {
            "graph": self._graph.context,
            "components": json.loads(self._components),
            "outputs": json.loads(self._exports),
            "realization": "unbound",
            "requirements": None
            if self._requirements is None
            else self._requirements.check(),
        }

    def compile(self, backend, outputs=None, *, include_condition_inputs=False):
        """Explicitly select an adapter and retain all carried required conditions."""
        from .backend import Backend

        if type(backend) is not Backend:
            raise ContractError(
                "workflow realization needs an explicitly selected backend"
            )
        if type(include_condition_inputs) is not bool:
            raise ContractError("condition-input inclusion must be an explicit boolean")
        if include_condition_inputs and self._requirements is None:
            raise ContractError(
                "condition-input inclusion requires carried requirements"
            )
        compiled = backend.compile(self._graph, outputs)
        return (
            compiled
            if self._requirements is None
            else compiled.require(
                self._requirements, include_condition_inputs=include_condition_inputs
            )
        )

    @property
    def document(self):
        # Reconstruct Graph and Requirements separately using their existing
        # checked loaders. Provenance is inspection data, never a supplied proof.
        return json.loads(
            snapshot(
                {
                    "graph": self._graph.document,
                    "requirements": None
                    if self._requirements is None
                    else self._requirements.document,
                    "inspection": self.inspect(),
                }
            )
        )
