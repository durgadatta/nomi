"""Catalog-driven statistical description ports, separate from executable plans."""

from dataclasses import dataclass
from types import MappingProxyType
import json

from .model import (
    MAX_BYTES,
    MAX_NODES,
    Node,
    PlanError,
    _encode,
    _digest,
    _keys,
    _name,
    _plain,
    _topological,
    catalog,
)


@dataclass(frozen=True)
class Description:
    id: str
    family: str
    ports: tuple[tuple[str, tuple[str, ...]], ...]
    parameters_json: str


def _parameter(value, contract, where):
    kind = contract["kind"]
    valid = {
        "text": lambda: type(value) is str and bool(value),
        "bool": lambda: type(value) is bool,
        "positive_int": lambda: type(value) is int and value > 0,
        "record": lambda: type(value) is dict,
        "array": lambda: type(value) is list,
        "text_list": lambda: (
            type(value) is list and all(type(item) is str for item in value)
        ),
        "enum": lambda: type(value) is str and value in contract["values"],
    }
    if kind not in valid or not valid[kind]():
        raise PlanError(f"{where}: expected declared parameter kind {kind}")


class ObjectGraph:
    """Immutable descriptions of contracts, not instances of realized statistics.

    This checker validates reference families and inert parameter shapes. It
    never interprets formulas, algorithms, assumptions or scientific evidence.
    """

    __slots__ = ("_objects", "_order", "_outputs", "_document", "_context", "_sealed")

    def __setattr__(self, key, value):
        if getattr(self, "_sealed", False):
            raise AttributeError("object descriptions are immutable")
        object.__setattr__(self, key, value)

    def __delattr__(self, key):
        raise AttributeError("object descriptions are immutable")

    @classmethod
    def from_document(cls, document):
        _plain(document)
        _keys(document, ("version", "objects", "outputs"))
        if type(document["version"]) is not int or document["version"] != 1:
            raise PlanError("unsupported object envelope version")
        if (
            type(document["objects"]) is not list
            or not 1 <= len(document["objects"]) <= MAX_NODES
        ):
            raise PlanError("object count exceeds budget")
        encoded = _encode(document)
        if len(encoded.encode()) > MAX_BYTES:
            raise PlanError("object document exceeds byte budget")
        catalog_document = catalog()
        if (
            type(catalog_document.get("object_envelope_version")) is not int
            or catalog_document["object_envelope_version"] != 1
        ):
            raise PlanError("unsupported catalog object envelope")
        families = {family["id"]: family for family in catalog_document["families"]}
        objects = {}
        for raw in document["objects"]:
            _keys(raw, ("id", "family", "ports", "parameters"), where="object")
            name, family = _name(raw["id"], "object id"), raw["family"]
            if name in objects:
                raise PlanError(f"{name}: duplicate object identity")
            if type(family) is not str or family not in families:
                raise PlanError(f"{name}: unknown statistical family")
            contract = families[family]
            _keys(raw["ports"], contract["ports"], where=f"{name}.ports")
            _keys(raw["parameters"], contract["parameters"], where=f"{name}.parameters")
            ports = []
            for key, specification in contract["ports"].items():
                value = raw["ports"][key]
                if specification["multiplicity"] == "one":
                    refs = (_name(value, f"{name}.{key}"),)
                else:
                    if type(value) is not list:
                        raise PlanError(f"{name}.{key}: expected reference list")
                    refs = tuple(_name(ref, f"{name}.{key}") for ref in value)
                    if len(refs) != len(set(refs)):
                        raise PlanError(f"{name}.{key}: duplicate reference")
                ports.append((key, refs))
            for key, specification in contract["parameters"].items():
                _parameter(raw["parameters"][key], specification, f"{name}.{key}")
            objects[name] = Description(
                name, family, tuple(ports), _encode(raw["parameters"])
            )
        dependencies = {}
        for name, description in objects.items():
            refs = []
            for port, values in description.ports:
                expected = families[description.family]["ports"][port]["families"]
                for ref in values:
                    if ref not in objects:
                        raise PlanError(f"{name}.{port}: unknown reference {ref}")
                    if objects[ref].family not in expected:
                        raise PlanError(
                            f"{name}.{port}: expected family {expected}, received {objects[ref].family}"
                        )
                    refs.append(ref)
            dependencies[name] = Node(name, "description", tuple(refs))
        order = _topological(dependencies)
        if type(document["outputs"]) is not list or not document["outputs"]:
            raise PlanError("object outputs must be nonempty references")
        for output in document["outputs"]:
            _name(output, "object output")
            if output not in objects:
                raise PlanError(f"unknown object output {output}")
        if len(set(document["outputs"])) != len(document["outputs"]):
            raise PlanError("duplicate object output")
        result = cls()
        result._objects = MappingProxyType(objects)
        result._order = tuple(order)
        result._outputs = tuple(document["outputs"])
        result._document = encoded
        result._context = _digest(
            {"document": document, "catalog": catalog_document, "envelope": 1}
        )
        result._sealed = True
        return result

    @property
    def document(self):
        return json.loads(self._document)

    def inspect(self, name):
        if type(name) is not str or name not in self._objects:
            raise PlanError("unknown statistical description")
        description = self._objects[name]
        return {
            "id": description.id,
            "context": self._context,
            "family": description.family,
            "ports": {key: list(refs) for key, refs in description.ports},
            "parameters": json.loads(description.parameters_json),
            "realization": "description only",
        }

    def check(self):
        return {
            "status": "description-checked",
            "context": self._context,
            "scope": "reference families and parameter shapes",
            "scientific_validity": "not established",
            "execution": "not implemented",
            "outputs": list(self._outputs),
            "objects": [self.inspect(name) for name in self._order],
        }
