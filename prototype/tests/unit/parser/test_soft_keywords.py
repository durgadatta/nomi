import pytest

from prototype.parser.nomi.usage import generate_ast
from prototype.syntax.features import get_declared_soft_keywords


EXPECTED_SOFT_KEYWORDS = {"match", "case", "type", "by", "guard", "data"}


def test_feature_manifest_declares_current_soft_keywords():
    assert set(get_declared_soft_keywords()) == EXPECTED_SOFT_KEYWORDS


@pytest.mark.parametrize("keyword", sorted(EXPECTED_SOFT_KEYWORDS))
def test_soft_keywords_parse_as_names_outside_feature_positions(keyword):
    tree = generate_ast(code=f"{keyword} = 1\nresult = {keyword}\n")

    assert tree.body[0].targets[0].id == keyword
    assert tree.body[1].targets[0].id == "result"
    assert tree.body[1].value.id == keyword
