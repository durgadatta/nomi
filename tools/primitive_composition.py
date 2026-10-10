"""Inspect a designing composition map; no lowering or semantic proof claims."""

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "config/primitive_composition.json"
DOCUMENT = ROOT / "docs/design/primitive_composition.md"
START = "<!-- composition-catalog:start -->"
END = "<!-- composition-catalog:end -->"
NODE_FIELDS = {
    "id",
    "label",
    "kind",
    "depends",
    "owner",
    "law",
    "gate",
    "placement",
    "status",
    "fixtures",
}
NAME = re.compile(r"[a-z][a-z0-9-]{0,63}\Z")


class CompositionError(ValueError):
    pass


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise CompositionError("duplicate catalog field")
        result[key] = value
    return result


def load(path=CATALOG):
    with Path(path).open("rb") as stream:
        source = stream.read(1_000_001)
    if len(source) > 1_000_000:
        raise CompositionError("catalog byte budget exceeded")
    try:
        return json.loads(source, object_pairs_hook=_pairs)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise CompositionError("invalid catalog JSON") from exc


def _path(value, suffix, boundary="docs"):
    if type(value) is not str or not value.startswith("docs/"):
        raise CompositionError("composition references must be documentation paths")
    path = ROOT / value
    if path.suffix != suffix or not path.resolve().is_relative_to(ROOT / boundary):
        raise CompositionError("composition reference escapes its artifact boundary")
    if not path.is_file():
        raise CompositionError(f"missing composition reference: {value}")
    return path


def validate(catalog):
    if type(catalog) is not dict or set(catalog) != {"version", "status", "nodes"}:
        raise CompositionError("expected exact composition catalog envelope")
    if (
        type(catalog["version"]) is not int
        or catalog["version"] != 1
        or catalog["status"] != "designing"
    ):
        raise CompositionError("unsupported composition catalog or acceptance claim")
    raw = catalog["nodes"]
    if type(raw) is not list or not 1 <= len(raw) <= 256:
        raise CompositionError("expected bounded nonempty composition nodes")
    nodes, covered = {}, set()
    for node in raw:
        if type(node) is not dict or set(node) != NODE_FIELDS:
            raise CompositionError("expected exact composition node fields")
        identity = node["id"]
        if (
            type(identity) is not str
            or not NAME.fullmatch(identity)
            or identity in nodes
        ):
            raise CompositionError("invalid or duplicate composition identity")
        for field in ("label", "law", "gate"):
            value = node[field]
            if (
                type(value) is not str
                or not value.strip()
                or len(value) > 1024
                or "\n" in value
            ):
                raise CompositionError(f"missing or invalid {field}: {identity}")
        if node["status"] not in ("hypothesis", "target", "experiment", "open"):
            raise CompositionError("invalid node status")
        if node["placement"] not in (
            "semantic-family",
            "core",
            "convenience",
            "library",
            "tool",
            "scoped-candidate",
        ):
            raise CompositionError("invalid node placement")
        deps = node["depends"]
        if (
            type(deps) is not list
            or any(type(dep) is not str or not NAME.fullmatch(dep) for dep in deps)
            or len(deps) != len(set(deps))
        ):
            raise CompositionError("invalid or duplicate composition dependencies")
        if node["kind"] == "family":
            if (
                deps
                or node["placement"] != "semantic-family"
                or node["status"] != "hypothesis"
            ):
                raise CompositionError(
                    "candidate families must remain unaccepted roots"
                )
        elif node["kind"] == "composition":
            if not deps or node["placement"] == "semantic-family":
                raise CompositionError(
                    "composition requires existing semantic dependencies"
                )
        else:
            raise CompositionError("invalid composition node kind")
        _path(node["owner"], ".md", "docs/design")
        if not node["owner"].startswith("docs/design/"):
            raise CompositionError("composition laws require a design owner")
        fixtures = node["fixtures"]
        if (
            type(fixtures) is not list
            or any(type(f) is not str for f in fixtures)
            or len(fixtures) != len(set(fixtures))
        ):
            raise CompositionError("invalid or duplicate fixture references")
        for fixture in fixtures:
            _path(fixture, ".nomi")
            covered.add(fixture)
        nodes[identity] = node
    depths, pending = {}, dict(nodes)
    for node in nodes.values():
        if set(node["depends"]) - nodes.keys():
            raise CompositionError(f"unknown composition dependency: {node['id']}")
    while pending:
        ready = [
            identity
            for identity, node in pending.items()
            if set(node["depends"]) <= depths.keys()
        ]
        if not ready:
            raise CompositionError("cyclic composition hierarchy")
        for identity in ready:
            depths[identity] = 1 + max(
                (depths[dep] for dep in nodes[identity]["depends"]), default=-1
            )
            del pending[identity]
    expected = {
        str(p.relative_to(ROOT)) for p in (ROOT / "docs/design/targets").rglob("*.nomi")
    }
    missing = expected - covered
    if missing:
        raise CompositionError(
            f"unmapped target fixtures: {', '.join(sorted(missing))}"
        )
    return nodes, depths, len(expected)


def explain(catalog, identity=None):
    nodes, depths, fixtures = validate(catalog)
    if identity is not None and identity not in nodes:
        raise CompositionError("unknown composition identity")
    selected = set(nodes) if identity is None else set()
    stack = [] if identity is None else [identity]
    while stack:
        item = stack.pop()
        if item not in selected:
            selected.add(item)
            stack.extend(nodes[item]["depends"])
    return {
        "status": "designing",
        "scope": "declared dependency/navigation coverage; no semantic proof",
        "subject": identity,
        "mapped_target_fixtures": fixtures,
        "families": [
            i for i in nodes if i in selected and nodes[i]["kind"] == "family"
        ],
        "layers": [
            {
                "depth": depth,
                "nodes": [
                    nodes[i] for i in nodes if i in selected and depths[i] == depth
                ],
            }
            for depth in sorted({depths[i] for i in selected})
        ],
    }


def render(catalog):
    nodes, depths, _ = validate(catalog)
    lines = [
        START,
        "",
        "| Construct / ID | Dependencies | Placement / status | Law and unclosed gate |",
        "| --- | --- | --- | --- |",
    ]

    def cell(text):
        return text.replace("|", "&#124;").replace("<", "&lt;").replace(">", "&gt;")

    for identity in sorted(nodes, key=lambda i: (depths[i], list(nodes).index(i))):
        node = nodes[identity]
        deps = ", ".join(f"`{d}`" for d in node["depends"]) or "Candidate root"
        owner = "../" + node["owner"].removeprefix("docs/")
        lines.append(
            f"| {cell(node['label'])} / `{identity}` | {deps} | {node['placement']} / {node['status']} | "
            f"[Owner]({owner}). {cell(node['law'])} **Gate:** {cell(node['gate'])} |"
        )
    return "\n".join(lines + ["", END])


def check_document(catalog, document):
    if document.count(START) != 1 or document.count(END) != 1:
        raise CompositionError("missing or repeated composition projection markers")
    start, end = document.index(START), document.index(END) + len(END)
    if document[start:end] != render(catalog):
        raise CompositionError(
            "stale composition projection; regenerate the marked table"
        )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "show", "render"))
    parser.add_argument("identity", nargs="?")
    parser.add_argument("--catalog", default=str(CATALOG))
    args = parser.parse_args(argv)
    try:
        if args.identity is not None and args.command != "show":
            raise CompositionError("only show accepts a composition identity")
        catalog = load(args.catalog)
        if args.command == "render":
            print(render(catalog))
        elif args.command == "show":
            print(json.dumps(explain(catalog, args.identity), indent=2))
        else:
            result = explain(catalog)
            check_document(catalog, DOCUMENT.read_text())
            print(
                json.dumps(
                    {
                        "status": "checked",
                        "nodes": sum(len(layer["nodes"]) for layer in result["layers"]),
                        "mapped_target_fixtures": result["mapped_target_fixtures"],
                        "scope": result["scope"],
                    }
                )
            )
        return 0
    except (CompositionError, OSError) as exc:
        print(json.dumps({"status": "refused", "message": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
