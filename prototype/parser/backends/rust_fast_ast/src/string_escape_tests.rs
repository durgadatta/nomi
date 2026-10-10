use crate::lexer::lex;
use crate::token::TokenKind;

fn literal_value(source: &str) -> String {
    let tokens = lex(source).unwrap();
    match &tokens[0].kind {
        TokenKind::String { value, .. } => value.clone(),
        other => panic!("expected text token, got {other:?}"),
    }
}

#[test]
fn prototype_escape_values_are_decoded_without_losing_source_text() {
    for (source, expected) in [
        (r#""\x41\u00e9\U0001f600""#, "Aé😀"),
        (r#""\a\b\f\v\n\r\t""#, "\u{7}\u{8}\u{c}\u{b}\n\r\t"),
        (r#""\101\0\777""#, "A\0ǿ"),
        (r#""\q\z""#, "\\q\\z"),
        (r#"r"\x41\n""#, "\\x41\\n"),
        (r#"r"a\"b""#, "a\\\"b"),
        ("\"line\\\ncontinued\"", "linecontinued"),
    ] {
        assert_eq!(literal_value(source), expected, "{source}");
    }
}

#[test]
fn malformed_or_unrepresentable_escapes_refuse_instead_of_mutating_text() {
    for source in [
        r#""\xG1""#,
        r#""\x1""#,
        r#""\u123""#,
        r#""\uD800""#,
        r#""\U00110000""#,
        r#""\N{LATIN CAPITAL LETTER A}""#,
    ] {
        let error = lex(source).unwrap_err();
        assert!(error.message.contains("escape"), "{source}: {error}");
        assert_eq!(error.offset, 1, "{source}");
    }
}
