use std::collections::{BTreeMap, BTreeSet};

use crate::lexer::lex;
use crate::payload::{json_array, json_null, json_object, json_string};
use crate::token::{same_variant, token_name, token_text, Token, TokenKind};

const PATTERN_SURFACE_SCHEMA: &str = "nomi.pattern-surface";
const PATTERN_SURFACE_VERSION: usize = 1;
const INVALID_PATTERN_SYNTAX: &str = "InvalidPatternSyntax";
const DUPLICATE_PATTERN_CAPTURE: &str = "DuplicatePatternCapture";
const ALTERNATIVE_BINDING_MISMATCH: &str = "AlternativeBindingMismatch";
const MULTIPLE_PATTERN_REMAINDERS: &str = "MultiplePatternRemainders";
const MAP_PATTERN_REST_NOT_LAST: &str = "MapPatternRestNotLast";
const DUPLICATE_MAP_PATTERN_KEY: &str = "DuplicateMapPatternKey";
const RESERVED_PATTERN_NAMES: &[&str] = &[
    "actor",
    "and",
    "as",
    "async",
    "await",
    "break",
    "catch",
    "check",
    "class",
    "continue",
    "data",
    "defer",
    "effect",
    "else",
    "example",
    "extend",
    "false",
    "for",
    "from",
    "func",
    "generator",
    "if",
    "import",
    "in",
    "interface",
    "macro",
    "match",
    "none",
    "not",
    "note",
    "or",
    "panic",
    "protocol",
    "pub",
    "raise",
    "return",
    "set",
    "then",
    "trait",
    "true",
    "type",
    "uses",
    "var",
    "when",
    "where",
    "while",
    "with",
    "yield",
];

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
struct Span {
    start: usize,
    end: usize,
}

impl Span {
    fn to_json(self) -> String {
        json_object(vec![
            ("start", self.start.to_string()),
            ("end", self.end.to_string()),
        ])
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct PatternFailure {
    code: &'static str,
    span: Span,
    subject: Option<String>,
}

impl PatternFailure {
    fn invalid(source: &str) -> Self {
        Self {
            code: INVALID_PATTERN_SYNTAX,
            span: Span {
                start: 0,
                end: source.len(),
            },
            subject: None,
        }
    }

    fn structured(code: &'static str, span: Span, subject: Option<String>) -> Self {
        Self {
            code,
            span,
            subject,
        }
    }

    fn message(&self) -> String {
        match self.code {
            INVALID_PATTERN_SYNTAX => {
                "Pattern source does not conform to Pattern Surface v1.".to_string()
            }
            DUPLICATE_PATTERN_CAPTURE => format!(
                "Pattern capture `{}` appears more than once.",
                self.subject.as_deref().unwrap_or("")
            ),
            ALTERNATIVE_BINDING_MISMATCH => {
                "Or-pattern alternatives must capture the same names.".to_string()
            }
            MULTIPLE_PATTERN_REMAINDERS => {
                "A collection pattern can contain at most one `..` remainder.".to_string()
            }
            MAP_PATTERN_REST_NOT_LAST => {
                "A map `..` remainder must be the final entry.".to_string()
            }
            DUPLICATE_MAP_PATTERN_KEY => format!(
                "Map pattern key {} appears more than once.",
                self.subject.as_deref().unwrap_or("")
            ),
            _ => unreachable!("all Pattern Surface diagnostic codes have messages"),
        }
    }

    fn to_json(&self) -> String {
        json_object(vec![
            ("code", json_string(self.code)),
            ("message", json_string(&self.message())),
            ("span", self.span.to_json()),
        ])
    }
}

type PatternResult<T> = Result<T, PatternFailure>;

#[derive(Debug, Clone, PartialEq, Eq)]
enum LiteralValue {
    None,
    Bool(bool),
    String(String),
}

impl LiteralValue {
    fn to_json(&self) -> String {
        match self {
            Self::None => json_null(),
            Self::Bool(value) => value.to_string(),
            Self::String(value) => json_string(value),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct LiteralPattern {
    literal_kind: &'static str,
    value: LiteralValue,
    lexeme: String,
    span: Span,
}

impl LiteralPattern {
    fn identity(&self) -> String {
        format!("{}:{}", self.literal_kind, self.value.to_json())
    }

    fn to_json(&self) -> String {
        json_object(vec![
            ("kind", json_string("LiteralPattern")),
            ("literal_kind", json_string(self.literal_kind)),
            ("value", self.value.to_json()),
            ("lexeme", json_string(&self.lexeme)),
            ("span", self.span.to_json()),
        ])
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct PatternRest {
    capture: Option<String>,
    span: Span,
}

impl PatternRest {
    fn to_json(&self) -> String {
        json_object(vec![
            (
                "capture",
                self.capture
                    .as_deref()
                    .map(json_string)
                    .unwrap_or_else(json_null),
            ),
            ("span", self.span.to_json()),
        ])
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct MapPatternEntry {
    key: LiteralPattern,
    pattern: Pattern,
    span: Span,
}

impl MapPatternEntry {
    fn to_json(&self) -> String {
        json_object(vec![
            ("key", self.key.to_json()),
            ("pattern", self.pattern.to_json()),
            ("span", self.span.to_json()),
        ])
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
enum Pattern {
    Wildcard {
        span: Span,
    },
    Capture {
        name: String,
        span: Span,
    },
    Literal(LiteralPattern),
    Nominal {
        path: Vec<String>,
        arguments: Vec<Pattern>,
        payload_syntax: bool,
        span: Span,
    },
    Tuple {
        items: Vec<Pattern>,
        span: Span,
    },
    List {
        prefix: Vec<Pattern>,
        rest: Option<PatternRest>,
        suffix: Vec<Pattern>,
        span: Span,
    },
    Map {
        entries: Vec<MapPatternEntry>,
        rest: Option<PatternRest>,
        span: Span,
    },
    Or {
        alternatives: Vec<Pattern>,
        span: Span,
    },
    As {
        pattern: Box<Pattern>,
        capture: String,
        capture_span: Span,
        span: Span,
    },
}

impl Pattern {
    fn span(&self) -> Span {
        match self {
            Self::Wildcard { span }
            | Self::Capture { span, .. }
            | Self::Nominal { span, .. }
            | Self::Tuple { span, .. }
            | Self::List { span, .. }
            | Self::Map { span, .. }
            | Self::Or { span, .. }
            | Self::As { span, .. } => *span,
            Self::Literal(pattern) => pattern.span,
        }
    }

    fn with_span(mut self, span: Span) -> Self {
        match &mut self {
            Self::Wildcard { span: current }
            | Self::Capture { span: current, .. }
            | Self::Nominal { span: current, .. }
            | Self::Tuple { span: current, .. }
            | Self::List { span: current, .. }
            | Self::Map { span: current, .. }
            | Self::Or { span: current, .. }
            | Self::As { span: current, .. } => *current = span,
            Self::Literal(pattern) => pattern.span = span,
        }
        self
    }

    fn to_json(&self) -> String {
        match self {
            Self::Wildcard { span } => json_object(vec![
                ("kind", json_string("WildcardPattern")),
                ("span", span.to_json()),
            ]),
            Self::Capture { name, span } => json_object(vec![
                ("kind", json_string("CapturePattern")),
                ("name", json_string(name)),
                ("span", span.to_json()),
            ]),
            Self::Literal(pattern) => pattern.to_json(),
            Self::Nominal {
                path,
                arguments,
                payload_syntax,
                span,
            } => json_object(vec![
                ("kind", json_string("NominalPattern")),
                (
                    "path",
                    json_array(path.iter().map(|part| json_string(part))),
                ),
                (
                    "arguments",
                    json_array(arguments.iter().map(Pattern::to_json)),
                ),
                ("payload_syntax", payload_syntax.to_string()),
                ("span", span.to_json()),
            ]),
            Self::Tuple { items, span } => json_object(vec![
                ("kind", json_string("TuplePattern")),
                ("items", json_array(items.iter().map(Pattern::to_json))),
                ("span", span.to_json()),
            ]),
            Self::List {
                prefix,
                rest,
                suffix,
                span,
            } => json_object(vec![
                ("kind", json_string("ListPattern")),
                ("prefix", json_array(prefix.iter().map(Pattern::to_json))),
                (
                    "rest",
                    rest.as_ref()
                        .map(PatternRest::to_json)
                        .unwrap_or_else(json_null),
                ),
                ("suffix", json_array(suffix.iter().map(Pattern::to_json))),
                ("span", span.to_json()),
            ]),
            Self::Map {
                entries,
                rest,
                span,
            } => json_object(vec![
                ("kind", json_string("MapPattern")),
                (
                    "entries",
                    json_array(entries.iter().map(MapPatternEntry::to_json)),
                ),
                (
                    "openness",
                    json_string(if rest.is_some() { "open" } else { "exact" }),
                ),
                (
                    "rest",
                    rest.as_ref()
                        .map(PatternRest::to_json)
                        .unwrap_or_else(json_null),
                ),
                ("span", span.to_json()),
            ]),
            Self::Or { alternatives, span } => json_object(vec![
                ("kind", json_string("OrPattern")),
                (
                    "alternatives",
                    json_array(alternatives.iter().map(Pattern::to_json)),
                ),
                ("span", span.to_json()),
            ]),
            Self::As {
                pattern,
                capture,
                capture_span,
                span,
            } => json_object(vec![
                ("kind", json_string("AsPattern")),
                ("pattern", pattern.to_json()),
                ("capture", json_string(capture)),
                ("capture_span", capture_span.to_json()),
                ("span", span.to_json()),
            ]),
        }
    }
}

enum ListItem {
    Pattern(Pattern),
    Rest(PatternRest),
}

struct PatternParser<'a> {
    source: &'a str,
    tokens: Vec<Token>,
    index: usize,
}

impl<'a> PatternParser<'a> {
    fn new(source: &'a str, tokens: Vec<Token>) -> Self {
        Self {
            source,
            tokens,
            index: 0,
        }
    }

    fn parse_document(mut self) -> PatternResult<Pattern> {
        let root = self.parse_pattern()?;
        self.expect(&TokenKind::Eof)?;
        Ok(root)
    }

    fn parse_pattern(&mut self) -> PatternResult<Pattern> {
        let pattern = self.parse_or_pattern()?;
        if !self.peek_name("as") {
            return Ok(pattern);
        }

        self.advance();
        let capture_token = self.expect_capture("expected a capture name after 'as'")?;
        let capture = name_value(&capture_token).to_string();
        let capture_span = self.token_span(&capture_token);
        Ok(Pattern::As {
            span: Span {
                start: pattern.span().start,
                end: capture_span.end,
            },
            pattern: Box::new(pattern),
            capture,
            capture_span,
        })
    }

    fn parse_or_pattern(&mut self) -> PatternResult<Pattern> {
        let first = self.parse_primary_pattern()?;
        if !self.check(&TokenKind::Pipe) {
            return Ok(first);
        }

        let start = first.span().start;
        let mut alternatives = vec![first];
        while self.consume(&TokenKind::Pipe).is_some() {
            alternatives.push(self.parse_primary_pattern()?);
        }
        let end = alternatives
            .last()
            .expect("or-pattern has at least two alternatives")
            .span()
            .end;
        Ok(Pattern::Or {
            alternatives,
            span: Span { start, end },
        })
    }

    fn parse_primary_pattern(&mut self) -> PatternResult<Pattern> {
        let token = self.peek().clone();
        match &token.kind {
            TokenKind::Name(name) if name == "_" => {
                self.advance();
                Ok(Pattern::Wildcard {
                    span: self.token_span(&token),
                })
            }
            TokenKind::Name(name) if matches!(name.as_str(), "none" | "true" | "false") => {
                self.advance();
                Ok(Pattern::Literal(named_literal(
                    name,
                    self.token_span(&token),
                )))
            }
            TokenKind::Name(name) if is_capture_name(name) => {
                self.advance();
                Ok(Pattern::Capture {
                    name: name.clone(),
                    span: self.token_span(&token),
                })
            }
            TokenKind::Name(name) if is_type_name(name) => self.parse_nominal_pattern(),
            TokenKind::Name(name) => {
                Err(self.error_at(format!("invalid pattern name {name:?}"), token.offset))
            }
            TokenKind::Number(_) | TokenKind::Minus => {
                self.parse_integer_literal().map(Pattern::Literal)
            }
            TokenKind::String { .. } => self.parse_string_literal().map(Pattern::Literal),
            TokenKind::LParen => self.parse_parenthesized_pattern(),
            TokenKind::LBracket => self.parse_list_pattern(),
            TokenKind::LBrace => self.parse_map_pattern(),
            _ => Err(self.error_at(
                format!("expected a pattern, found {}", token_name(&token.kind)),
                token.offset,
            )),
        }
    }

    fn parse_nominal_pattern(&mut self) -> PatternResult<Pattern> {
        let first = self.advance();
        let start = first.offset;
        let mut end = self.token_end(&first);
        let mut path = vec![name_value(&first).to_string()];

        while self.consume(&TokenKind::Dot).is_some() {
            let part = self.expect_name("expected a nominal path component after '.'")?;
            let value = name_value(&part);
            if !is_name_part(value) {
                return Err(self.error_at("invalid nominal path component", part.offset));
            }
            path.push(value.to_string());
            end = self.token_end(&part);
        }

        if self.consume(&TokenKind::LParen).is_none() {
            return Ok(Pattern::Nominal {
                path,
                arguments: Vec::new(),
                payload_syntax: false,
                span: Span { start, end },
            });
        }

        let mut arguments = Vec::new();
        if !self.check(&TokenKind::RParen) {
            loop {
                arguments.push(self.parse_pattern()?);
                if self.consume(&TokenKind::Comma).is_none() {
                    break;
                }
                if self.check(&TokenKind::RParen) {
                    break;
                }
            }
        }
        let close = self.expect(&TokenKind::RParen)?;
        Ok(Pattern::Nominal {
            path,
            arguments,
            payload_syntax: true,
            span: Span {
                start,
                end: self.token_end(&close),
            },
        })
    }

    fn parse_parenthesized_pattern(&mut self) -> PatternResult<Pattern> {
        let open = self.expect(&TokenKind::LParen)?;
        if let Some(close) = self.consume(&TokenKind::RParen) {
            return Ok(Pattern::Tuple {
                items: Vec::new(),
                span: Span {
                    start: open.offset,
                    end: self.token_end(&close),
                },
            });
        }

        let first = self.parse_pattern()?;
        if self.consume(&TokenKind::Comma).is_none() {
            let close = self.expect(&TokenKind::RParen)?;
            return Ok(first.with_span(Span {
                start: open.offset,
                end: self.token_end(&close),
            }));
        }

        let mut items = vec![first];
        while !self.check(&TokenKind::RParen) {
            items.push(self.parse_pattern()?);
            if self.consume(&TokenKind::Comma).is_none() {
                break;
            }
        }
        let close = self.expect(&TokenKind::RParen)?;
        Ok(Pattern::Tuple {
            items,
            span: Span {
                start: open.offset,
                end: self.token_end(&close),
            },
        })
    }

    fn parse_list_pattern(&mut self) -> PatternResult<Pattern> {
        let open = self.expect(&TokenKind::LBracket)?;
        let mut items = Vec::new();
        if !self.check(&TokenKind::RBracket) {
            loop {
                if self.check(&TokenKind::DotDot) {
                    items.push(ListItem::Rest(self.parse_rest_pattern()?));
                } else {
                    items.push(ListItem::Pattern(self.parse_pattern()?));
                }
                if self.consume(&TokenKind::Comma).is_none() {
                    break;
                }
                if self.check(&TokenKind::RBracket) {
                    break;
                }
            }
        }
        let close = self.expect(&TokenKind::RBracket)?;

        let rest_indexes = items
            .iter()
            .enumerate()
            .filter_map(|(index, item)| matches!(item, ListItem::Rest(_)).then_some(index))
            .collect::<Vec<_>>();
        if rest_indexes.len() > 1 {
            let ListItem::Rest(second) = &items[rest_indexes[1]] else {
                unreachable!("rest index points to a remainder")
            };
            return Err(PatternFailure::structured(
                MULTIPLE_PATTERN_REMAINDERS,
                second.span,
                None,
            ));
        }

        let mut prefix = Vec::new();
        let mut rest = None;
        let mut suffix = Vec::new();
        for item in items {
            match item {
                ListItem::Rest(value) => rest = Some(value),
                ListItem::Pattern(value) if rest.is_none() => prefix.push(value),
                ListItem::Pattern(value) => suffix.push(value),
            }
        }
        Ok(Pattern::List {
            prefix,
            rest,
            suffix,
            span: Span {
                start: open.offset,
                end: self.token_end(&close),
            },
        })
    }

    fn parse_map_pattern(&mut self) -> PatternResult<Pattern> {
        let open = self.expect(&TokenKind::LBrace)?;
        let mut entries = Vec::new();
        let mut rest = None;
        let mut seen_keys = BTreeSet::new();

        if !self.check(&TokenKind::RBrace) {
            loop {
                if self.check(&TokenKind::DotDot) {
                    if rest.is_some() {
                        let second = self.parse_rest_pattern()?;
                        return Err(PatternFailure::structured(
                            MULTIPLE_PATTERN_REMAINDERS,
                            second.span,
                            None,
                        ));
                    }
                    rest = Some(self.parse_rest_pattern()?);
                } else {
                    if let Some(remainder) = &rest {
                        return Err(PatternFailure::structured(
                            MAP_PATTERN_REST_NOT_LAST,
                            remainder.span,
                            None,
                        ));
                    }
                    let key = self.parse_map_key()?;
                    if !seen_keys.insert(key.identity()) {
                        return Err(PatternFailure::structured(
                            DUPLICATE_MAP_PATTERN_KEY,
                            key.span,
                            Some(key.lexeme.clone()),
                        ));
                    }
                    self.expect(&TokenKind::Colon)?;
                    let pattern = self.parse_pattern()?;
                    entries.push(MapPatternEntry {
                        span: Span {
                            start: key.span.start,
                            end: pattern.span().end,
                        },
                        key,
                        pattern,
                    });
                }
                if self.consume(&TokenKind::Comma).is_none() {
                    break;
                }
                if self.check(&TokenKind::RBrace) {
                    break;
                }
            }
        }
        let close = self.expect(&TokenKind::RBrace)?;
        Ok(Pattern::Map {
            entries,
            rest,
            span: Span {
                start: open.offset,
                end: self.token_end(&close),
            },
        })
    }

    fn parse_map_key(&mut self) -> PatternResult<LiteralPattern> {
        let token = self.peek().clone();
        match &token.kind {
            TokenKind::Name(name) if matches!(name.as_str(), "none" | "true" | "false") => {
                self.advance();
                Ok(named_literal(name, self.token_span(&token)))
            }
            TokenKind::Number(_) | TokenKind::Minus => self.parse_integer_literal(),
            TokenKind::String { .. } => self.parse_string_literal(),
            _ => Err(self.error_at("map pattern keys must be literals", token.offset)),
        }
    }

    fn parse_rest_pattern(&mut self) -> PatternResult<PatternRest> {
        let marker = self.expect(&TokenKind::DotDot)?;
        let capture = match &self.peek().kind {
            TokenKind::Name(name) if is_capture_name(name) => {
                let token = self.advance();
                Some((name_value(&token).to_string(), self.token_end(&token)))
            }
            _ => None,
        };
        Ok(PatternRest {
            capture: capture.as_ref().map(|(name, _)| name.clone()),
            span: Span {
                start: marker.offset,
                end: capture
                    .map(|(_, end)| end)
                    .unwrap_or_else(|| self.token_end(&marker)),
            },
        })
    }

    fn parse_integer_literal(&mut self) -> PatternResult<LiteralPattern> {
        let start_token = self.peek().clone();
        let (start, end, lexeme) = if matches!(start_token.kind, TokenKind::Minus) {
            self.advance();
            let number = self.expect_number("expected an integer immediately after '-'")?;
            if self.token_end(&start_token) != number.offset {
                return Err(self.error_at(
                    "negative pattern literals may not contain whitespace after '-'",
                    start_token.offset,
                ));
            }
            (
                start_token.offset,
                self.token_end(&number),
                self.source[start_token.offset..self.token_end(&number)].to_string(),
            )
        } else {
            let number = self.expect_number("expected an integer literal")?;
            (
                number.offset,
                self.token_end(&number),
                token_text(&number.kind),
            )
        };

        if !is_valid_integer_lexeme(&lexeme) {
            return Err(self.error_at("invalid integer pattern literal", start));
        }
        Ok(LiteralPattern {
            literal_kind: "integer",
            value: LiteralValue::String(lexeme.replace('_', "")),
            lexeme,
            span: Span { start, end },
        })
    }

    fn parse_string_literal(&mut self) -> PatternResult<LiteralPattern> {
        let token = self.advance();
        let TokenKind::String { value, source } = &token.kind else {
            unreachable!("parse_string_literal called for a non-string token")
        };
        // Keep this fenced subset aligned with the Lark producer until a
        // language-owned scalar literal codec replaces both host decoders.
        let quote_offset = source
            .find(['\'', '"'])
            .expect("lexer string source includes a quote");
        let prefix = &source[..quote_offset];
        let bytes_literal = matches!(prefix, "b" | "B");
        if !matches!(prefix, "" | "b" | "B")
            || !has_supported_pattern_string_syntax(source, quote_offset, bytes_literal)
        {
            return Err(self.error_at("unsupported Pattern Surface string spelling", token.offset));
        }

        let (literal_kind, value) = match prefix {
            "" => ("text", LiteralValue::String(value.clone())),
            "b" | "B" if value.is_ascii() => ("bytes", LiteralValue::String(hex_bytes(value))),
            _ => {
                return Err(
                    self.error_at("unsupported Pattern Surface bytes spelling", token.offset)
                )
            }
        };
        Ok(LiteralPattern {
            literal_kind,
            value,
            lexeme: source.clone(),
            span: self.token_span(&token),
        })
    }

    fn check(&self, expected: &TokenKind) -> bool {
        same_variant(&self.peek().kind, expected)
    }

    fn peek_name(&self, expected: &str) -> bool {
        matches!(&self.peek().kind, TokenKind::Name(name) if name == expected)
    }

    fn peek(&self) -> &Token {
        self.tokens
            .get(self.index)
            .expect("Pattern Surface token stream ends with EOF")
    }

    fn advance(&mut self) -> Token {
        let token = self.peek().clone();
        self.index += 1;
        token
    }

    fn consume(&mut self, expected: &TokenKind) -> Option<Token> {
        self.check(expected).then(|| self.advance())
    }

    fn expect(&mut self, expected: &TokenKind) -> PatternResult<Token> {
        if self.check(expected) {
            return Ok(self.advance());
        }
        let actual = self.peek();
        Err(self.error_at(
            format!(
                "expected {}, found {}",
                token_name(expected),
                token_name(&actual.kind)
            ),
            actual.offset,
        ))
    }

    fn expect_name(&mut self, message: &str) -> PatternResult<Token> {
        if matches!(self.peek().kind, TokenKind::Name(_)) {
            return Ok(self.advance());
        }
        Err(self.error_at(message, self.peek().offset))
    }

    fn expect_capture(&mut self, message: &str) -> PatternResult<Token> {
        let token = self.expect_name(message)?;
        if is_capture_name(name_value(&token)) {
            Ok(token)
        } else {
            Err(self.error_at(message, token.offset))
        }
    }

    fn expect_number(&mut self, message: &str) -> PatternResult<Token> {
        if matches!(self.peek().kind, TokenKind::Number(_)) {
            return Ok(self.advance());
        }
        Err(self.error_at(message, self.peek().offset))
    }

    fn token_end(&self, token: &Token) -> usize {
        token.offset + token_text(&token.kind).len()
    }

    fn token_span(&self, token: &Token) -> Span {
        Span {
            start: token.offset,
            end: self.token_end(token),
        }
    }

    fn error_at(&self, _message: impl AsRef<str>, _offset: usize) -> PatternFailure {
        PatternFailure::invalid(self.source)
    }
}

fn named_literal(name: &str, span: Span) -> LiteralPattern {
    let value = match name {
        "none" => LiteralValue::None,
        "true" => LiteralValue::Bool(true),
        "false" => LiteralValue::Bool(false),
        _ => unreachable!("named literals are checked by the parser"),
    };
    LiteralPattern {
        literal_kind: if name == "none" { "none" } else { "boolean" },
        value,
        lexeme: name.to_string(),
        span,
    }
}

fn name_value(token: &Token) -> &str {
    let TokenKind::Name(value) = &token.kind else {
        unreachable!("name_value called for a non-name token")
    };
    value
}

fn is_capture_name(name: &str) -> bool {
    let mut chars = name.chars();
    matches!(chars.next(), Some('a'..='z'))
        && chars.all(|ch| ch.is_ascii_alphanumeric() || ch == '_')
}

fn is_type_name(name: &str) -> bool {
    let mut chars = name.chars();
    matches!(chars.next(), Some('A'..='Z'))
        && chars.all(|ch| ch.is_ascii_alphanumeric() || ch == '_')
}

fn is_name_part(name: &str) -> bool {
    let mut chars = name.chars();
    matches!(chars.next(), Some('a'..='z' | 'A'..='Z'))
        && chars.all(|ch| ch.is_ascii_alphanumeric() || ch == '_')
}

fn is_valid_integer_lexeme(lexeme: &str) -> bool {
    let digits = lexeme.strip_prefix('-').unwrap_or(lexeme);
    if digits == "0" {
        return true;
    }
    let mut groups = digits.split('_');
    let Some(first) = groups.next() else {
        return false;
    };
    matches!(first.chars().next(), Some('1'..='9'))
        && first.chars().all(|ch| ch.is_ascii_digit())
        && groups.all(|group| !group.is_empty() && group.chars().all(|ch| ch.is_ascii_digit()))
}

fn has_supported_pattern_string_syntax(
    source: &str,
    quote_offset: usize,
    bytes_literal: bool,
) -> bool {
    let quoted = &source[quote_offset..];
    if quoted.len() < 2 || !quoted.starts_with('"') || !quoted.ends_with('"') {
        return false;
    }
    let content = &quoted[1..quoted.len() - 1];
    let mut chars = content.chars();
    while let Some(ch) = chars.next() {
        if ch == '\\' {
            if !matches!(chars.next(), Some('"' | '\\' | 'n' | 'r' | 't')) {
                return false;
            }
        } else if ch.is_control() || (!bytes_literal && matches!(ch, '{' | '}')) {
            return false;
        }
    }
    true
}

fn hex_bytes(value: &str) -> String {
    value
        .as_bytes()
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect()
}

fn binding_map(root: &Pattern) -> PatternResult<BTreeMap<String, Span>> {
    match root {
        Pattern::Capture { name, span } => {
            let mut bindings = BTreeMap::new();
            merge_capture(&mut bindings, name, *span)?;
            Ok(bindings)
        }
        Pattern::Wildcard { .. } | Pattern::Literal(_) => Ok(BTreeMap::new()),
        Pattern::Or { alternatives, span } => {
            let maps = alternatives
                .iter()
                .map(binding_map)
                .collect::<PatternResult<Vec<_>>>()?;
            let expected = maps.first().expect("or-pattern has alternatives");
            if maps
                .iter()
                .skip(1)
                .any(|item| item.keys().ne(expected.keys()))
            {
                return Err(PatternFailure::structured(
                    ALTERNATIVE_BINDING_MISMATCH,
                    *span,
                    None,
                ));
            }
            Ok(expected.clone())
        }
        Pattern::As {
            pattern,
            capture,
            capture_span,
            ..
        } => {
            let mut bindings = binding_map(pattern)?;
            merge_capture(&mut bindings, capture, *capture_span)?;
            Ok(bindings)
        }
        Pattern::Nominal { arguments, .. } => merge_child_bindings(arguments.iter()),
        Pattern::Tuple { items, .. } => merge_child_bindings(items.iter()),
        Pattern::List {
            prefix,
            rest,
            suffix,
            ..
        } => {
            let mut bindings = merge_child_bindings(prefix.iter().chain(suffix))?;
            merge_rest_capture(&mut bindings, rest)?;
            Ok(bindings)
        }
        Pattern::Map { entries, rest, .. } => {
            let mut bindings = merge_child_bindings(entries.iter().map(|entry| &entry.pattern))?;
            merge_rest_capture(&mut bindings, rest)?;
            Ok(bindings)
        }
    }
}

fn merge_child_bindings<'a>(
    children: impl IntoIterator<Item = &'a Pattern>,
) -> PatternResult<BTreeMap<String, Span>> {
    let mut bindings = BTreeMap::new();
    for child in children {
        for (name, span) in binding_map(child)? {
            merge_capture(&mut bindings, &name, span)?;
        }
    }
    Ok(bindings)
}

fn merge_rest_capture(
    bindings: &mut BTreeMap<String, Span>,
    rest: &Option<PatternRest>,
) -> PatternResult<()> {
    if let Some(PatternRest {
        capture: Some(name),
        span,
    }) = rest
    {
        merge_capture(bindings, name, *span)?;
    }
    Ok(())
}

fn merge_capture(
    bindings: &mut BTreeMap<String, Span>,
    name: &str,
    span: Span,
) -> PatternResult<()> {
    if RESERVED_PATTERN_NAMES.contains(&name) {
        return Err(PatternFailure::structured(
            INVALID_PATTERN_SYNTAX,
            span,
            None,
        ));
    }
    if bindings.insert(name.to_string(), span).is_some() {
        return Err(PatternFailure::structured(
            DUPLICATE_PATTERN_CAPTURE,
            span,
            Some(name.to_string()),
        ));
    }
    Ok(())
}

fn document_json(source: &str, result: PatternResult<Pattern>) -> String {
    let (root, diagnostics) = match result {
        Ok(root) => (root.to_json(), json_array(Vec::<String>::new())),
        Err(error) => (json_null(), json_array([error.to_json()])),
    };
    json_object(vec![
        ("schema", json_string(PATTERN_SURFACE_SCHEMA)),
        ("version", PATTERN_SURFACE_VERSION.to_string()),
        ("source", json_string(source)),
        ("root", root),
        ("diagnostics", diagnostics),
    ])
}

pub fn parse_pattern_to_json(source: &str) -> Result<String, String> {
    let result = match lex(source) {
        Ok(tokens) => {
            let tokens = tokens
                .into_iter()
                .filter(|token| {
                    !matches!(
                        token.kind,
                        TokenKind::Newline | TokenKind::Indent | TokenKind::Dedent
                    )
                })
                .collect();
            PatternParser::new(source, tokens)
                .parse_document()
                .and_then(|root| {
                    binding_map(&root)?;
                    Ok(root)
                })
        }
        Err(_) => Err(PatternFailure::invalid(source)),
    };
    Ok(document_json(source, result))
}

#[cfg(test)]
mod tests {
    use super::parse_pattern_to_json;

    #[test]
    fn emits_lossless_pattern_surface_payload() {
        let source = "(Command.Read(path) | Command.Write(path)) as request";
        let payload = parse_pattern_to_json(source).expect("pattern should parse");

        assert!(payload.contains("\"schema\":\"nomi.pattern-surface\""));
        assert!(payload.contains("\"kind\":\"AsPattern\""));
        assert!(payload.contains("\"kind\":\"OrPattern\""));
        assert!(payload.contains("\"diagnostics\":[]"));
        assert!(payload.contains(&format!("\"end\":{}", source.len())));
    }

    #[test]
    fn spans_are_utf8_byte_offsets() {
        let source = "\"hé\"";
        let payload = parse_pattern_to_json(source).expect("pattern should parse");

        assert!(payload.contains("\"span\":{\"start\":0,\"end\":5}"));
    }

    #[test]
    fn reports_ambiguous_or_effectful_shapes() {
        for source in ["1.5", "extract(value)", "[..left, ..right]", "{.., 1: x}"] {
            let payload = parse_pattern_to_json(source).expect("diagnostic payload");
            assert!(
                payload.contains("\"root\":null"),
                "expected rejection for {source}"
            );
        }
    }
}
