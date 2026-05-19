from prototype.parser.nomi.usage import get_parser


def token_types(source: str) -> list[str]:
    return [token.type for token in get_parser().lex(source)]


def test_postlexer_marks_arrow_function_parameter_parens():
    tokens = token_types("inc = (x) => x + 1\n")

    assert tokens == [
        "NAME",
        "EQUAL",
        "_ARROW_LPAR",
        "NAME",
        "_ARROW_RPAR",
        "_FAT_ARROW",
        "NAME",
        "PLUS",
        "DEC_NUMBER",
        "_NEWLINE",
    ]


def test_postlexer_marks_operator_sections_without_call_parens():
    tokens = token_types("plus = (+)\nleft = (2*)\nright = (+2)\n")

    assert tokens.count("SECTION_OP") == 3
    assert tokens == [
        "NAME", "EQUAL", "LPAR", "SECTION_OP", "RPAR", "_NEWLINE",
        "NAME", "EQUAL", "LPAR", "DEC_NUMBER", "SECTION_OP", "RPAR", "_NEWLINE",
        "NAME", "EQUAL", "LPAR", "SECTION_OP", "DEC_NUMBER", "RPAR", "_NEWLINE",
    ]


def test_postlexer_marks_match_case_colon_and_guard_if():
    tokens = token_types(
        "match value:\n"
        "    case x if x > 0:\n"
        "        pass\n"
    )

    assert "_BLOCK_COLON" in tokens
    assert "_CASE_IF" in tokens
    assert "_CASE_COLON" in tokens


def test_postlexer_marks_postfix_flow_guards():
    tokens = token_types(
        "func f():\n"
        "    return 1 if ready\n"
        "    return 0 unless ready\n"
    )

    assert "_POSTFIX_IF" in tokens
    assert "_POSTFIX_UNLESS" in tokens


def test_postlexer_inserts_implicit_multiplication_star():
    tokens = token_types("x = 2foo\ny = 3(bar)\n")

    assert tokens == [
        "NAME", "EQUAL", "DEC_NUMBER", "STAR", "NAME", "_NEWLINE",
        "NAME", "EQUAL", "DEC_NUMBER", "STAR", "LPAR", "NAME", "RPAR", "_NEWLINE",
    ]
