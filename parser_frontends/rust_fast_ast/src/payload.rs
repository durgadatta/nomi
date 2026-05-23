pub(crate) fn json_object(fields: Vec<(&'static str, String)>) -> String {
    let fields = fields
        .into_iter()
        .map(|(name, value)| format!("{}:{}", json_string(name), value))
        .collect::<Vec<_>>()
        .join(",");
    format!("{{{fields}}}")
}

pub(crate) fn json_array(items: impl IntoIterator<Item = String>) -> String {
    let items = items.into_iter().collect::<Vec<_>>().join(",");
    format!("[{items}]")
}

pub(crate) fn json_null() -> String {
    "null".to_string()
}

pub(crate) fn json_string(value: &str) -> String {
    let mut escaped = String::from("\"");
    for ch in value.chars() {
        match ch {
            '"' => escaped.push_str("\\\""),
            '\\' => escaped.push_str("\\\\"),
            '\n' => escaped.push_str("\\n"),
            '\r' => escaped.push_str("\\r"),
            '\t' => escaped.push_str("\\t"),
            other => escaped.push(other),
        }
    }
    escaped.push('"');
    escaped
}
