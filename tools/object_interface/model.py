"""Engine-free typed objects and closed composition definitions.

This is a graph envelope, not Nomi Core or a universal domain algebra. Nominal
families and declared pure definitions belong to each versioned vocabulary.
"""

from dataclasses import dataclass
import json
from types import MappingProxyType

from .documents import (
    ContractError,
    Frozen,
    MAX_NODES,
    digest,
    encode,
    keys,
    name,
    names,
    ordered,
    schema,
    snapshot,
    value_check,
)

ROLES = {"input", "literal", "alias", "apply", "derived", "description"}


@dataclass(frozen=True)
class ObjectSpec:
    id: str
    op: str
    ports: tuple[tuple[str, tuple[str, ...]], ...]
    attributes_json: str
    type: str

    @property
    def dependencies(self):
        return tuple(ref for _, refs in self.ports for ref in refs)


def _objects(raw_objects, operations, external=None, template=False):
    if type(raw_objects) is not list or not 1 <= len(raw_objects) <= MAX_NODES:
        raise ContractError("expected 1..512 named objects")
    objects = {}
    external = external or {}
    for raw in raw_objects:
        keys(raw, ("id", "op", "ports", "attributes"), "object")
        identity = name(raw["id"])
        if identity in objects:
            raise ContractError(f"{identity}: duplicate identity")
        op = raw["op"]
        if type(op) is not str or op not in operations:
            raise ContractError(f"{identity}: unknown operation")
        contract = operations[op]
        if template and (
            contract["role"] in ("input", "description") or contract["effects"]
        ):
            raise ContractError("definitions may compose only pure realizable objects")
        keys(raw["ports"], contract["ports"], f"{identity}.ports")
        keys(raw["attributes"], contract["attributes"], f"{identity}.attributes")
        ports = []
        for port, port_contract in sorted(contract["ports"].items()):
            supplied = raw["ports"][port]
            refs = [supplied] if port_contract["multiplicity"] == "one" else supplied
            if type(refs) is not list:
                raise ContractError(f"{identity}.{port}: expected references")
            for ref in refs:
                if not (template and type(ref) is str and ref in external):
                    name(ref, f"{identity}.{port}")
            ports.append((port, tuple(refs)))
        for key, value in raw["attributes"].items():
            value_check(value, contract["attributes"][key], f"{identity}.{key}")
        objects[identity] = ObjectSpec(
            identity, op, tuple(ports), encode(raw["attributes"]), contract["result"]
        )
    order = ordered(
        {
            identity: tuple(ref for ref in obj.dependencies if ref not in external)
            for identity, obj in objects.items()
        }
    )
    for obj in objects.values():
        for port, refs in obj.ports:
            accepts = operations[obj.op]["ports"][port]["accepts"]
            for ref in refs:
                actual = external[ref] if ref in external else objects[ref].type
                if actual not in accepts:
                    raise ContractError(
                        f"{obj.id}.{port}: expected {accepts}, received {actual}"
                    )
    return objects, order


class Vocabulary(Frozen):
    __slots__ = ("_document", "_templates", "_definition_order", "_fingerprint")

    @classmethod
    def from_document(cls, document):
        encoded = snapshot(document)
        document = json.loads(encoded)
        keys(
            document, ("version", "id", "revision", "types", "operations"), "vocabulary"
        )
        if type(document["version"]) is not int or document["version"] != 1:
            raise ContractError("unsupported vocabulary envelope")
        name(document["id"], "vocabulary identity")
        name(document["revision"], "vocabulary revision")
        types, operations = document["types"], document["operations"]
        if type(types) is not dict or not 1 <= len(types) <= MAX_NODES:
            raise ContractError("invalid nominal family table")
        if type(operations) is not dict or not 1 <= len(operations) <= MAX_NODES:
            raise ContractError("invalid operation table")
        for family, contract in types.items():
            name(family, "nominal family")
            keys(contract, ("value",), family)
            if contract["value"] is not None:
                schema(contract["value"])
        for op, contract in operations.items():
            name(op, "operation")
            keys(
                contract,
                ("role", "ports", "attributes", "result", "effects", "definition"),
                op,
            )
            if type(contract["role"]) is not str or contract["role"] not in ROLES:
                raise ContractError(f"{op}: unknown role")
            if type(contract["result"]) is not str or contract["result"] not in types:
                raise ContractError(f"{op}: unknown result family")
            names(contract["effects"], f"{op}.effects")
            if contract["role"] != "apply" and contract["effects"]:
                raise ContractError("only apply operations may declare effects")
            if (
                type(contract["ports"]) is not dict
                or type(contract["attributes"]) is not dict
            ):
                raise ContractError(f"{op}: invalid ports or attributes")
            for port, port_contract in contract["ports"].items():
                name(port, "port")
                keys(port_contract, ("accepts", "multiplicity"), f"{op}.{port}")
                accepted = names(port_contract["accepts"], f"{op}.{port}.accepts", True)
                if set(accepted) - types.keys() or port_contract[
                    "multiplicity"
                ] not in ("one", "many"):
                    raise ContractError(f"{op}.{port}: invalid port contract")
            for attribute, contract_schema in contract["attributes"].items():
                name(attribute, "attribute")
                schema(contract_schema)
            role = contract["role"]
            if role == "input" and (contract["ports"] or contract["attributes"]):
                raise ContractError("input identity supplies its abstract binding slot")
            if role == "literal" and (
                contract["ports"]
                or set(contract["attributes"]) != {"value"}
                or contract["attributes"]["value"] != types[contract["result"]]["value"]
            ):
                raise ContractError("literal must match the family's value codec")
            if role == "alias" and (
                contract["attributes"]
                or len(contract["ports"]) != 1
                or next(iter(contract["ports"].values()))
                != {"accepts": [contract["result"]], "multiplicity": "one"}
            ):
                raise ContractError("alias must preserve exactly one typed reference")
            if role != "derived" and contract["definition"] is not None:
                raise ContractError("only derived operations have closed definitions")
            if role == "derived" and (
                contract["attributes"]
                or any(
                    port["multiplicity"] != "one" or len(port["accepts"]) != 1
                    for port in contract["ports"].values()
                )
            ):
                raise ContractError(
                    "derived definitions require single closed typed ports and no attributes"
                )
        templates, dependencies = {}, {}
        for op, contract in operations.items():
            if contract["role"] != "derived":
                continue
            definition = contract["definition"]
            keys(definition, ("objects", "output"), f"{op}.definition")
            external = {
                "$" + port: item["accepts"][0]
                for port, item in contract["ports"].items()
            }
            objects, order = _objects(definition["objects"], operations, external, True)
            output = definition["output"]
            if (
                type(output) is not str
                or output not in objects
                or objects[output].type != contract["result"]
            ):
                raise ContractError(f"{op}: definition output has wrong family")
            templates[op] = (MappingProxyType(objects), order, output)
            dependencies[op] = tuple(
                obj.op
                for obj in objects.values()
                if operations[obj.op]["role"] == "derived"
            )
        definition_order = ordered(dependencies)
        result = cls()
        result._document = encoded
        result._templates = MappingProxyType(templates)
        result._definition_order = definition_order
        result._fingerprint = digest(document)
        result._sealed = True
        return result

    @property
    def document(self):
        return json.loads(self._document)

    @property
    def fingerprint(self):
        return self._fingerprint


class _Terms:
    """Structural interning: equality uses terms, not a digest equality oracle."""

    def __init__(self):
        self.index, self.terms = {}, []

    def intern(self, term):
        if term not in self.index:
            if len(self.terms) >= MAX_NODES:
                raise ContractError("expanded composition exceeds node budget")
            self.index[term] = len(self.terms)
            self.terms.append(term)
        return self.index[term]


class Graph(Frozen):
    __slots__ = (
        "_document",
        "_vocabulary",
        "_objects",
        "_order",
        "_outputs",
        "_terms",
        "_normal",
        "_context",
    )

    @classmethod
    def from_document(cls, document, vocabulary):
        if type(vocabulary) is not Vocabulary:
            raise ContractError("expected checked vocabulary")
        encoded = snapshot(document)
        document = json.loads(encoded)
        keys(document, ("version", "vocabulary", "objects", "outputs"), "graph")
        if type(document["version"]) is not int or document["version"] != 1:
            raise ContractError("unsupported graph envelope")
        if document["vocabulary"] != vocabulary.fingerprint:
            raise ContractError("graph requires a different vocabulary fingerprint")
        manifest = vocabulary.document
        operations = manifest["operations"]
        objects, order = _objects(document["objects"], operations)
        outputs = names(document["outputs"], "outputs", True)
        if set(outputs) - objects.keys():
            raise ContractError("unknown output reference")
        terms, normal, expanded = _Terms(), {}, {}

        def lower(obj, environment, nesting=0):
            if nesting > 64:
                raise ContractError("expanded definition exceeds nesting budget")
            contract = operations[obj.op]
            ports = tuple(
                (port, tuple(environment[ref] for ref in refs))
                for port, refs in obj.ports
            )
            if contract["role"] == "alias":
                return ports[0][1][0]
            if contract["role"] == "derived":
                cache_key = (obj.op, ports)
                if cache_key in expanded:
                    return expanded[cache_key]
                local = {"$" + port: refs[0] for port, refs in ports}
                template, template_order, output = vocabulary._templates[obj.op]
                for identity in template_order:
                    local[identity] = lower(template[identity], local, nesting + 1)
                expanded[cache_key] = local[output]
                return expanded[cache_key]
            identity = (
                obj.id
                if contract["role"] in ("input", "description") or contract["effects"]
                else None
            )
            return terms.intern(
                (obj.op, obj.type, identity, ports, obj.attributes_json)
            )

        for identity in order:
            normal[identity] = lower(objects[identity], normal)
        result = cls()
        result._document = encoded
        result._vocabulary = vocabulary
        result._objects = MappingProxyType(objects)
        result._order = order
        result._outputs = outputs
        result._terms = tuple(terms.terms)
        result._normal = MappingProxyType(normal)
        result._context = digest({"graph": document, "envelope": "nomi.object-graph-1"})
        result._sealed = True
        return result

    @property
    def document(self):
        return json.loads(self._document)

    @property
    def context(self):
        return self._context

    @property
    def vocabulary(self):
        return self._vocabulary

    def ref(self, identity):
        if type(identity) is not str or identity not in self._objects:
            raise ContractError("unknown object reference")
        return Reference(self, identity)

    def inspect(self, identity):
        obj = self.ref(identity)._graph._objects[identity]
        contract = self._vocabulary.document["operations"][obj.op]
        return {
            "id": identity,
            "context": self._context,
            "type": obj.type,
            "operation": obj.op,
            "role": contract["role"],
            "ports": {port: list(refs) for port, refs in obj.ports},
            "attributes": json.loads(obj.attributes_json),
            "effects": contract["effects"],
            "normal_reference": self._normal[identity],
            "realization": "unbound",
        }

    def compose(self, identity, op, ports, attributes=None):
        """Add one object in a new revision, using this revision's references.

        No existing object or reference changes. The new named object joins the
        requested outputs; the returned graph owns its new reference context.
        """
        name(identity)
        if identity in self._objects:
            raise ContractError("composition requires a new object identity")
        if type(ports) is not dict:
            raise ContractError("composition requires named reference ports")

        def identity_of(ref):
            if type(ref) is not Reference or ref._graph is not self:
                raise ContractError(
                    "composition requires references from this exact graph revision"
                )
            return ref.id

        references = {
            port: [identity_of(ref) for ref in value]
            if type(value) is list
            else identity_of(value)
            for port, value in ports.items()
        }
        document = self.document
        document["objects"].append(
            {
                "id": identity,
                "op": op,
                "ports": references,
                "attributes": {} if attributes is None else attributes,
            }
        )
        document["outputs"].append(identity)
        return Graph.from_document(document, self._vocabulary)

    def dependencies(self, identity):
        """Logical repair reach and normalized input reach, without an engine."""
        self.ref(identity)
        parents = {
            key: {ref for _, refs in obj.ports for ref in refs}
            for key, obj in self._objects.items()
        }
        closures = {}
        for key in self._order:
            closures[key] = {key}
            for parent in parents[key]:
                closures[key].update(closures[parent])
        physical, stack = set(), [self._normal[identity]]
        while stack:
            index = stack.pop()
            if index not in physical:
                physical.add(index)
                stack.extend(ref for _, refs in self._terms[index][3] for ref in refs)
        operations = self._vocabulary.document["operations"]
        receipt = {
            "version": 1,
            "status": "dependencies-checked",
            "context": self._context,
            "vocabulary": self._vocabulary.fingerprint,
            "subject": identity,
            "logical_dependencies": [
                key
                for key in self._order
                if key != identity and key in closures[identity]
            ],
            "logical_dependents": [
                key
                for key in self._order
                if key != identity and identity in closures[key]
            ],
            "logical_inputs": [
                key
                for key in self._order
                if key in closures[identity]
                and operations[self._objects[key].op]["role"] == "input"
            ],
            "normalized_inputs": [
                self._terms[index][2]
                for index in sorted(physical)
                if operations[self._terms[index][0]]["role"] == "input"
            ],
            "logical_outputs": [
                key for key in self._outputs if identity in closures[key]
            ],
            "execution": "not performed",
            "scope": "declared logical repair reach and normalized input reach; not scheduling, causation or domain proof",
        }
        snapshot(receipt)
        return receipt

    def check(self):
        return {
            "status": "composition-checked",
            "context": self._context,
            "vocabulary": self._vocabulary.fingerprint,
            "scope": "nominal port families, inert attributes and closed definitions",
            "domain_validity": "not established",
            "execution": "not performed",
            "outputs": list(self._outputs),
            "objects": [self.inspect(identity) for identity in self._order],
        }

    def normal_form(self, identity):
        root = self.ref(identity)._graph._normal[identity]
        reachable = set()

        def visit(index):
            if index in reachable:
                return
            reachable.add(index)
            for _, refs in self._terms[index][3]:
                for ref in refs:
                    visit(ref)

        visit(root)
        return {
            "root": root,
            "terms": [
                {
                    "id": index,
                    "op": term[0],
                    "type": term[1],
                    "identity": term[2],
                    "ports": {port: list(refs) for port, refs in term[3]},
                    "attributes": json.loads(term[4]),
                }
                for index, term in enumerate(self._terms)
                if index in reachable
            ],
        }

    def compare(self, left, right):
        self.ref(left)
        self.ref(right)
        equivalent = self._normal[left] == self._normal[right]
        return {
            "version": 1,
            "context": self._context,
            "vocabulary": self._vocabulary.fingerprint,
            "left": left,
            "right": right,
            "status": "equivalent" if equivalent else "unknown",
            "basis": "structural identity after declared pure definitions and aliases",
            "normal_forms": [self.normal_form(left), self.normal_form(right)],
        }

    def verify(self, receipt):
        snapshot(receipt)
        if type(receipt) is not dict or receipt.get("status") != "equivalent":
            raise ContractError("expected equivalent comparison receipt")
        expected = self.compare(receipt.get("left"), receipt.get("right"))
        if encode(receipt) != encode(expected):
            raise ContractError("comparison receipt does not replay in this context")
        return {
            "status": "verified",
            "context": self._context,
            "independent_checker": False,
        }


@dataclass(frozen=True)
class Reference:
    """A graph/revision-qualified semantic reference, never an engine handle."""

    _graph: Graph
    id: str

    def __post_init__(self):
        if (
            type(self._graph) is not Graph
            or type(self.id) is not str
            or self.id not in self._graph._objects
        ):
            raise ContractError(
                "reference requires an existing graph-qualified identity"
            )

    @property
    def context(self):
        return self._graph.context

    def inspect(self):
        return self._graph.inspect(self.id)

    def dependencies(self):
        return self._graph.dependencies(self.id)
