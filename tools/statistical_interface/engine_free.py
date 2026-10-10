"""Statistical descriptor adapter on the domain-neutral object envelope.

The statistical checker still owns its stricter metadata checks. This bridge
does not flatten scientific contracts into executable operations or new laws.
"""

from tools.object_interface import Graph, Vocabulary

from .model import catalog
from .objects import ObjectGraph


def descriptor_vocabulary():
    statistical_catalog = catalog()
    families = statistical_catalog["families"]
    operations = {}
    for family in families:
        operations["statistics." + family["id"]] = {
            "role": "description",
            "result": family["id"],
            "effects": [],
            "definition": None,
            "ports": {
                key: {
                    "accepts": contract["families"],
                    "multiplicity": contract["multiplicity"],
                }
                for key, contract in family["ports"].items()
            },
            "attributes": family["parameters"],
        }
    return Vocabulary.from_document(
        {
            "version": 1,
            "id": "nomi.statistical-descriptions",
            "revision": "v1",
            "types": {family["id"]: {"value": None} for family in families},
            "operations": operations,
        }
    )


def adapt_descriptions(document):
    checked = ObjectGraph.from_document(document)
    vocabulary = descriptor_vocabulary()
    source = checked.document
    return Graph.from_document(
        {
            "version": 1,
            "vocabulary": vocabulary.fingerprint,
            "objects": [
                {
                    "id": obj["id"],
                    "op": "statistics." + obj["family"],
                    "ports": obj["ports"],
                    "attributes": obj["parameters"],
                }
                for obj in source["objects"]
            ],
            "outputs": source["outputs"],
        },
        vocabulary,
    )
