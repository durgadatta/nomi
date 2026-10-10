"""Independent passive replay for the pinned engine-free object lab vocabulary.

Standard library only; no planner, shared inference, normalizer or backend.
Other vocabularies require independently admitted consumer rules, not an
automatic reinterpretation of supplied definitions as new trusted laws.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

VOCABULARY = "261a416c00ab73b7849ce085ed9c4436b9fe941fcc4414dd384216d6552d782a"
DOCUMENT_VOCABULARY = "e928fb99763004ed80bbf6f194d922abf96a908ead0ce0ceb5ce78890829d3c8"
LIMIT = 1_000_000
IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z_0-9.-]{0,127}\Z")

# These rules are reviewed independently of producer metadata/implementation.
RULES = {
    "exact.input": ("ExactInt", "input", ()),
    "exact.literal": ("ExactInt", "literal", ()),
    "exact.alias": ("ExactInt", "alias", ("target",)),
    "exact.add": ("ExactInt", "apply", ("left", "right")),
    "exact.multiply": ("ExactInt", "apply", ("left", "right")),
    "exact.double": ("ExactInt", "double", ("value",)),
    "exact.square": ("ExactInt", "square", ("value",)),
    "text.input": ("Text", "input", ()),
    "text.literal": ("Text", "literal", ()),
    "text.alias": ("Text", "alias", ("target",)),
    "text.concat": ("Text", "apply", ("left", "right")),
    "document.describe": ("Document", "description", ("body", "title")),
}
DOCUMENT_RULES = {
    **RULES,
    "document.spec.input": ("DocumentSpec", "input", ()),
    "document.spec.literal": ("DocumentSpec", "literal", ()),
    "document.spec.alias": ("DocumentSpec", "alias", ("target",)),
    "document.spec.describe": ("Document", "description", ("spec",)),
    "document.render_text": ("RenderedText", "apply", ("spec",)),
    "document.title": ("Text", "apply", ("spec",)),
    "document.paragraph_count": ("ExactInt", "apply", ("spec",)),
    "rendered.as_text": ("Text", "apply", ("value",)),
}


def _rules_for(vocabulary):
    fingerprint = _digest(vocabulary)
    if fingerprint == VOCABULARY:
        return RULES
    if fingerprint == DOCUMENT_VOCABULARY:
        return DOCUMENT_RULES
    raise ReplayError("independent consumer does not admit this vocabulary")


def _value_ok(value, codec):
    # Only codecs in independently pinned artifacts can reach this function.
    if codec is None:
        return False
    kind = codec["kind"]
    if kind in ("text", "int"):
        return type(value) is (str if kind == "text" else int)
    if kind == "record":
        return (
            type(value) is dict
            and set(value) == set(codec["fields"])
            and all(
                _value_ok(value[field], shape)
                for field, shape in codec["fields"].items()
            )
        )
    if kind == "array":
        return type(value) is list and all(
            _value_ok(item, codec["items"]) for item in value
        )
    return False


def _path_codec(codec, path):
    if type(path) is not list or len(path) > 64:
        raise ReplayError("invalid structural path")
    for segment in path:
        if codec is None:
            raise ReplayError("path has no declared codec")
        if type(segment) is str:
            _identity(segment)
            if codec["kind"] != "record" or segment not in codec.get("fields", {}):
                raise ReplayError("unknown structural field")
            codec = codec["fields"][segment]
        elif type(segment) is int and 0 <= segment <= LIMIT:
            if codec["kind"] != "array" or "items" not in codec:
                raise ReplayError("path does not select a declared array item")
            codec = codec["items"]
        else:
            raise ReplayError("invalid structural path segment")
    if codec is None:
        raise ReplayError("path has no declared codec")
    return codec


class ReplayError(ValueError):
    pass


def _encode(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError, RecursionError) as exc:
        raise ReplayError("invalid artifact encoding") from exc


def _digest(value):
    return hashlib.sha256(_encode(value).encode()).hexdigest()


def _inert(value, depth=0):
    if depth > 64:
        raise ReplayError("artifact nesting budget exceeded")
    if type(value) is dict:
        for key, child in value.items():
            if type(key) is not str:
                raise ReplayError("invalid record key")
            _inert(child, depth + 1)
    elif type(value) is list:
        for child in value:
            _inert(child, depth + 1)
    elif type(value) not in (str, int, bool, type(None)):
        raise ReplayError("non-inert artifact value")


def _artifact(value):
    _inert(value)
    if len(_encode(value).encode()) > LIMIT:
        raise ReplayError("artifact byte budget exceeded")


def _keys(value, expected):
    if type(value) is not dict or set(value) != set(expected):
        raise ReplayError(f"expected exact record fields {expected}")


def _identity(value):
    if type(value) is not str or not IDENTIFIER.fullmatch(value):
        raise ReplayError("invalid reference identity")
    return value


def _unique_names(values):
    if type(values) is not list or not values:
        raise ReplayError("expected nonempty reference list")
    for value in values:
        _identity(value)
    if len(values) != len(set(values)):
        raise ReplayError("duplicate reference")


def _reconstruct(vocabulary, graph):
    for artifact in (vocabulary, graph):
        _artifact(artifact)
    rules = _rules_for(vocabulary)
    _keys(graph, ("version", "vocabulary", "objects", "outputs"))
    if (
        type(graph["version"]) is not int
        or graph["version"] != 1
        or graph["vocabulary"] != _digest(vocabulary)
    ):
        raise ReplayError("unsupported object graph context")
    if type(graph["objects"]) is not list or not 1 <= len(graph["objects"]) <= 512:
        raise ReplayError("object count budget exceeded")
    objects = {}
    for raw in graph["objects"]:
        _keys(raw, ("id", "op", "ports", "attributes"))
        identity, op = _identity(raw["id"]), raw["op"]
        if identity in objects:
            raise ReplayError("duplicate object identity")
        if type(op) is not str or op not in rules:
            raise ReplayError("unknown operation")
        family, role, port_names = rules[op]
        _keys(raw["ports"], port_names)
        for ref in raw["ports"].values():
            _identity(ref)
        attributes = raw["attributes"]
        if role == "literal":
            _keys(attributes, ("value",))
            if not _value_ok(attributes["value"], vocabulary["types"][family]["value"]):
                raise ReplayError("literal value disagrees with nominal family")
        elif role == "description":
            _keys(attributes, ("purpose",))
            if type(attributes["purpose"]) is not str:
                raise ReplayError("invalid document purpose")
        else:
            _keys(attributes, ())
        objects[identity] = raw
    _unique_names(graph["outputs"])
    if set(graph["outputs"]) - objects.keys():
        raise ReplayError("unknown output")
    for raw in objects.values():
        family, _, _ = rules[raw["op"]]
        for ref in raw["ports"].values():
            if ref not in objects:
                raise ReplayError("unknown dependency")
            required = (
                "DocumentSpec"
                if raw["op"]
                in (
                    "document.spec.describe",
                    "document.render_text",
                    "document.title",
                    "document.paragraph_count",
                )
                else "RenderedText"
                if raw["op"] == "rendered.as_text"
                else "Text"
                if family == "Document"
                else family
            )
            if rules[objects[ref]["op"]][0] != required:
                raise ReplayError("incompatible nominal port families")
    # Preserve source order within topological layers so published term IDs
    # can also be checked; structural interning is the equality oracle.
    order, depths, pending = [], {}, dict(objects)
    while pending:
        ready = [
            identity
            for identity, raw in pending.items()
            if set(raw["ports"].values()) <= depths.keys()
        ]
        if not ready:
            raise ReplayError("cyclic object composition")
        for identity in ready:
            depths[identity] = 1 + max(
                (depths[ref] for ref in pending[identity]["ports"].values()), default=0
            )
            if depths[identity] > 64:
                raise ReplayError("composition depth budget exceeded")
            order.append(identity)
            del pending[identity]
    terms, index, normal = [], {}, {}

    def intern(term):
        if term not in index:
            if len(terms) >= 512:
                raise ReplayError("normalized term budget exceeded")
            index[term] = len(terms)
            terms.append(term)
        return index[term]

    for identity in order:
        raw = objects[identity]
        op = raw["op"]
        family, role, _ = rules[op]
        ports = tuple(
            (port, (normal[ref],)) for port, ref in sorted(raw["ports"].items())
        )
        if role == "alias":
            normal[identity] = ports[0][1][0]
            continue
        if role in ("square", "double"):
            operand = ports[0][1][0]
            op = "exact.multiply" if role == "square" else "exact.add"
            ports = (("left", (operand,)), ("right", (operand,)))
        normal[identity] = intern(
            (
                op,
                family,
                identity if role in ("input", "description") else None,
                ports,
                _encode(raw["attributes"]),
            )
        )
    return objects, normal, terms


def replay(vocabulary, graph, receipt):
    _artifact(receipt)
    _, normal, terms = _reconstruct(vocabulary, graph)
    _keys(
        receipt,
        (
            "version",
            "context",
            "vocabulary",
            "left",
            "right",
            "status",
            "basis",
            "normal_forms",
        ),
    )
    for side in ("left", "right"):
        if type(receipt[side]) is not str or receipt[side] not in normal:
            raise ReplayError("unknown comparison reference")
    left, right = receipt["left"], receipt["right"]
    if normal[left] != normal[right]:
        raise ReplayError("structural equivalence was not established")

    def projection(identity):
        reachable, stack = set(), [normal[identity]]
        while stack:
            item = stack.pop()
            if item not in reachable:
                reachable.add(item)
                stack.extend(ref for _, refs in terms[item][3] for ref in refs)
        return {
            "root": normal[identity],
            "terms": [
                {
                    "id": i,
                    "op": term[0],
                    "type": term[1],
                    "identity": term[2],
                    "ports": {port: list(refs) for port, refs in term[3]},
                    "attributes": json.loads(term[4]),
                }
                for i, term in enumerate(terms)
                if i in reachable
            ],
        }

    context = _digest({"graph": graph, "envelope": "nomi.object-graph-1"})
    expected = {
        "version": 1,
        "context": context,
        "vocabulary": _digest(vocabulary),
        "left": left,
        "right": right,
        "status": "equivalent",
        "basis": "structural identity after declared pure definitions and aliases",
        "normal_forms": [projection(left), projection(right)],
    }
    if _encode(receipt) != _encode(expected):
        raise ReplayError(
            "comparison receipt disagrees with independently reconstructed evidence"
        )
    return {
        "status": "verified",
        "context": context,
        "vocabulary": _digest(vocabulary),
        "independent_checker": True,
        "scope": "pinned object lab vocabulary; no engine conformance claim",
    }


def _requirement_receipt(vocabulary, graph, requirements, bindings=None):
    objects, normal, terms = _reconstruct(vocabulary, graph)
    rules = _rules_for(vocabulary)
    _artifact(requirements)
    _keys(requirements, ("version", "graph", "owner", "revision", "requirements"))
    graph_context = _digest({"graph": graph, "envelope": "nomi.object-graph-1"})
    if (
        type(requirements["version"]) is not int
        or requirements["version"] not in (1, 2)
        or requirements["graph"] != graph_context
    ):
        raise ReplayError("unsupported or stale requirement context")
    _identity(requirements["owner"])
    _identity(requirements["revision"])
    version = requirements["version"]
    obligations = requirements["requirements"]
    if type(obligations) is not list or not 1 <= len(obligations) <= 512:
        raise ReplayError("requirement count budget exceeded")
    supplied = {} if bindings is None else bindings
    _artifact(supplied)
    if type(supplied) is not dict:
        raise ReplayError("binding evidence must be input records")
    for identity, value in supplied.items():
        if identity not in objects:
            raise ReplayError("unknown input binding")
        family, role, _ = rules[objects[identity]["op"]]
        if role != "input" or not _value_ok(
            value, vocabulary["types"][family]["value"]
        ):
            raise ReplayError("incompatible abstract input binding")
    seen, results = set(), []
    for obligation in obligations:
        _keys(
            obligation,
            ("id", "rule", "subject")
            if version == 1
            else ("id", "rule", "subject", "path"),
        )
        identity = _identity(obligation["id"])
        if identity in seen:
            raise ReplayError("duplicate requirement identity")
        seen.add(identity)
        rule = obligation["rule"]
        admitted = ("exact.positive-v1", "text.nonempty-v1")
        if version == 2:
            admitted += ("array.nonempty-v1",)
        if type(rule) is not str or rule not in admitted:
            raise ReplayError("independent consumer does not admit this predicate")
        subject = obligation["subject"]
        if type(subject) is not str or subject not in objects:
            raise ReplayError("unknown requirement subject")
        family = rules[objects[subject]["op"]][0]
        path = [] if version == 1 else obligation["path"]
        codec = vocabulary["types"][family]["value"]
        if version == 1:
            required = "ExactInt" if rule == "exact.positive-v1" else "Text"
            if family != required:
                raise ReplayError("incompatible predicate subject family")
        else:
            selected = _path_codec(codec, path)
            required_kind = {
                "exact.positive-v1": "int",
                "text.nonempty-v1": "text",
                "array.nonempty-v1": "array",
            }[rule]
            if selected["kind"] != required_kind:
                raise ReplayError("incompatible predicate path kind")
        term = terms[normal[subject]]
        _, role, _ = rules[term[0]]
        known, value, basis = False, None, "unresolved expression"
        if role == "literal":
            known, value, basis = True, json.loads(term[4])["value"], "declared literal"
        elif role == "input" and term[2] in supplied:
            known, value, basis = True, supplied[term[2]], "explicit input snapshot"
        exists = known
        if known:
            for segment in path:
                if (
                    type(segment) is str and type(value) is dict and segment in value
                ) or (
                    type(segment) is int
                    and type(value) is list
                    and segment < len(value)
                ):
                    value = value[segment]
                else:
                    exists = False
                    basis += "; missing path"
                    break
        passed = exists and (
            value > 0 if rule == "exact.positive-v1" else len(value) > 0
        )
        results.append(
            {
                "id": identity,
                "subject": subject,
                "rule": rule,
                "status": "satisfied"
                if known and passed
                else "refuted"
                if known
                else "pending",
                "basis": basis,
            }
        )
        if version == 2:
            results[-1]["path"] = path
    statuses = {result["status"] for result in results}
    verdict = (
        "refuted"
        if "refuted" in statuses
        else "pending"
        if "pending" in statuses
        else "satisfied"
    )
    context = _digest(
        {
            "requirements": requirements,
            "checker": "literal-input-predicates-v1"
            if version == 1
            else "structural-path-predicates-v2",
        }
    )
    expected = {
        "version": version,
        "context": context,
        "graph": graph_context,
        "status": verdict,
        "evidence_phase": "static" if bindings is None else "binding",
        "binding_digest": None if bindings is None else _digest(bindings),
        "requirements": results,
        "scope": "closed representation predicates, not scientific assumptions or a general solver"
        if version == 1
        else "closed structural path predicates, not scientific assumptions or a general solver",
    }
    return expected


def replay_requirements(vocabulary, graph, requirements, receipt, bindings=None):
    _artifact(receipt)
    expected = _requirement_receipt(vocabulary, graph, requirements, bindings)
    if _encode(receipt) != _encode(expected):
        raise ReplayError(
            "predicate evidence disagrees with independently reconstructed verdict"
        )
    return {
        "status": "verified",
        "verdict": expected["status"],
        "context": expected["context"],
        "graph": expected["graph"],
        "independent_checker": True,
        "scope": "pinned lab predicates; no engine or scientific validity claim",
    }


def replay_workflows(vocabulary, base_graph, workflows, receipt):
    """Independently replay explicit template expansion, with no engine/bindings."""
    _reconstruct(vocabulary, base_graph)
    _artifact(workflows)
    _artifact(receipt)
    if type(workflows) is not list or not 1 <= len(workflows) <= 512:
        raise ReplayError("expected bounded explicit workflow definitions")
    rules = _rules_for(vocabulary)
    admitted = {}
    for workflow in workflows:
        _keys(
            workflow,
            ("version", "id", "revision", "graph", "inputs", "outputs", "requirements"),
        )
        if type(workflow["version"]) is not int or workflow["version"] != 1:
            raise ReplayError("unsupported workflow envelope")
        _identity(workflow["id"])
        _identity(workflow["revision"])
        objects, _, _ = _reconstruct(vocabulary, workflow["graph"])
        for direction in ("inputs", "outputs"):
            mapping = workflow[direction]
            if type(mapping) is not dict:
                raise ReplayError("invalid workflow interface")
            for port, identity in mapping.items():
                _identity(port)
                if type(identity) is not str or identity not in objects:
                    raise ReplayError("unknown workflow interface reference")
        inputs = list(workflow["inputs"].values())
        slots = {i for i, obj in objects.items() if rules[obj["op"]][1] == "input"}
        if len(inputs) != len(set(inputs)) or set(inputs) != slots:
            raise ReplayError("workflow inputs must expose each abstract slot once")
        if not workflow["outputs"] or set(workflow["outputs"].values()) != set(
            workflow["graph"]["outputs"]
        ):
            raise ReplayError("workflow outputs disagree with the template selection")
        if workflow["requirements"] is not None:
            _requirement_receipt(
                vocabulary, workflow["graph"], workflow["requirements"]
            )
        context = _digest({"workflow": workflow, "envelope": "nomi.object-workflow-1"})
        if context in admitted:
            raise ReplayError("duplicate workflow definition")
        admitted[context] = workflow
    _keys(receipt, ("graph", "requirements", "inspection"))
    view = receipt["inspection"]
    _keys(view, ("graph", "components", "outputs", "realization", "requirements"))
    components = view["components"]
    if type(components) is not list or not 1 <= len(components) <= 512:
        raise ReplayError("invalid workflow component count")
    graph = json.loads(_encode(base_graph))
    conditions, expected_components, namespaces = [], [], set()
    exports = {}
    for component in components:
        _keys(
            component,
            (
                "workflow",
                "id",
                "revision",
                "namespace",
                "inputs",
                "outputs",
                "requirement_source",
            ),
        )
        context = component["workflow"]
        if type(context) is not str or context not in admitted:
            raise ReplayError("workflow definition context is not supplied")
        workflow = admitted[context]
        namespace = _identity(component["namespace"])
        if namespace in namespaces:
            raise ReplayError("duplicate workflow namespace")
        namespaces.add(namespace)
        arguments = component["inputs"]
        _keys(arguments, workflow["inputs"])
        current_objects, _, _ = _reconstruct(vocabulary, graph)
        local_objects, _, _ = _reconstruct(vocabulary, workflow["graph"])
        substitution = {}
        for port, local in workflow["inputs"].items():
            target = arguments[port]
            if type(target) is not str or target not in current_objects:
                raise ReplayError("unknown workflow argument in this revision")
            if (
                rules[current_objects[target]["op"]][0]
                != rules[local_objects[local]["op"]][0]
            ):
                raise ReplayError("workflow argument nominal family mismatch")
            substitution[local] = target
        for local in local_objects:
            if local not in substitution:
                target = _identity(namespace + "." + local)
                if target in current_objects:
                    raise ReplayError("workflow expansion identity collision")
                substitution[local] = target
        for original in workflow["graph"]["objects"]:
            if original["id"] in workflow["inputs"].values():
                continue
            copied = json.loads(_encode(original))
            copied["id"] = substitution[original["id"]]
            for port, reference in original["ports"].items():
                copied["ports"][port] = (
                    [substitution[r] for r in reference]
                    if type(reference) is list
                    else substitution[reference]
                )
            graph["objects"].append(copied)
        exports = {
            port: substitution[workflow["outputs"][port]]
            for port in sorted(workflow["outputs"])
        }
        for target in exports.values():
            if target not in graph["outputs"]:
                graph["outputs"].append(target)
        _reconstruct(vocabulary, graph)
        source = workflow["requirements"]
        source_evidence = (
            None
            if source is None
            else _requirement_receipt(vocabulary, workflow["graph"], source)
        )
        if source is not None:
            for requirement in source["requirements"]:
                copied = json.loads(_encode(requirement))
                copied["id"] = _identity(namespace + "." + requirement["id"])
                copied["subject"] = substitution[requirement["subject"]]
                copied["path"] = requirement.get("path", [])
                conditions.append(copied)
        expected_components.append(
            {
                "workflow": context,
                "id": workflow["id"],
                "revision": workflow["revision"],
                "namespace": namespace,
                "inputs": arguments,
                "outputs": exports,
                "requirement_source": None
                if source is None
                else {
                    "owner": source["owner"],
                    "revision": source["revision"],
                    "context": source_evidence["context"],
                },
            }
        )
    graph_context = _digest({"graph": graph, "envelope": "nomi.object-graph-1"})
    required = (
        None
        if not conditions
        else {
            "version": 2,
            "graph": graph_context,
            "owner": "nomi.workflow-composition",
            "revision": "v1",
            "requirements": conditions,
        }
    )
    evidence = (
        None if required is None else _requirement_receipt(vocabulary, graph, required)
    )
    expected = {
        "graph": graph,
        "requirements": required,
        "inspection": {
            "graph": graph_context,
            "components": expected_components,
            "outputs": exports,
            "realization": "unbound",
            "requirements": evidence,
        },
    }
    if _encode(receipt) != _encode(expected):
        raise ReplayError(
            "workflow receipt disagrees with independent substitution and conditions"
        )
    return {
        "status": "verified",
        "graph": graph_context,
        "independent_checker": True,
        "components": len(components),
        "verdict": None if evidence is None else evidence["status"],
        "scope": "pinned artifact substitution and carried conditions; no engine or authoring-intent proof",
    }


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ReplayError("duplicate JSON key")
        result[key] = value
    return result


def load(path):
    with Path(path).open("rb") as stream:
        data = stream.read(LIMIT + 1)
    if len(data) > LIMIT:
        raise ReplayError("artifact byte budget exceeded")
    try:
        result = json.loads(data, object_pairs_hook=_pairs)
        _artifact(result)
        return result
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise ReplayError("invalid JSON artifact") from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vocabulary")
    parser.add_argument("graph")
    parser.add_argument("receipt")
    parser.add_argument(
        "--requirements",
        help="replay requirement evidence rather than a composition comparison",
    )
    parser.add_argument(
        "--bindings", help="explicit input evidence for requirement replay"
    )
    parser.add_argument(
        "--workflow",
        action="append",
        help="explicit workflow definition; replay an expanded instance from the base graph",
    )
    args = parser.parse_args(argv)
    try:
        if args.workflow:
            if args.requirements or args.bindings:
                raise ReplayError(
                    "workflow expansion replay is separate from binding evidence"
                )
            result = replay_workflows(
                load(args.vocabulary),
                load(args.graph),
                [load(p) for p in args.workflow],
                load(args.receipt),
            )
        elif args.requirements:
            result = replay_requirements(
                load(args.vocabulary),
                load(args.graph),
                load(args.requirements),
                load(args.receipt),
                None if args.bindings is None else load(args.bindings),
            )
        else:
            if args.bindings:
                raise ReplayError(
                    "binding evidence requires an explicit requirement artifact"
                )
            result = replay(load(args.vocabulary), load(args.graph), load(args.receipt))
        print(json.dumps(result, indent=2))
        return 0
    except (ReplayError, OSError) as exc:
        print(json.dumps({"status": "refused", "message": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
