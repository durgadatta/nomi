from prototype.parser.nomi.frontend import (
    DEFAULT_FRONTEND,
    ParserFrontendSpec,
    get_parser_frontend,
    render_parser_frontend_table,
)


def test_default_parser_frontend_exposes_current_lark_path():
    frontend = get_parser_frontend()

    assert frontend.spec.name == DEFAULT_FRONTEND
    assert frontend.spec.grammar_format == "layered Lark grammar"
    assert frontend.spec.output_contract == "layer-transformed tree for NomiToPythonAST"


def test_parser_frontend_artifacts_keep_python_ast_backend_separate():
    frontend = get_parser_frontend()

    artifacts = frontend.parse_artifacts(code="x = 1\n", preserve_positions=False)

    assert artifacts.frontend.name == "lark-lalr"
    assert artifacts.raw_tree is not None
    assert artifacts.transformed_tree is not None


def test_parser_frontend_table_names_planned_non_lark_spikes():
    table = render_parser_frontend_table()

    assert "tree-sitter-cst" in table
    assert "rust-peg-cst" in table
    assert "Nomi Surface IR, then Python AST backend" in table


def test_parser_frontend_table_accepts_explicit_specs():
    table = render_parser_frontend_table(
        (
            ParserFrontendSpec(
                name="example",
                status="research-candidate",
                grammar_format="example grammar",
                implementation="example implementation",
                cst_artifact="example tree",
                output_contract="example output",
            ),
        )
    )

    assert "example grammar" in table
