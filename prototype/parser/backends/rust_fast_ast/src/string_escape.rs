//! Decoding for the current Python-compatible prototype literal subset.

use crate::error::ParseError;

pub(crate) fn decode(source: &str, start: usize) -> Result<(String, usize), ParseError> {
    let offset = start + 1;
    let ch = source[offset..]
        .chars()
        .next()
        .ok_or_else(|| ParseError::new("unterminated string escape", start))?;
    let next = offset + ch.len_utf8();
    let simple = match ch {
        'a' => Some('\u{7}'),
        'b' => Some('\u{8}'),
        'f' => Some('\u{c}'),
        'v' => Some('\u{b}'),
        'n' => Some('\n'),
        'r' => Some('\r'),
        't' => Some('\t'),
        '\\' | '"' | '\'' => Some(ch),
        _ => None,
    };
    if let Some(value) = simple {
        return Ok((value.to_string(), next));
    }
    if ch == '\n' {
        return Ok((String::new(), next));
    }
    if ch == '\r' && source[next..].starts_with('\n') {
        return Ok((String::new(), next + 1));
    }
    if matches!(ch, 'x' | 'u' | 'U') {
        let digits = match ch {
            'x' => 2,
            'u' => 4,
            _ => 8,
        };
        let bytes = source.as_bytes().get(next..next + digits);
        if !bytes.is_some_and(|value| value.iter().all(u8::is_ascii_hexdigit)) {
            return Err(ParseError::new(
                format!("invalid \\{ch} string escape; expected {digits} hexadecimal digits"),
                start,
            ));
        }
        let value = u32::from_str_radix(&source[next..next + digits], 16).unwrap();
        let decoded = char::from_u32(value)
            .ok_or_else(|| ParseError::new("string escape is not a Unicode scalar value", start))?;
        return Ok((decoded.to_string(), next + digits));
    }
    if matches!(ch, '0'..='7') {
        let mut end = next;
        for digit in source[next..].chars().take(2) {
            if !matches!(digit, '0'..='7') {
                break;
            }
            end += 1;
        }
        let value = u32::from_str_radix(&source[offset..end], 8).unwrap();
        return Ok((char::from_u32(value).unwrap().to_string(), end));
    }
    if ch == 'N' {
        return Err(ParseError::new("named Unicode string escapes are not supported by this prototype parser; use a literal character or \\u/\\U", start));
    }
    // Python-compatible unknown escapes retain their backslash. Target escape
    // admission is independent of this compatibility decoder.
    Ok((format!("\\{ch}"), next))
}
