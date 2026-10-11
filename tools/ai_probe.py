"""Input-free tensor metadata experiment; no tensors, AD or backend execution."""

import argparse
import json

from tools.object_interface.documents import (
    ContractError,
    Frozen,
    digest,
    keys,
    load_document,
    name,
    names,
    ordered,
    snapshot,
)

PROFILE = "named-tensor-shapes-v1"
DTYPES = ("Float32", "Float64")
OPERATIONS = {
    "input": ("id", "op", "axes", "dtype"),
    "parameter": ("id", "op", "axes", "dtype"),
    "add": ("id", "op", "args"),
    "subtract": ("id", "op", "args"),
    "matmul": ("id", "op", "args"),
    "square": ("id", "op", "args"),
    "mean": ("id", "op", "args"),
    "broadcast": ("id", "op", "args", "axes"),
}


class Program(Frozen):
    """Checked metadata snapshot under one closed profile, not an executable."""

    __slots__ = ("_source",)

    def __init__(self, document):
        self._source = snapshot(document)
        self.check()
        self._sealed = True

    @property
    def document(self):
        return json.loads(self._source)

    def check(self, backend=None):
        source = self.document
        keys(
            source,
            (
                "version",
                "id",
                "revision",
                "profile",
                "extent_variables",
                "axes",
                "objects",
                "outputs",
            ),
        )
        if (
            type(source["version"]) is not int
            or source["version"] != 1
            or source["profile"] != PROFILE
        ):
            raise ContractError("unsupported tensor metadata profile")
        name(source["id"])
        if (
            type(source["revision"]) is not int
            or not 0 <= source["revision"] <= 1_000_000
        ):
            raise ContractError("invalid program revision")
        variables = names(source["extent_variables"], "extent variables")
        if len(variables) > 8:
            raise ContractError("extent variable budget exceeded")
        axes = {}
        if type(source["axes"]) is not list or len(source["axes"]) > 8:
            raise ContractError("expected at most eight axis declarations")
        for row in source["axes"]:
            keys(row, ("id", "extent"), "axis")
            identity = name(row["id"], "axis")
            if identity in axes:
                raise ContractError("duplicate axis identity")
            extent = row["extent"]
            if not (
                (type(extent) is int and 1 <= extent <= 1_000_000)
                or (type(extent) is str and extent in variables)
            ):
                raise ContractError(
                    "axis extent needs a bounded positive integer or declared positive variable"
                )
            axes[identity] = extent

        def shape(raw):
            result = names(raw, "ordered axes")
            if len(result) > 4 or not set(result) <= axes.keys():
                raise ContractError("unknown axis or rank exceeds four")
            return result

        rows, dependencies = {}, {}
        if (
            type(source["objects"]) is not list
            or not 1 <= len(source["objects"]) <= 128
        ):
            raise ContractError("expected 1..128 tensor objects")
        for row in source["objects"]:
            if (
                type(row) is not dict
                or type(row.get("op")) is not str
                or row["op"] not in OPERATIONS
            ):
                raise ContractError("unsupported tensor operation")
            keys(row, OPERATIONS[row["op"]], "tensor object")
            identity = name(row["id"])
            if identity in rows:
                raise ContractError("duplicate tensor object identity")
            rows[identity] = row
            args = row.get("args", [])
            if type(args) is not list:
                raise ContractError("expected ordered operand list")
            for ref in args:
                name(ref, "operand")
            arity = (
                0
                if row["op"] in ("input", "parameter")
                else (2 if row["op"] in ("add", "subtract", "matmul") else 1)
            )
            if len(args) != arity:
                raise ContractError("invalid tensor operation arity")
            dependencies[identity] = args
        outputs = names(source["outputs"], "outputs", nonempty=True)
        if not set(outputs) <= rows.keys():
            raise ContractError("unknown output")

        signatures, leaves = {}, {}
        for identity in ordered(dependencies):
            row = rows[identity]
            op, refs = row["op"], dependencies[identity]
            if op in ("input", "parameter"):
                result_axes = shape(row["axes"])
                dtype = row["dtype"]
                if type(dtype) is not str or dtype not in DTYPES:
                    raise ContractError("unsupported tensor scalar label")
                leaves[identity] = {identity}
            else:
                first_axes, dtype = signatures[refs[0]]
                result_axes = first_axes
                leaves[identity] = set().union(*(leaves[ref] for ref in refs))
                if len(refs) == 2:
                    second_axes, second_dtype = signatures[refs[1]]
                    if dtype != second_dtype:
                        raise ContractError(
                            f"{identity}: implicit dtype conversion is unsupported"
                        )
                    if op == "matmul":
                        if len(first_axes) != 2 or len(second_axes) != 2:
                            raise ContractError(
                                f"{identity}: matmul needs rank-two operands"
                            )
                        if first_axes[1] != second_axes[0]:
                            raise ContractError(
                                f"{identity}: contracting axis identities differ"
                            )
                        result_axes = shape([first_axes[0], second_axes[1]])
                    elif first_axes != second_axes:
                        raise ContractError(
                            f"{identity}: equal ordered axes required; broadcast explicitly"
                        )
                if op == "mean":
                    result_axes = ()
                elif op == "broadcast":
                    result_axes = shape(row["axes"])
                    retained = tuple(axis for axis in result_axes if axis in first_axes)
                    if retained != first_axes:
                        raise ContractError(
                            f"{identity}: broadcast must retain ordered source axes"
                        )
            signatures[identity] = (result_axes, dtype)

        coverage = {"status": "unknown", "reason": "no backend descriptor supplied"}
        if backend is not None:
            backend = json.loads(snapshot(backend))
            keys(
                backend,
                ("id", "revision", "operations", "dtypes"),
                "backend descriptor",
            )
            name(backend["id"], "backend")
            if (
                type(backend["revision"]) is not int
                or not 0 <= backend["revision"] <= 1_000_000
            ):
                raise ContractError("invalid backend descriptor revision")
            supported = names(backend["operations"], "backend operations")
            dtypes = names(backend["dtypes"], "backend scalar labels")
            if not set(supported) <= OPERATIONS.keys() or not set(dtypes) <= set(
                DTYPES
            ):
                raise ContractError("backend descriptor exceeds the closed profile")
            missing = [
                identity
                for identity, row in rows.items()
                if row["op"] not in supported or signatures[identity][1] not in dtypes
            ]
            coverage = {
                "status": "unsupported" if missing else "declared-coverage",
                "context": digest(backend),
                "missing_objects": missing,
            }

        report = {
            "profile": PROFILE,
            "context": digest({"domain": PROFILE, "program": source}),
            "objects": [
                {
                    "id": identity,
                    "op": row["op"],
                    "axes": list(signatures[identity][0]),
                    "extents": [axes[axis] for axis in signatures[identity][0]],
                    "dtype": signatures[identity][1],
                    "leaf_dependencies": sorted(leaves[identity]),
                }
                for identity, row in rows.items()
            ],
            "outputs": list(outputs),
            "backend": coverage,
            "scope": {
                "inputs": "none",
                "checked": "closed named-axis metadata composition",
                "extent_variables": "positive; no symbolic arithmetic solving",
                "derivatives": "not-produced",
                "execution": "not-run",
                "numerical-correctness": "not-established",
                "independent-replay": "not-implemented",
            },
        }
        return json.loads(snapshot(report))

    def explain(self, identity):
        name(identity)
        report = self.check()
        row = next((row for row in report["objects"] if row["id"] == identity), None)
        if row is None:
            raise ContractError("unknown tensor object")
        return {"context": report["context"], "object": row, "scope": report["scope"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("program")
    parser.add_argument("--object")
    parser.add_argument("--backend")
    args = parser.parse_args()
    try:
        program = Program(load_document(args.program))
        if args.object and args.backend:
            raise ContractError(
                "select object inspection or whole-program backend coverage"
            )
        result = (
            program.explain(args.object)
            if args.object
            else program.check(load_document(args.backend) if args.backend else None)
        )
        print(json.dumps(result, indent=2))
        return 1 if result.get("backend", {}).get("status") == "unsupported" else 0
    except (ContractError, OSError, ValueError, RecursionError) as error:
        print(json.dumps({"status": "refused", "reason": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
