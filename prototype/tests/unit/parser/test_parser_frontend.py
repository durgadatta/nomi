from prototype.parser.nomi.frontend import (
    DEFAULT_FRONTEND,
    PARSER_FRONTEND_CANDIDATES,
    ParserFrontendCapabilities,
    ParserFrontendSpec,
    get_parser_frontend,
    get_selectable_parser_frontends,
    render_parser_frontend_table,
)


def test_default_parser_frontend_exposes_current_lark_path():
    frontend = get_parser_frontend()

    assert frontend.spec.name == DEFAULT_FRONTEND
    assert frontend.spec.grammar_format == "layered Lark grammar"
    assert frontend.spec.output_contract == "layer-transformed tree for NomiToPythonAST"
    assert frontend.spec.capabilities.parse_current_grammar is True
    assert frontend.spec.capabilities.lower_to_python_ast is True


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
    assert "| frontend | status | full grammar | python AST | selectable |" in table
    assert "Nomi Surface IR, then Python AST backend" in table


def test_only_full_parity_frontends_are_selectable_for_execution():
    assert get_selectable_parser_frontends() == ("lark-lalr",)

    non_lark_frontends = [
        spec for spec in PARSER_FRONTEND_CANDIDATES if spec.name != "lark-lalr"
    ]
    assert non_lark_frontends
    assert all(
        not spec.capabilities.selectable_for_execution
        for spec in non_lark_frontends
    )


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
                capabilities=ParserFrontendCapabilities(
                    parse_current_grammar=True,
                    lower_to_python_ast=True,
                ),
            ),
        )
    )

    assert "example grammar" in table
    assert "| example | research-candidate | yes | yes | no |" in table
