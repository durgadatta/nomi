"""Checked atomic replacement of named objects; no engine or contract migration."""

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
)
from .model import Graph


class Revision(Frozen):
    __slots__ = ("_document", "_source", "_graph", "_context", "_changed")

    @classmethod
    def from_document(cls, document, graph):
        if type(graph) is not Graph:
            raise ContractError("revision requires a checked source graph")
        encoded = snapshot(document)
        document = json.loads(encoded)
        keys(document, ("version", "graph", "replacements"), "revision")
        if type(document["version"]) is not int or document["version"] != 1:
            raise ContractError("unsupported revision envelope")
        if document["graph"] != graph.context:
            raise ContractError("revision requires the exact source graph context")
        replacements = document["replacements"]
        if type(replacements) is not list or not 1 <= len(replacements) <= MAX_NODES:
            raise ContractError("expected bounded nonempty object replacements")
        by_id = {}
        for replacement in replacements:
            keys(replacement, ("id", "op", "ports", "attributes"), "replacement")
            identity = name(replacement["id"], "replaced object identity")
            graph.ref(identity)
            if identity in by_id:
                raise ContractError("duplicate replaced object identity")
            by_id[identity] = replacement
        revised = graph.document
        changed = []
        for index, obj in enumerate(revised["objects"]):
            if obj["id"] in by_id:
                replacement = by_id[obj["id"]]
                if encode(obj) != encode(replacement):
                    changed.append(obj["id"])
                revised["objects"][index] = replacement
        checked = Graph.from_document(revised, graph.vocabulary)
        result = cls()
        result._document, result._source = encoded, graph.context
        result._graph = graph if checked.context == graph.context else checked
        result._context = digest(
            {"revision": document, "envelope": "nomi.object-revision-1"}
        )
        result._changed = tuple(changed)
        result._sealed = True
        return result

    @property
    def document(self):
        return json.loads(self._document)

    @property
    def graph(self):
        return self._graph

    @property
    def context(self):
        return self._context

    def inspect(self):
        return {
            "status": "composition-checked",
            "revision": self._context,
            "source": self._source,
            "graph": self._graph.context,
            "requested_objects": [r["id"] for r in self.document["replacements"]],
            "changed_objects": list(self._changed),
            "realization": "unbound",
            "contracts": "not migrated",
        }

    @property
    def receipt(self):
        return json.loads(
            snapshot(
                {
                    "revision": self._context,
                    "graph": self._graph.document,
                    "inspection": self.inspect(),
                }
            )
        )
