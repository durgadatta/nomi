from pathlib import Path

from tools.syntax import grammar_ref


def test_build_reference_text_includes_regeneration_command_and_layers():
    text = grammar_ref.build_reference_text()

    assert text.startswith("// Nomi grammar - assembled from layers")
    assert "python3 -m tools.syntax.grammar_ref" in text
    assert "// Layer: terminals" in text
    assert "// Layer: calls" in text


def test_reference_check_detects_current_and_stale_files(tmp_path: Path):
    path = tmp_path / "nomi.ref.lark"

    grammar_ref.write_reference_grammar(path)
    assert grammar_ref.is_reference_current(path)

    path.write_text("stale\n", encoding="utf-8")
    assert not grammar_ref.is_reference_current(path)
