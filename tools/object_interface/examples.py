"""Explicit lab vocabulary and replaceable pure implementation. No discovery."""

from pathlib import Path

from .backend import Backend
from .documents import ContractError, load_document
from .model import Vocabulary

ROOT = Path(__file__).resolve().parents[2]


def lab_vocabulary():
    return Vocabulary.from_document(
        load_document(ROOT / "config/object_interface.json")
    )


def python_backend(vocabulary):
    if vocabulary.fingerprint != lab_vocabulary().fingerprint:
        raise ContractError("example backend requires the tracked lab vocabulary")

    def exact(op):
        def run(ports, attributes):
            left, right = ports["left"], ports["right"]
            if max(left.bit_length(), right.bit_length()) > 4096:
                raise ContractError("example backend integer capacity exceeded")
            result = op(left, right)
            if result.bit_length() > 4096:
                raise ContractError("example backend integer capacity exceeded")
            return result

        return run

    return Backend(
        "python-exact-text",
        "v1",
        vocabulary.fingerprint,
        {
            "exact.add": exact(lambda left, right: left + right),
            "exact.multiply": exact(lambda left, right: left * right),
            "text.concat": lambda ports, attributes: ports["left"] + ports["right"],
        },
    )
