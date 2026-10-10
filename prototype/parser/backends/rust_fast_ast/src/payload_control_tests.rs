use crate::payload::json_string;

#[test]
fn every_json_control_character_has_an_escaped_representation() {
    for code in 0_u32..=31 {
        let value = char::from_u32(code).unwrap().to_string();
        let expected = match code {
            9 => "\"\\t\"".to_string(),
            10 => "\"\\n\"".to_string(),
            13 => "\"\\r\"".to_string(),
            _ => format!("\"\\u{code:04x}\""),
        };
        assert_eq!(json_string(&value), expected, "U+{code:04X}");
    }
}

#[test]
fn parsed_literal_controls_are_escaped_in_value_and_source_fields() {
    let payload = crate::parse_to_json("value = '\u{b}\u{1c}Ada'\n").unwrap();
    assert!(!payload.contains('\u{b}'));
    assert!(!payload.contains('\u{1c}'));
    assert_eq!(payload.matches("\\u000b").count(), 2);
    assert_eq!(payload.matches("\\u001c").count(), 2);
}

#[test]
fn ordinary_unicode_is_preserved_without_host_normalization() {
    assert_eq!(
        json_string("Ada😀\u{85}\u{3000}"),
        "\"Ada😀\u{85}\u{3000}\""
    );
}
