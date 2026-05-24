"""Declared host capabilities for direct runtimes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HOST_CAPABILITIES_PATH = Path(__file__).with_name("host_capabilities.json")


def load_host_capabilities() -> dict[str, Any]:
    payload = json.loads(HOST_CAPABILITIES_PATH.read_text(encoding="utf-8"))
    if payload.get("schema") != "nomi.host-capabilities":
        raise ValueError("unexpected host capability manifest schema")
    return payload


def declared_host_capability_names(runtime_name: str) -> frozenset[str]:
    return frozenset(
        capability["name"]
        for capability in load_host_capabilities()["capabilities"]
        if runtime_name in capability["runtimes"]
    )


def validate_host_call_names(runtime_name: str, names: set[str]) -> None:
    declared = declared_host_capability_names(runtime_name)
    missing = declared - names
    extra = names - declared
    if missing or extra:
        parts = []
        if missing:
            parts.append(f"missing declared host call(s): {', '.join(sorted(missing))}")
        if extra:
            parts.append(f"undeclared host call(s): {', '.join(sorted(extra))}")
        raise ValueError(f"{runtime_name} host capability mismatch: {'; '.join(parts)}")


def render_host_capability_table() -> str:
    rows = [
        "| capability | runtimes | arity | returns | deterministic | effects | pure | prints | may throw | browser |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for capability in load_host_capabilities()["capabilities"]:
        rows.append(
            "| {name} | {runtimes} | {arity} | {returns} | {determinism} | {effects} | {pure} | {prints} | {throws} | {browser} |".format(
                name=capability["name"],
                runtimes=", ".join(capability["runtimes"]),
                arity=capability["arity"],
                returns=capability["return_shape"],
                determinism=capability["determinism"],
                effects=", ".join(capability["side_effects"]) or "-",
                pure=_mark(capability["pure"]),
                prints=_mark(capability["may_print"]),
                throws=_mark(capability["may_throw"]),
                browser=_mark(capability["available_in_browser"]),
            )
        )
    return "\n".join(rows)


def _mark(value: bool) -> str:
    return "yes" if value else "no"
