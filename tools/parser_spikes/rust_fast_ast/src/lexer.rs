use crate::error::ParseError;
use crate::token::{Token, TokenKind};

pub(crate) fn lex(source: &str) -> Result<Vec<Token>, ParseError> {
    let mut tokens = Vec::new();
    let mut offset = 0;
    let mut line_start = true;
    let mut indents = vec![0usize];

    while offset < source.len() {
        if line_start {
            let (indent, next_offset, blank_line) = read_line_indent(source, offset);
            offset = next_offset;
            if blank_line {
                continue;
            }
            let current = *indents.last().expect("indent stack is never empty");
            if indent > current {
                indents.push(indent);
                tokens.push(Token {
                    kind: TokenKind::Indent,
                    offset,
                });
            } else {
                while indent < *indents.last().expect("indent stack is never empty") {
                    indents.pop();
                    tokens.push(Token {
                        kind: TokenKind::Dedent,
                        offset,
                    });
                }
                if indent != *indents.last().expect("indent stack is never empty") {
                    return Err(ParseError::new("inconsistent indentation", offset));
                }
            }
            line_start = false;
        }

        if offset >= source.len() {
            break;
        }

        let ch = source[offset..].chars().next().expect("valid char boundary");
        match ch {
            ' ' | '\t' | '\r' | '\x0c' => {
                offset += ch.len_utf8();
            }
            '\n' => {
                tokens.push(Token {
                    kind: TokenKind::Newline,
                    offset,
                });
                offset += ch.len_utf8();
                line_start = true;
            }
            '#' => {
                offset = skip_comment(source, offset);
            }
            '+' => {
                let next = offset + ch.len_utf8();
                if source[next..].starts_with('=') {
                    tokens.push(Token {
                        kind: TokenKind::PlusEqual,
                        offset,
                    });
                    offset = next + 1;
                } else {
                    tokens.push(Token {
                        kind: TokenKind::Plus,
                        offset,
                    });
                    offset = next;
                }
            }
            '-' => {
                let next = offset + ch.len_utf8();
                if source[next..].starts_with('>') {
                    tokens.push(Token {
                        kind: TokenKind::Arrow,
                        offset,
                    });
                    offset = next + 1;
                } else if source[next..].starts_with('=') {
                    tokens.push(Token {
                        kind: TokenKind::MinusEqual,
                        offset,
                    });
                    offset = next + 1;
                } else {
                    tokens.push(Token {
                        kind: TokenKind::Minus,
                        offset,
                    });
                    offset = next;
                }
            }
            '*' => {
                let next = offset + ch.len_utf8();
                if source[next..].starts_with('*') {
                    tokens.push(Token {
                        kind: TokenKind::DoubleStar,
                        offset,
                    });
                    offset = next + 1;
                } else if source[next..].starts_with('=') {
                    tokens.push(Token {
                        kind: TokenKind::StarEqual,
                        offset,
                    });
                    offset = next + 1;
                } else {
                    tokens.push(Token {
                        kind: TokenKind::Star,
                        offset,
                    });
                    offset = next;
                }
            }
            '/' => {
                let next = offset + ch.len_utf8();
                if source[next..].starts_with('/') {
                    tokens.push(Token {
                        kind: TokenKind::DoubleSlash,
                        offset,
                    });
                    offset = next + 1;
                } else if source[next..].starts_with('=') {
                    tokens.push(Token {
                        kind: TokenKind::SlashEqual,
                        offset,
                    });
                    offset = next + 1;
                } else {
                    tokens.push(Token {
                        kind: TokenKind::Slash,
                        offset,
                    });
                    offset = next;
                }
            }
            '$' => {
                tokens.push(Token {
                    kind: TokenKind::Dollar,
                    offset,
                });
                offset += ch.len_utf8();
            }
            '|' => {
                let next = offset + ch.len_utf8();
                if source[next..].starts_with('>') {
                    tokens.push(Token {
                        kind: TokenKind::PipeGreater,
                        offset,
                    });
                    offset = next + 1;
                } else {
                    tokens.push(Token {
                        kind: TokenKind::Pipe,
                        offset,
                    });
                    offset = next;
                }
            }
            '?' => {
                let next = offset + ch.len_utf8();
                if source[next..].starts_with('?') {
                    tokens.push(Token {
                        kind: TokenKind::QuestionQuestion,
                        offset,
                    });
                    offset = next + 1;
                } else if source[next..].starts_with('.') {
                    tokens.push(Token {
                        kind: TokenKind::QuestionDot,
                        offset,
                    });
                    offset = next + 1;
                } else {
                    tokens.push(Token {
                        kind: TokenKind::Question,
                        offset,
                    });
                    offset = next;
                }
            }
            '%' => {
                tokens.push(Token {
                    kind: TokenKind::Percent,
                    offset,
                });
                offset += ch.len_utf8();
            }
            '@' => {
                tokens.push(Token {
                    kind: TokenKind::At,
                    offset,
                });
                offset += ch.len_utf8();
            }
            '=' => {
                let next = offset + ch.len_utf8();
                if source[next..].starts_with('>') {
                    tokens.push(Token {
                        kind: TokenKind::FatArrow,
                        offset,
                    });
                    offset = next + 1;
                } else if source[next..].starts_with('=') {
                    tokens.push(Token {
                        kind: TokenKind::DoubleEqual,
                        offset,
                    });
                    offset = next + 1;
                } else {
                    tokens.push(Token {
                        kind: TokenKind::Equal,
                        offset,
                    });
                    offset = next;
                }
            }
            '!' => {
                let next = offset + ch.len_utf8();
                if source[next..].starts_with('=') {
                    tokens.push(Token {
                        kind: TokenKind::NotEqual,
                        offset,
                    });
                    offset = next + 1;
                } else {
                    return Err(ParseError::new("unexpected character '!'", offset));
                }
            }
            '<' => {
                let next = offset + ch.len_utf8();
                if source[next..].starts_with('=') {
                    tokens.push(Token {
                        kind: TokenKind::LessEqual,
                        offset,
                    });
                    offset = next + 1;
                } else {
                    tokens.push(Token {
                        kind: TokenKind::Less,
                        offset,
                    });
                    offset = next;
                }
            }
            '>' => {
                let next = offset + ch.len_utf8();
                if source[next..].starts_with('=') {
                    tokens.push(Token {
                        kind: TokenKind::GreaterEqual,
                        offset,
                    });
                    offset = next + 1;
                } else {
                    tokens.push(Token {
                        kind: TokenKind::Greater,
                        offset,
                    });
                    offset = next;
                }
            }
            '(' => {
                tokens.push(Token {
                    kind: TokenKind::LParen,
                    offset,
                });
                offset += ch.len_utf8();
            }
            ')' => {
                tokens.push(Token {
                    kind: TokenKind::RParen,
                    offset,
                });
                offset += ch.len_utf8();
            }
            '[' => {
                tokens.push(Token {
                    kind: TokenKind::LBracket,
                    offset,
                });
                offset += ch.len_utf8();
            }
            ']' => {
                tokens.push(Token {
                    kind: TokenKind::RBracket,
                    offset,
                });
                offset += ch.len_utf8();
            }
            '{' => {
                tokens.push(Token {
                    kind: TokenKind::LBrace,
                    offset,
                });
                offset += ch.len_utf8();
            }
            '}' => {
                tokens.push(Token {
                    kind: TokenKind::RBrace,
                    offset,
                });
                offset += ch.len_utf8();
            }
            '.' => {
                let next = offset + ch.len_utf8();
                if source[next..].starts_with(".<") {
                    tokens.push(Token {
                        kind: TokenKind::DotDotLess,
                        offset,
                    });
                    offset = next + 2;
                } else if source[next..].starts_with('.') {
                    tokens.push(Token {
                        kind: TokenKind::DotDot,
                        offset,
                    });
                    offset = next + 1;
                } else {
                    tokens.push(Token {
                        kind: TokenKind::Dot,
                        offset,
                    });
                    offset = next;
                }
            }
            ':' => {
                tokens.push(Token {
                    kind: TokenKind::Colon,
                    offset,
                });
                offset += ch.len_utf8();
            }
            ',' => {
                tokens.push(Token {
                    kind: TokenKind::Comma,
                    offset,
                });
                offset += ch.len_utf8();
            }
            ';' => {
                tokens.push(Token {
                    kind: TokenKind::Semi,
                    offset,
                });
                offset += ch.len_utf8();
            }
            '"' | '\'' => {
                let (value, next_offset) = read_string(source, offset, ch)?;
                tokens.push(Token {
                    kind: TokenKind::String(value),
                    offset,
                });
                offset = next_offset;
            }
            '0'..='9' => {
                let (value, next_offset) = read_number(source, offset);
                tokens.push(Token {
                    kind: TokenKind::Number(value),
                    offset,
                });
                offset = next_offset;
            }
            _ if is_string_prefix_at(source, offset) => {
                let (value, next_offset) = read_prefixed_string(source, offset)?;
                tokens.push(Token {
                    kind: TokenKind::String(value),
                    offset,
                });
                offset = next_offset;
            }
            _ if is_name_start(ch) => {
                let (value, next_offset) = read_name(source, offset);
                tokens.push(Token {
                    kind: TokenKind::Name(value),
                    offset,
                });
                offset = next_offset;
            }
            _ => {
                return Err(ParseError::new(
                    format!("unexpected character {ch:?}"),
                    offset,
                ));
            }
        };
    }

    while indents.len() > 1 {
        indents.pop();
        tokens.push(Token {
            kind: TokenKind::Dedent,
            offset: source.len(),
        });
    }
    tokens.push(Token {
        kind: TokenKind::Eof,
        offset: source.len(),
    });
    Ok(tokens)
}

fn read_line_indent(source: &str, start: usize) -> (usize, usize, bool) {
    let mut offset = start;
    let mut indent = 0usize;
    while offset < source.len() {
        let ch = source[offset..].chars().next().expect("valid char boundary");
        match ch {
            ' ' => {
                indent += 1;
                offset += ch.len_utf8();
            }
            '\t' => {
                indent += 8 - (indent % 8);
                offset += ch.len_utf8();
            }
            '\r' | '\x0c' => {
                offset += ch.len_utf8();
            }
            '\n' => return (indent, offset + ch.len_utf8(), true),
            '#' => {
                let comment_end = skip_comment(source, offset);
                if comment_end < source.len() && source[comment_end..].starts_with('\n') {
                    return (indent, comment_end + 1, true);
                }
                return (indent, comment_end, true);
            }
            _ => return (indent, offset, false),
        }
    }
    (indent, offset, true)
}

fn skip_comment(source: &str, mut offset: usize) -> usize {
    while offset < source.len() {
        let ch = source[offset..].chars().next().expect("valid char boundary");
        if ch == '\n' {
            break;
        }
        offset += ch.len_utf8();
    }
    offset
}

fn read_prefixed_string(source: &str, start: usize) -> Result<(String, usize), ParseError> {
    let mut quote_offset = start;
    while quote_offset < source.len() {
        let ch = source[quote_offset..]
            .chars()
            .next()
            .expect("valid char boundary");
        if ch == '"' || ch == '\'' {
            return read_string(source, quote_offset, ch);
        }
        quote_offset += ch.len_utf8();
    }
    Err(ParseError::new("expected string after prefix", start))
}

fn is_string_prefix_at(source: &str, start: usize) -> bool {
    let mut offset = start;
    let mut saw_prefix = false;
    while offset < source.len() {
        let ch = source[offset..].chars().next().expect("valid char boundary");
        if matches!(ch, 'f' | 'F' | 'r' | 'R' | 'u' | 'U' | 'b' | 'B') {
            saw_prefix = true;
            offset += ch.len_utf8();
            continue;
        }
        return saw_prefix && (ch == '"' || ch == '\'');
    }
    false
}

fn read_string(source: &str, start: usize, quote: char) -> Result<(String, usize), ParseError> {
    let quote_len = quote.len_utf8();
    let triple = source[start + quote_len..].starts_with(quote)
        && source[start + quote_len * 2..].starts_with(quote);
    let content_start = if triple {
        start + quote_len * 3
    } else {
        start + quote_len
    };
    let mut escaped = false;
    let mut value = String::new();
    let mut offset = content_start;
    while offset < source.len() {
        let ch = source[offset..].chars().next().expect("valid char boundary");
        if escaped {
            let decoded = match ch {
                'n' => '\n',
                'r' => '\r',
                't' => '\t',
                '\\' => '\\',
                '"' => '"',
                '\'' => '\'',
                other => other,
            };
            value.push(decoded);
            escaped = false;
            offset += ch.len_utf8();
        } else if ch == '\\' {
            escaped = true;
            offset += ch.len_utf8();
        } else if triple
            && ch == quote
            && source[offset + quote_len..].starts_with(quote)
            && source[offset + quote_len * 2..].starts_with(quote)
        {
            return Ok((value, offset + quote_len * 3));
        } else if !triple && ch == quote {
            return Ok((value, offset + ch.len_utf8()));
        } else if !triple && ch == '\n' {
            return Err(ParseError::new("unterminated string", offset));
        } else {
            value.push(ch);
            offset += ch.len_utf8();
        }
    }
    Err(ParseError::new("unterminated string", start))
}

fn read_number(source: &str, start: usize) -> (String, usize) {
    let mut end = start;
    let mut dot_seen = false;
    for (offset, ch) in source[start..].char_indices() {
        if ch.is_ascii_digit() || ch == '_' {
            end = start + offset + ch.len_utf8();
        } else if ch == '.'
            && !dot_seen
            && !source[start + offset + ch.len_utf8()..].starts_with('.')
        {
            dot_seen = true;
            end = start + offset + ch.len_utf8();
        } else {
            break;
        }
    }
    (source[start..end].to_string(), end)
}

fn read_name(source: &str, start: usize) -> (String, usize) {
    let mut end = start;
    for (offset, ch) in source[start..].char_indices() {
        if is_name_continue(ch) {
            end = start + offset + ch.len_utf8();
        } else {
            break;
        }
    }
    (source[start..end].to_string(), end)
}

fn is_name_start(ch: char) -> bool {
    ch == '_' || ch.is_alphabetic()
}

fn is_name_continue(ch: char) -> bool {
    ch == '_' || ch.is_alphanumeric()
}
