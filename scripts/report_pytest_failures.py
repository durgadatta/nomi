"""Expose pytest failures as GitHub annotations without needing log access."""

from __future__ import annotations

from pathlib import Path
import sys
import xml.etree.ElementTree as ET


def annotations(path: Path) -> list[str]:
    if not path.is_file():
        return []
    result = []
    for case in ET.parse(path).iter("testcase"):
        for outcome in case:
            if outcome.tag not in {"failure", "error"}:
                continue
            name = ".".join(filter(None, [case.get("classname"), case.get("name")]))
            detail = outcome.text or outcome.get("message", "")
            message = f"{name}: {detail[-8000:]}"
            escaped = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
            result.append(f"::error::{escaped}")
    return result


if __name__ == "__main__":
    for annotation in annotations(Path(sys.argv[1])):
        print(annotation)
