"""Pinned plain-text document profile; explicit, replaceable pure renderers."""

from pathlib import Path

from .backend import Backend
from .documents import ContractError, load_document
from .model import Vocabulary

ROOT = Path(__file__).resolve().parents[2]


def document_vocabulary():
    return Vocabulary.from_document(
        load_document(ROOT / "config/document_interface.json")
    )


def _blocks(ports, attributes):
    spec = ports["spec"]
    blocks = [spec["title"]]
    for section in spec["sections"]:
        blocks.append(section["heading"])
        blocks.extend(section["paragraphs"])
    return "\n\n".join(blocks) + "\n"


def _stream(ports, attributes):
    spec = ports["spec"]
    content = spec["title"]
    for section in spec["sections"]:
        content += "\n\n" + section["heading"]
        for paragraph in section["paragraphs"]:
            content += "\n\n" + paragraph
    return content + "\n"


def document_backend(vocabulary, profile="blocks"):
    if vocabulary.fingerprint != document_vocabulary().fingerprint:
        raise ContractError("document backend requires the tracked document vocabulary")
    if profile not in ("blocks", "stream"):
        raise ContractError("unknown document rendering profile")
    return Backend(
        "document-" + profile,
        "v1",
        vocabulary.fingerprint,
        {
            "document.render_text": _blocks if profile == "blocks" else _stream,
            "document.title": lambda p, a: p["spec"]["title"],
            "document.paragraph_count": lambda p, a: sum(
                len(section["paragraphs"]) for section in p["spec"]["sections"]
            ),
            "rendered.as_text": lambda p, a: p["value"],
        },
    )
