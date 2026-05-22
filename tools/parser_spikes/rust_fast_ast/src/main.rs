use std::env;
use std::fmt;
use std::fs;
use std::process;

#[derive(Debug, Clone, PartialEq)]
enum TokenKind {
    Name(String),
    Number(String),
    String(String),
    Plus,
    Minus,
    Star,
    Slash,
    DoubleStar,
    Equal,
    FatArrow,
    LParen,
    RParen,
    Comma,
    Newline,
    Semi,
    Eof,
}

#[derive(Debug, Clone, PartialEq)]
struct Token {
    kind: TokenKind,
    offset: usize,
}

#[derive(Debug)]
struct ParseError {
    message: String,
    offset: usize,
}

impl ParseError {
    fn new(message: impl Into<String>, offset: usize) -> Self {
        Self {
            message: message.into(),
            offset,
        }
    }
}

impl fmt::Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} at byte {}", self.message, self.offset)
    }
}

#[derive(Debug, Clone)]
enum Stmt {
    Assign { target: String, value: Expr },
    Expr(Expr),
    FunctionDef {
        name: String,
        params: Vec<String>,
        body: Expr,
    },
}

#[derive(Debug, Clone)]
enum Expr {
    Name(String),
    Number(String),
    String(String),
    Call { func: Box<Expr>, args: Vec<Expr> },
    BinOp {
        left: Box<Expr>,
        op: BinOp,
        right: Box<Expr>,
    },
    FunctionExpr { params: Vec<String>, body: Box<Expr> },
}

#[derive(Debug, Clone, Copy)]
enum BinOp {
    Add,
    Sub,
    Mult,
    Div,
    Pow,
}

fn main() {
    if let Err(error) = run() {
        eprintln!("{error}");
        process::exit(1);
    }
}

fn run() -> Result<(), String> {
    let mut args = env::args().skip(1);
    let command = args.next().ok_or("usage: nomi-rust-fast-ast ast-json <path>")?;
    let path = args.next().ok_or("usage: nomi-rust-fast-ast ast-json <path>")?;
    if command != "ast-json" {
        return Err(format!("unknown command: {command}"));
    }
    if args.next().is_some() {
        return Err("too many arguments".to_string());
    }
    let source = fs::read_to_string(path).map_err(|error| error.to_string())?;
    let tokens = lex(&source).map_err(|error| error.to_string())?;
    let module = Parser::new(tokens).parse_module().map_err(|error| error.to_string())?;
    println!("{}", module_json(&module));
    Ok(())
}

fn lex(source: &str) -> Result<Vec<Token>, ParseError> {
    let mut tokens = Vec::new();
    let mut offset = 0;
    while offset < source.len() {
        let ch = source[offset..].chars().next().expect("valid char boundary");
        match ch {
            ' ' | '\t' | '\r' | '\x0c' => {
                offset += ch.len_utf8();
            }
            '\n' => {
                tokens.push(Token { kind: TokenKind::Newline, offset });
                offset += ch.len_utf8();
            }
            '#' => {
                offset += ch.len_utf8();
                while offset < source.len() {
                    let next = source[offset..].chars().next().expect("valid char boundary");
                    if next == '\n' {
                        break;
                    }
                    offset += next.len_utf8();
                }
            }
            '+' => {
                tokens.push(Token { kind: TokenKind::Plus, offset });
                offset += ch.len_utf8();
            }
            '-' => {
                tokens.push(Token { kind: TokenKind::Minus, offset });
                offset += ch.len_utf8();
            }
            '*' => {
                let next_offset = offset + ch.len_utf8();
                if source[next_offset..].starts_with('*') {
                    tokens.push(Token { kind: TokenKind::DoubleStar, offset });
                    offset = next_offset + 1;
                } else {
                    tokens.push(Token { kind: TokenKind::Star, offset });
                    offset = next_offset;
                }
            }
            '/' => {
                tokens.push(Token { kind: TokenKind::Slash, offset });
                offset += ch.len_utf8();
            }
            '=' => {
                let next_offset = offset + ch.len_utf8();
                if source[next_offset..].starts_with('>') {
                    tokens.push(Token { kind: TokenKind::FatArrow, offset });
                    offset = next_offset + 1;
                } else {
                    tokens.push(Token { kind: TokenKind::Equal, offset });
                    offset = next_offset;
                }
            }
            '(' => {
                tokens.push(Token { kind: TokenKind::LParen, offset });
                offset += ch.len_utf8();
            }
            ')' => {
                tokens.push(Token { kind: TokenKind::RParen, offset });
                offset += ch.len_utf8();
            }
            ',' => {
                tokens.push(Token { kind: TokenKind::Comma, offset });
                offset += ch.len_utf8();
            }
            ';' => {
                tokens.push(Token { kind: TokenKind::Semi, offset });
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
    tokens.push(Token { kind: TokenKind::Eof, offset: source.len() });
    Ok(tokens)
}

fn read_string(source: &str, start: usize, quote: char) -> Result<(String, usize), ParseError> {
    let mut escaped = false;
    let mut value = String::new();
    for (offset, ch) in source[start + quote.len_utf8()..].char_indices() {
        let absolute = start + quote.len_utf8() + offset;
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
        } else if ch == '\\' {
            escaped = true;
        } else if ch == quote {
            return Ok((value, absolute + ch.len_utf8()));
        } else if ch == '\n' {
            return Err(ParseError::new("unterminated string", absolute));
        } else {
            value.push(ch);
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
        } else if ch == '.' && !dot_seen {
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

struct Parser {
    tokens: Vec<Token>,
    cursor: usize,
}

impl Parser {
    fn new(tokens: Vec<Token>) -> Self {
        Self { tokens, cursor: 0 }
    }

    fn parse_module(&mut self) -> Result<Vec<Stmt>, ParseError> {
        let mut body = Vec::new();
        self.skip_separators();
        while !self.at_eof() {
            body.push(self.parse_stmt()?);
            self.expect_stmt_end()?;
            self.skip_separators();
        }
        Ok(body)
    }

    fn parse_stmt(&mut self) -> Result<Stmt, ParseError> {
        if let Some(stmt) = self.try_function_equation()? {
            return Ok(stmt);
        }
        if let Some(stmt) = self.try_assignment()? {
            return Ok(stmt);
        }
        Ok(Stmt::Expr(self.parse_expr(0)?))
    }

    fn try_function_equation(&mut self) -> Result<Option<Stmt>, ParseError> {
        let mark = self.cursor;
        let name = match self.advance().kind.clone() {
            TokenKind::Name(value) => value,
            _ => {
                self.cursor = mark;
                return Ok(None);
            }
        };
        if !self.eat(&TokenKind::LParen) {
            self.cursor = mark;
            return Ok(None);
        }
        let Some(params) = self.try_param_list() else {
            self.cursor = mark;
            return Ok(None);
        };
        if !self.eat(&TokenKind::RParen) || !self.eat(&TokenKind::Equal) {
            self.cursor = mark;
            return Ok(None);
        }
        let body = self.parse_expr(0)?;
        Ok(Some(Stmt::FunctionDef { name, params, body }))
    }

    fn try_assignment(&mut self) -> Result<Option<Stmt>, ParseError> {
        let mark = self.cursor;
        let target = match self.advance().kind.clone() {
            TokenKind::Name(value) => value,
            _ => {
                self.cursor = mark;
                return Ok(None);
            }
        };
        if !self.eat(&TokenKind::Equal) {
            self.cursor = mark;
            return Ok(None);
        }
        let value = self.parse_arrow_or_expr()?;
        Ok(Some(Stmt::Assign { target, value }))
    }

    fn parse_arrow_or_expr(&mut self) -> Result<Expr, ParseError> {
        let mark = self.cursor;
        if let Some(params) = self.try_arrow_params()? {
            if self.eat(&TokenKind::FatArrow) {
                let body = self.parse_expr(0)?;
                return Ok(Expr::FunctionExpr {
                    params,
                    body: Box::new(body),
                });
            }
        }
        self.cursor = mark;
        self.parse_expr(0)
    }

    fn try_arrow_params(&mut self) -> Result<Option<Vec<String>>, ParseError> {
        match self.peek().kind.clone() {
            TokenKind::Name(name) => {
                self.advance();
                Ok(Some(vec![name]))
            }
            TokenKind::LParen => {
                let mark = self.cursor;
                self.advance();
                let Some(params) = self.try_param_list() else {
                    self.cursor = mark;
                    return Ok(None);
                };
                if !self.eat(&TokenKind::RParen) {
                    self.cursor = mark;
                    return Ok(None);
                }
                Ok(Some(params))
            }
            _ => Ok(None),
        }
    }

    fn try_param_list(&mut self) -> Option<Vec<String>> {
        let mark = self.cursor;
        let mut params = Vec::new();
        if matches!(self.peek().kind, TokenKind::RParen) {
            return Some(params);
        }
        loop {
            let token = self.advance().clone();
            match token.kind {
                TokenKind::Name(name) => params.push(name),
                _ => {
                    self.cursor = mark;
                    return None;
                }
            }
            if !self.eat(&TokenKind::Comma) {
                break;
            }
        }
        Some(params)
    }

    fn parse_expr(&mut self, min_bp: u8) -> Result<Expr, ParseError> {
        let mut left = self.parse_postfix()?;
        loop {
            let Some((op, left_bp, right_bp)) = self.current_binop() else {
                break;
            };
            if left_bp < min_bp {
                break;
            }
            self.advance();
            let right = self.parse_expr(right_bp)?;
            left = Expr::BinOp {
                left: Box::new(left),
                op,
                right: Box::new(right),
            };
        }
        Ok(left)
    }

    fn parse_postfix(&mut self) -> Result<Expr, ParseError> {
        let mut expr = self.parse_primary()?;
        loop {
            if !self.eat(&TokenKind::LParen) {
                break;
            }
            let mut args = Vec::new();
            if !self.eat(&TokenKind::RParen) {
                loop {
                    args.push(self.parse_expr(0)?);
                    if self.eat(&TokenKind::Comma) {
                        continue;
                    }
                    self.expect(&TokenKind::RParen)?;
                    break;
                }
            }
            expr = Expr::Call {
                func: Box::new(expr),
                args,
            };
        }
        Ok(expr)
    }

    fn parse_primary(&mut self) -> Result<Expr, ParseError> {
        let token = self.advance().clone();
        match token.kind {
            TokenKind::Name(value) => Ok(Expr::Name(value)),
            TokenKind::Number(value) => Ok(Expr::Number(value)),
            TokenKind::String(value) => Ok(Expr::String(value)),
            TokenKind::LParen => {
                let expr = self.parse_expr(0)?;
                self.expect(&TokenKind::RParen)?;
                Ok(expr)
            }
            TokenKind::Minus => {
                let right = self.parse_expr(13)?;
                Ok(Expr::BinOp {
                    left: Box::new(Expr::Number("0".to_string())),
                    op: BinOp::Sub,
                    right: Box::new(right),
                })
            }
            _ => Err(ParseError::new("expected expression", token.offset)),
        }
    }

    fn current_binop(&self) -> Option<(BinOp, u8, u8)> {
        match self.peek().kind {
            TokenKind::Plus => Some((BinOp::Add, 10, 11)),
            TokenKind::Minus => Some((BinOp::Sub, 10, 11)),
            TokenKind::Star => Some((BinOp::Mult, 12, 13)),
            TokenKind::Slash => Some((BinOp::Div, 12, 13)),
            TokenKind::DoubleStar => Some((BinOp::Pow, 15, 14)),
            _ => None,
        }
    }

    fn expect_stmt_end(&mut self) -> Result<(), ParseError> {
        if matches!(self.peek().kind, TokenKind::Newline | TokenKind::Semi | TokenKind::Eof) {
            Ok(())
        } else {
            Err(ParseError::new("expected statement end", self.peek().offset))
        }
    }

    fn skip_separators(&mut self) {
        while matches!(self.peek().kind, TokenKind::Newline | TokenKind::Semi) {
            self.advance();
        }
    }

    fn expect(&mut self, expected: &TokenKind) -> Result<(), ParseError> {
        if self.eat(expected) {
            Ok(())
        } else {
            Err(ParseError::new(
                format!("expected {}", token_name(expected)),
                self.peek().offset,
            ))
        }
    }

    fn eat(&mut self, expected: &TokenKind) -> bool {
        if same_variant(&self.peek().kind, expected) {
            self.advance();
            true
        } else {
            false
        }
    }

    fn advance(&mut self) -> &Token {
        let token = &self.tokens[self.cursor];
        if !matches!(token.kind, TokenKind::Eof) {
            self.cursor += 1;
        }
        token
    }

    fn peek(&self) -> &Token {
        &self.tokens[self.cursor]
    }

    fn at_eof(&self) -> bool {
        matches!(self.peek().kind, TokenKind::Eof)
    }
}

fn same_variant(left: &TokenKind, right: &TokenKind) -> bool {
    std::mem::discriminant(left) == std::mem::discriminant(right)
}

fn token_name(kind: &TokenKind) -> &'static str {
    match kind {
        TokenKind::Name(_) => "name",
        TokenKind::Number(_) => "number",
        TokenKind::String(_) => "string",
        TokenKind::Plus => "+",
        TokenKind::Minus => "-",
        TokenKind::Star => "*",
        TokenKind::Slash => "/",
        TokenKind::DoubleStar => "**",
        TokenKind::Equal => "=",
        TokenKind::FatArrow => "=>",
        TokenKind::LParen => "(",
        TokenKind::RParen => ")",
        TokenKind::Comma => ",",
        TokenKind::Newline => "newline",
        TokenKind::Semi => ";",
        TokenKind::Eof => "end of file",
    }
}

fn module_json(body: &[Stmt]) -> String {
    let statements = body.iter().map(stmt_json).collect::<Vec<_>>().join(",");
    format!("{{\"type\":\"Module\",\"body\":[{statements}]}}")
}

fn stmt_json(stmt: &Stmt) -> String {
    match stmt {
        Stmt::Assign { target, value } => format!(
            "{{\"type\":\"Assign\",\"target\":{},\"value\":{}}}",
            json_string(target),
            expr_json(value),
        ),
        Stmt::Expr(value) => format!(
            "{{\"type\":\"Expr\",\"value\":{}}}",
            expr_json(value),
        ),
        Stmt::FunctionDef { name, params, body } => function_json(Some(name), params, body),
    }
}

fn expr_json(expr: &Expr) -> String {
    match expr {
        Expr::Name(value) => format!("{{\"type\":\"Name\",\"id\":{}}}", json_string(value)),
        Expr::Number(value) => format!("{{\"type\":\"Number\",\"value\":{}}}", json_string(value)),
        Expr::String(value) => format!("{{\"type\":\"String\",\"value\":{}}}", json_string(value)),
        Expr::Call { func, args } => {
            let args = args.iter().map(expr_json).collect::<Vec<_>>().join(",");
            format!(
                "{{\"type\":\"Call\",\"func\":{},\"args\":[{}]}}",
                expr_json(func),
                args,
            )
        }
        Expr::BinOp { left, op, right } => format!(
            "{{\"type\":\"BinOp\",\"left\":{},\"op\":{},\"right\":{}}}",
            expr_json(left),
            json_string(op_name(*op)),
            expr_json(right),
        ),
        Expr::FunctionExpr { params, body } => function_json(None, params, body),
    }
}

fn function_json(name: Option<&String>, params: &[String], body: &Expr) -> String {
    let name = match name {
        Some(value) => json_string(value),
        None => "null".to_string(),
    };
    let params = params.iter().map(|param| json_string(param)).collect::<Vec<_>>().join(",");
    format!(
        "{{\"type\":\"FunctionDef\",\"name\":{},\"params\":[{}],\"body\":{}}}",
        name,
        params,
        expr_json(body),
    )
}

fn op_name(op: BinOp) -> &'static str {
    match op {
        BinOp::Add => "Add",
        BinOp::Sub => "Sub",
        BinOp::Mult => "Mult",
        BinOp::Div => "Div",
        BinOp::Pow => "Pow",
    }
}

fn json_string(value: &str) -> String {
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
