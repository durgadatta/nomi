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
    DoubleSlash,
    Percent,
    At,
    Equal,
    PlusEqual,
    MinusEqual,
    StarEqual,
    SlashEqual,
    FatArrow,
    Arrow,
    Dollar,
    Pipe,
    PipeGreater,
    Question,
    QuestionQuestion,
    QuestionDot,
    Less,
    Greater,
    LessEqual,
    GreaterEqual,
    DoubleEqual,
    NotEqual,
    LParen,
    RParen,
    LBracket,
    RBracket,
    LBrace,
    RBrace,
    Dot,
    DotDot,
    DotDotLess,
    Colon,
    Comma,
    Newline,
    Indent,
    Dedent,
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
    Assign {
        target: String,
        value: Expr,
    },
    AugAssign {
        target: String,
        op: String,
        value: Expr,
    },
    Expr(Expr),
    FunctionDef {
        name: String,
        params: Vec<String>,
        body: Expr,
    },
    Return(Option<Expr>),
    Yield(Option<Expr>),
    Raise(Option<Expr>),
    Simple(String),
    Suite {
        kind: String,
        head: String,
        body: Vec<Stmt>,
        clauses: Vec<Clause>,
    },
}

#[derive(Debug, Clone)]
struct Clause {
    kind: String,
    head: String,
    body: Vec<Stmt>,
}

#[derive(Debug, Clone)]
enum Expr {
    Name(String),
    Number(String),
    String(String),
    Constant(String),
    List(Vec<Expr>),
    Tuple(Vec<Expr>),
    Dict,
    Attribute {
        value: Box<Expr>,
        attr: String,
    },
    Subscript {
        value: Box<Expr>,
        slice: Box<Expr>,
    },
    Call {
        func: Box<Expr>,
        args: Vec<Expr>,
    },
    BinOp {
        left: Box<Expr>,
        op: BinOp,
        right: Box<Expr>,
    },
    Compare {
        left: Box<Expr>,
        op: CmpOp,
        right: Box<Expr>,
    },
    BoolOp {
        left: Box<Expr>,
        op: BoolOp,
        right: Box<Expr>,
    },
    UnaryOp {
        op: UnaryOp,
        value: Box<Expr>,
    },
    IfExp {
        body: Box<Expr>,
        test: Box<Expr>,
        orelse: Box<Expr>,
    },
    FunctionExpr {
        params: Vec<String>,
        body: Box<Expr>,
    },
    Raw(String),
}

#[derive(Debug, Clone, Copy)]
enum BinOp {
    Add,
    Sub,
    Mult,
    Div,
    FloorDiv,
    Mod,
    MatMult,
    Pow,
}

#[derive(Debug, Clone, Copy)]
enum CmpOp {
    Lt,
    LtE,
    Gt,
    GtE,
    Eq,
    NotEq,
}

#[derive(Debug, Clone, Copy)]
enum BoolOp {
    And,
    Or,
}

#[derive(Debug, Clone, Copy)]
enum UnaryOp {
    UAdd,
    Not,
}

#[derive(Debug, Clone, Copy)]
enum InfixOp {
    Bin(BinOp),
    Cmp(CmpOp),
    Bool(BoolOp),
}

fn main() {
    if let Err(error) = run() {
        eprintln!("{error}");
        process::exit(1);
    }
}

fn run() -> Result<(), String> {
    let mut args = env::args().skip(1);
    let command = args
        .next()
        .ok_or("usage: nomi-rust-fast-ast ast-json <path>")?;
    let path = args
        .next()
        .ok_or("usage: nomi-rust-fast-ast ast-json <path>")?;
    if command != "ast-json" {
        return Err(format!("unknown command: {command}"));
    }
    if args.next().is_some() {
        return Err("too many arguments".to_string());
    }
    let source = fs::read_to_string(path).map_err(|error| error.to_string())?;
    let tokens = lex(&source).map_err(|error| error.to_string())?;
    let module = Parser::new(tokens)
        .parse_module()
        .map_err(|error| error.to_string())?;
    println!("{}", module_json(&module));
    Ok(())
}

fn lex(source: &str) -> Result<Vec<Token>, ParseError> {
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
            '\n' => return (indent, offset, false),
            '#' => return (indent, offset, false),
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

struct Parser {
    tokens: Vec<Token>,
    cursor: usize,
    suite_closed: bool,
}

impl Parser {
    fn new(tokens: Vec<Token>) -> Self {
        Self {
            tokens,
            cursor: 0,
            suite_closed: false,
        }
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
        if self.is_keyword("func") {
            return self.parse_func_stmt();
        }
        if self.is_keyword("for") {
            return self.parse_head_suite("For");
        }
        if self.is_keyword("if") {
            return self.parse_head_suite("If");
        }
        if self.is_keyword("while") {
            return self.parse_head_suite("While");
        }
        if self.is_keyword("unless") {
            return self.parse_head_suite("Unless");
        }
        if self.is_keyword("match") {
            return self.parse_head_suite("Match");
        }
        if self.is_keyword("case") {
            return self.parse_head_suite("Case");
        }
        if self.is_keyword("guard") {
            return self.parse_head_suite("Guard");
        }
        if self.is_keyword("try") {
            return self.parse_try_stmt();
        }
        if self.is_keyword("defer") {
            self.advance();
            let value = self.collect_raw_until_line_end();
            return Ok(Stmt::Simple(format!("defer {value}").trim().to_string()));
        }
        if self.is_keyword("return") {
            self.advance();
            if self.is_keyword("match") {
                let value_start = self.cursor;
                self.advance();
                let head = self.collect_head_until_colon();
                if self.colon_starts_indented_suite() {
                    let body = self.parse_suite_from_current_colon()?;
                    return Ok(Stmt::Suite {
                        kind: "ReturnMatch".to_string(),
                        head,
                        body,
                        clauses: Vec::new(),
                    });
                }
                self.cursor = value_start;
                return Ok(Stmt::Return(Some(Expr::Raw(
                    self.collect_raw_until_line_end(),
                ))));
            }
            return Ok(Stmt::Return(self.parse_optional_expr()?));
        }
        if self.is_keyword("yield") {
            self.advance();
            return Ok(Stmt::Yield(self.parse_optional_expr()?));
        }
        if self.is_keyword("raise") {
            self.advance();
            return Ok(Stmt::Raise(self.parse_optional_expr()?));
        }
        if self.is_keyword("pass") || self.is_keyword("break") || self.is_keyword("continue") {
            let name = self.advance_name()?;
            return Ok(Stmt::Simple(name));
        }
        if let Some(stmt) = self.try_function_equation()? {
            return Ok(stmt);
        }
        if let Some(stmt) = self.try_assignment_like()? {
            return Ok(stmt);
        }
        if self.is_keyword("data") {
            return self.parse_head_suite("Data");
        }
        let mark = self.cursor;
        let expr = match self.parse_arrow_or_expr() {
            Ok(expr) => {
                if self.at_stmt_end()
                    || matches!(self.peek().kind, TokenKind::Colon | TokenKind::Arrow)
                {
                    expr
                } else {
                    self.cursor = mark;
                    Expr::Raw(self.collect_raw_until_line_end())
                }
            }
            Err(_) => {
                self.cursor = mark;
                Expr::Raw(self.collect_raw_until_line_end())
            }
        };
        if self.eat(&TokenKind::Arrow) {
            let params = self.collect_head_until_colon();
            let body = self.parse_suite_from_current_colon()?;
            return Ok(Stmt::Suite {
                kind: "BlockCall".to_string(),
                head: format!("{} -> {}", expr.brief(), params),
                body,
                clauses: Vec::new(),
            });
        }
        if matches!(self.peek().kind, TokenKind::Colon) {
            let body = self.parse_suite_from_current_colon()?;
            return Ok(Stmt::Suite {
                kind: "BlockCall".to_string(),
                head: expr.brief(),
                body,
                clauses: Vec::new(),
            });
        }
        Ok(Stmt::Expr(expr))
    }

    fn parse_func_stmt(&mut self) -> Result<Stmt, ParseError> {
        self.expect_keyword("func")?;
        let name = self.advance_name()?;
        self.expect(&TokenKind::LParen)?;
        let params = self.collect_until_matching(TokenKind::RParen)?;
        self.expect(&TokenKind::RParen)?;
        let body = self.parse_suite_from_current_colon()?;
        Ok(Stmt::Suite {
            kind: "Func".to_string(),
            head: format!("{name}({params})"),
            body,
            clauses: Vec::new(),
        })
    }

    fn parse_head_suite(&mut self, kind: &str) -> Result<Stmt, ParseError> {
        self.advance();
        let head = self.collect_head_until_colon();
        let body = self.parse_suite_from_current_colon()?;
        Ok(Stmt::Suite {
            kind: kind.to_string(),
            head,
            body,
            clauses: Vec::new(),
        })
    }

    fn parse_try_stmt(&mut self) -> Result<Stmt, ParseError> {
        self.expect_keyword("try")?;
        let body = self.parse_suite_from_current_colon()?;
        let mut clauses = Vec::new();
        loop {
            self.skip_separators();
            if !self.is_keyword("except") {
                break;
            }
            self.advance();
            let head = self.collect_head_until_colon();
            let clause_body = self.parse_suite_from_current_colon()?;
            clauses.push(Clause {
                kind: "Except".to_string(),
                head,
                body: clause_body,
            });
        }
        Ok(Stmt::Suite {
            kind: "Try".to_string(),
            head: String::new(),
            body,
            clauses,
        })
    }

    fn parse_suite_from_current_colon(&mut self) -> Result<Vec<Stmt>, ParseError> {
        self.expect(&TokenKind::Colon)?;
        if self.eat(&TokenKind::Newline) {
            self.skip_separators();
            self.expect(&TokenKind::Indent)?;
            let mut body = Vec::new();
            self.skip_separators();
            while !matches!(self.peek().kind, TokenKind::Dedent | TokenKind::Eof) {
                body.push(self.parse_stmt()?);
                self.expect_stmt_end()?;
                self.skip_separators();
            }
            self.expect(&TokenKind::Dedent)?;
            self.suite_closed = true;
            Ok(body)
        } else {
            let stmt = self.parse_stmt()?;
            Ok(vec![stmt])
        }
    }

    fn try_function_equation(&mut self) -> Result<Option<Stmt>, ParseError> {
        let mark = self.cursor;
        let name = match self.advance().kind {
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

    fn try_assignment_like(&mut self) -> Result<Option<Stmt>, ParseError> {
        let Some((op_index, op)) = self.find_assignment_operator() else {
            return Ok(None);
        };
        let target = self.token_text_range(self.cursor, op_index);
        if target.is_empty() {
            return Ok(None);
        }
        self.cursor = op_index + 1;
        if op == "=" && self.is_keyword("match") {
            let value_start = self.cursor;
            self.advance();
            let head = self.collect_head_until_colon();
            if self.colon_starts_indented_suite() {
                let body = self.parse_suite_from_current_colon()?;
                return Ok(Some(Stmt::Suite {
                    kind: "MatchAssign".to_string(),
                    head: format!("{target} = match {head}"),
                    body,
                    clauses: Vec::new(),
                }));
            }
            self.cursor = value_start;
        }
        let value = if op == "=" {
            self.parse_assignment_value()
        } else {
            self.parse_assignment_value()
        };
        if op == "=" && self.is_keyword("where") {
            self.advance();
            let body = self.parse_suite_from_current_colon()?;
            return Ok(Some(Stmt::Suite {
                kind: "WhereAssign".to_string(),
                head: format!("{target} = {}", value.brief()),
                body,
                clauses: Vec::new(),
            }));
        }
        if op == "=" {
            Ok(Some(Stmt::Assign { target, value }))
        } else {
            Ok(Some(Stmt::AugAssign {
                target,
                op: op.to_string(),
                value,
            }))
        }
    }

    fn parse_assignment_value(&mut self) -> Expr {
        let mark = self.cursor;
        match self.parse_arrow_or_expr() {
            Ok(value) if self.at_stmt_end() || self.is_keyword("where") => value,
            Ok(_) | Err(_) => {
                self.cursor = mark;
                Expr::Raw(self.collect_raw_until_line_end())
            }
        }
    }

    fn find_assignment_operator(&self) -> Option<(usize, &'static str)> {
        let mut depth = 0isize;
        let mut index = self.cursor;
        while index < self.tokens.len() {
            let token = &self.tokens[index];
            match token.kind {
                TokenKind::LParen | TokenKind::LBracket | TokenKind::LBrace => depth += 1,
                TokenKind::RParen | TokenKind::RBracket | TokenKind::RBrace => depth -= 1,
                TokenKind::Newline
                | TokenKind::Semi
                | TokenKind::Indent
                | TokenKind::Dedent
                | TokenKind::Eof
                    if depth == 0 =>
                {
                    return None;
                }
                TokenKind::Equal if depth == 0 => return Some((index, "=")),
                TokenKind::PlusEqual if depth == 0 => return Some((index, "+=")),
                TokenKind::MinusEqual if depth == 0 => return Some((index, "-=")),
                TokenKind::StarEqual if depth == 0 => return Some((index, "*=")),
                TokenKind::SlashEqual if depth == 0 => return Some((index, "/=")),
                _ => {}
            }
            index += 1;
        }
        None
    }

    fn parse_optional_expr(&mut self) -> Result<Option<Expr>, ParseError> {
        if self.at_stmt_end() {
            Ok(None)
        } else {
            Ok(Some(self.parse_expr(0)?))
        }
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
            let token = self.advance();
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
            if min_bp <= 3 && self.is_keyword("if") {
                self.advance();
                let test = self.parse_expr(0)?;
                self.expect_keyword("else")?;
                let orelse = self.parse_expr(0)?;
                left = Expr::IfExp {
                    body: Box::new(left),
                    test: Box::new(test),
                    orelse: Box::new(orelse),
                };
                continue;
            }
            let Some((op, left_bp, right_bp)) = self.current_infix() else {
                break;
            };
            if left_bp < min_bp {
                break;
            }
            self.advance();
            let right = self.parse_expr(right_bp)?;
            left = match op {
                InfixOp::Bin(bin_op) => Expr::BinOp {
                    left: Box::new(left),
                    op: bin_op,
                    right: Box::new(right),
                },
                InfixOp::Cmp(cmp_op) => Expr::Compare {
                    left: Box::new(left),
                    op: cmp_op,
                    right: Box::new(right),
                },
                InfixOp::Bool(bool_op) => Expr::BoolOp {
                    left: Box::new(left),
                    op: bool_op,
                    right: Box::new(right),
                },
            };
        }
        Ok(left)
    }

    fn parse_postfix(&mut self) -> Result<Expr, ParseError> {
        let mut expr = self.parse_primary()?;
        loop {
            if self.eat(&TokenKind::LParen) {
                let mut args = Vec::new();
                if !self.eat(&TokenKind::RParen) {
                    loop {
                        args.push(self.parse_arrow_or_expr()?);
                        if self.eat(&TokenKind::Comma) {
                            if matches!(self.peek().kind, TokenKind::RParen) {
                                self.advance();
                                break;
                            }
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
            } else if self.eat(&TokenKind::Dot) {
                let attr = self.advance_name()?;
                expr = Expr::Attribute {
                    value: Box::new(expr),
                    attr,
                };
            } else if self.eat(&TokenKind::LBracket) {
                let slice = if self.eat(&TokenKind::RBracket) {
                    Expr::Raw(String::new())
                } else {
                    let value = self.parse_expr(0)?;
                    self.expect(&TokenKind::RBracket)?;
                    value
                };
                expr = Expr::Subscript {
                    value: Box::new(expr),
                    slice: Box::new(slice),
                };
            } else {
                break;
            }
        }
        Ok(expr)
    }

    fn parse_primary(&mut self) -> Result<Expr, ParseError> {
        let token = self.advance();
        match token.kind {
            TokenKind::Name(value) if value == "True" || value == "False" || value == "None" => {
                Ok(Expr::Constant(value))
            }
            TokenKind::Name(value) if value == "not" => Ok(Expr::UnaryOp {
                op: UnaryOp::Not,
                value: Box::new(self.parse_expr(9)?),
            }),
            TokenKind::Name(value) => Ok(Expr::Name(value)),
            TokenKind::Number(value) => Ok(Expr::Number(value)),
            TokenKind::String(value) => Ok(Expr::String(value)),
            TokenKind::Dollar => {
                let marker = match self.peek().kind.clone() {
                    TokenKind::Name(value) | TokenKind::Number(value) => {
                        self.advance();
                        format!("${value}")
                    }
                    _ => "$".to_string(),
                };
                Ok(Expr::Raw(marker))
            }
            TokenKind::LParen => self.parse_parenthesized(),
            TokenKind::LBracket => self.parse_list(),
            TokenKind::LBrace => {
                self.consume_balanced(TokenKind::LBrace, TokenKind::RBrace)?;
                Ok(Expr::Dict)
            }
            TokenKind::Plus => Ok(Expr::UnaryOp {
                op: UnaryOp::UAdd,
                value: Box::new(self.parse_expr(13)?),
            }),
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

    fn parse_parenthesized(&mut self) -> Result<Expr, ParseError> {
        if self.eat(&TokenKind::RParen) {
            return Ok(Expr::Tuple(Vec::new()));
        }
        let first = self.parse_arrow_or_expr()?;
        if !self.eat(&TokenKind::Comma) {
            self.expect(&TokenKind::RParen)?;
            return Ok(first);
        }
        let mut items = vec![first];
        if !matches!(self.peek().kind, TokenKind::RParen) {
            loop {
                items.push(self.parse_arrow_or_expr()?);
                if !self.eat(&TokenKind::Comma) {
                    break;
                }
                if matches!(self.peek().kind, TokenKind::RParen) {
                    break;
                }
            }
        }
        self.expect(&TokenKind::RParen)?;
        Ok(Expr::Tuple(items))
    }

    fn parse_list(&mut self) -> Result<Expr, ParseError> {
        let mut items = Vec::new();
        if self.eat(&TokenKind::RBracket) {
            return Ok(Expr::List(items));
        }
        loop {
            items.push(self.parse_arrow_or_expr()?);
            if !self.eat(&TokenKind::Comma) {
                break;
            }
            if matches!(self.peek().kind, TokenKind::RBracket) {
                break;
            }
        }
        self.expect(&TokenKind::RBracket)?;
        Ok(Expr::List(items))
    }

    fn consume_balanced(
        &mut self,
        open: TokenKind,
        close: TokenKind,
    ) -> Result<(), ParseError> {
        let mut depth = 1isize;
        while depth > 0 {
            let token = self.advance();
            if matches!(token.kind, TokenKind::Eof) {
                return Err(ParseError::new("unterminated balanced expression", token.offset));
            }
            if same_variant(&token.kind, &open) {
                depth += 1;
            } else if same_variant(&token.kind, &close) {
                depth -= 1;
            }
        }
        Ok(())
    }

    fn current_infix(&self) -> Option<(InfixOp, u8, u8)> {
        match self.peek().kind {
            TokenKind::Name(ref value) if value == "or" => {
                Some((InfixOp::Bool(BoolOp::Or), 4, 5))
            }
            TokenKind::Name(ref value) if value == "and" => {
                Some((InfixOp::Bool(BoolOp::And), 6, 7))
            }
            TokenKind::Less => Some((InfixOp::Cmp(CmpOp::Lt), 8, 9)),
            TokenKind::LessEqual => Some((InfixOp::Cmp(CmpOp::LtE), 8, 9)),
            TokenKind::Greater => Some((InfixOp::Cmp(CmpOp::Gt), 8, 9)),
            TokenKind::GreaterEqual => Some((InfixOp::Cmp(CmpOp::GtE), 8, 9)),
            TokenKind::DoubleEqual => Some((InfixOp::Cmp(CmpOp::Eq), 8, 9)),
            TokenKind::NotEqual => Some((InfixOp::Cmp(CmpOp::NotEq), 8, 9)),
            TokenKind::Plus => Some((InfixOp::Bin(BinOp::Add), 10, 11)),
            TokenKind::Minus => Some((InfixOp::Bin(BinOp::Sub), 10, 11)),
            TokenKind::Star => Some((InfixOp::Bin(BinOp::Mult), 12, 13)),
            TokenKind::Slash => Some((InfixOp::Bin(BinOp::Div), 12, 13)),
            TokenKind::DoubleSlash => Some((InfixOp::Bin(BinOp::FloorDiv), 12, 13)),
            TokenKind::Percent => Some((InfixOp::Bin(BinOp::Mod), 12, 13)),
            TokenKind::At => Some((InfixOp::Bin(BinOp::MatMult), 12, 13)),
            TokenKind::DoubleStar => Some((InfixOp::Bin(BinOp::Pow), 15, 14)),
            _ => None,
        }
    }

    fn collect_head_until_colon(&mut self) -> String {
        let start = self.cursor;
        let mut depth = 0isize;
        while !matches!(self.peek().kind, TokenKind::Eof) {
            match self.peek().kind {
                TokenKind::LParen | TokenKind::LBracket | TokenKind::LBrace => depth += 1,
                TokenKind::RParen | TokenKind::RBracket | TokenKind::RBrace => depth -= 1,
                TokenKind::Colon if depth == 0 => break,
                _ => {}
            }
            self.advance();
        }
        self.token_text_range(start, self.cursor)
    }

    fn collect_until_matching(&mut self, close: TokenKind) -> Result<String, ParseError> {
        let start = self.cursor;
        let mut depth = 0isize;
        while !same_variant(&self.peek().kind, &close) || depth > 0 {
            match self.peek().kind {
                TokenKind::LParen | TokenKind::LBracket | TokenKind::LBrace => depth += 1,
                TokenKind::RParen | TokenKind::RBracket | TokenKind::RBrace => depth -= 1,
                TokenKind::Eof => {
                    return Err(ParseError::new("unexpected end of file", self.peek().offset));
                }
                _ => {}
            }
            self.advance();
        }
        Ok(self.token_text_range(start, self.cursor))
    }

    fn collect_raw_until_line_end(&mut self) -> String {
        let start = self.cursor;
        let mut depth = 0isize;
        while !matches!(self.peek().kind, TokenKind::Eof) {
            match self.peek().kind {
                TokenKind::LParen | TokenKind::LBracket | TokenKind::LBrace => depth += 1,
                TokenKind::RParen | TokenKind::RBracket | TokenKind::RBrace => depth -= 1,
                TokenKind::Newline | TokenKind::Dedent if depth == 0 => break,
                _ => {}
            }
            self.advance();
        }
        self.token_text_range(start, self.cursor)
    }

    fn colon_starts_indented_suite(&self) -> bool {
        matches!(self.peek().kind, TokenKind::Colon)
            && self
                .tokens
                .get(self.cursor + 1)
                .is_some_and(|token| matches!(token.kind, TokenKind::Newline))
    }

    fn token_text_range(&self, start: usize, end: usize) -> String {
        self.tokens[start..end]
            .iter()
            .map(|token| token_text(&token.kind))
            .filter(|text| !text.is_empty())
            .collect::<Vec<_>>()
            .join(" ")
            .trim()
            .to_string()
    }

    fn expect_stmt_end(&mut self) -> Result<(), ParseError> {
        if self.suite_closed {
            self.suite_closed = false;
            return Ok(());
        }
        if self.at_stmt_end() {
            Ok(())
        } else {
            Err(ParseError::new("expected statement end", self.peek().offset))
        }
    }

    fn at_stmt_end(&self) -> bool {
        matches!(
            self.peek().kind,
            TokenKind::Newline | TokenKind::Semi | TokenKind::Dedent | TokenKind::Eof
        )
    }

    fn skip_separators(&mut self) {
        while matches!(self.peek().kind, TokenKind::Newline | TokenKind::Semi) {
            self.advance();
        }
    }

    fn expect_keyword(&mut self, expected: &str) -> Result<(), ParseError> {
        if self.is_keyword(expected) {
            self.advance();
            Ok(())
        } else {
            Err(ParseError::new(
                format!("expected keyword {expected}"),
                self.peek().offset,
            ))
        }
    }

    fn is_keyword(&self, expected: &str) -> bool {
        matches!(&self.peek().kind, TokenKind::Name(value) if value == expected)
    }

    fn advance_name(&mut self) -> Result<String, ParseError> {
        let token = self.advance();
        match token.kind {
            TokenKind::Name(value) => Ok(value),
            _ => Err(ParseError::new("expected name", token.offset)),
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

    fn advance(&mut self) -> Token {
        let token = self.tokens[self.cursor].clone();
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

impl Expr {
    fn brief(&self) -> String {
        match self {
            Expr::Name(value) => value.clone(),
            Expr::Call { func, .. } => format!("{}(...)", func.brief()),
            Expr::Attribute { value, attr } => format!("{}.{}", value.brief(), attr),
            Expr::Raw(value) => value.clone(),
            _ => format!("{self:?}"),
        }
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
        TokenKind::DoubleSlash => "//",
        TokenKind::Percent => "%",
        TokenKind::At => "@",
        TokenKind::Equal => "=",
        TokenKind::PlusEqual => "+=",
        TokenKind::MinusEqual => "-=",
        TokenKind::StarEqual => "*=",
        TokenKind::SlashEqual => "/=",
        TokenKind::FatArrow => "=>",
        TokenKind::Arrow => "->",
        TokenKind::Dollar => "$",
        TokenKind::Pipe => "|",
        TokenKind::PipeGreater => "|>",
        TokenKind::Question => "?",
        TokenKind::QuestionQuestion => "??",
        TokenKind::QuestionDot => "?.",
        TokenKind::Less => "<",
        TokenKind::Greater => ">",
        TokenKind::LessEqual => "<=",
        TokenKind::GreaterEqual => ">=",
        TokenKind::DoubleEqual => "==",
        TokenKind::NotEqual => "!=",
        TokenKind::LParen => "(",
        TokenKind::RParen => ")",
        TokenKind::LBracket => "[",
        TokenKind::RBracket => "]",
        TokenKind::LBrace => "{",
        TokenKind::RBrace => "}",
        TokenKind::Dot => ".",
        TokenKind::DotDot => "..",
        TokenKind::DotDotLess => "..<",
        TokenKind::Colon => ":",
        TokenKind::Comma => ",",
        TokenKind::Newline => "newline",
        TokenKind::Indent => "indent",
        TokenKind::Dedent => "dedent",
        TokenKind::Semi => ";",
        TokenKind::Eof => "end of file",
    }
}

fn token_text(kind: &TokenKind) -> String {
    match kind {
        TokenKind::Name(value) | TokenKind::Number(value) | TokenKind::String(value) => {
            value.clone()
        }
        other => token_name(other).to_string(),
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
        Stmt::AugAssign { target, op, value } => format!(
            "{{\"type\":\"AugAssign\",\"target\":{},\"op\":{},\"value\":{}}}",
            json_string(target),
            json_string(op),
            expr_json(value),
        ),
        Stmt::Expr(value) => format!(
            "{{\"type\":\"Expr\",\"value\":{}}}",
            expr_json(value),
        ),
        Stmt::FunctionDef { name, params, body } => function_json(Some(name), params, body),
        Stmt::Return(value) => optional_expr_json("Return", value),
        Stmt::Yield(value) => optional_expr_json("Yield", value),
        Stmt::Raise(value) => optional_expr_json("Raise", value),
        Stmt::Simple(kind) => format!("{{\"type\":{}}}", json_string(kind)),
        Stmt::Suite {
            kind,
            head,
            body,
            clauses,
        } => {
            let body = body.iter().map(stmt_json).collect::<Vec<_>>().join(",");
            let clauses = clauses
                .iter()
                .map(clause_json)
                .collect::<Vec<_>>()
                .join(",");
            format!(
                "{{\"type\":\"Suite\",\"kind\":{},\"head\":{},\"body\":[{}],\"clauses\":[{}]}}",
                json_string(kind),
                json_string(head),
                body,
                clauses,
            )
        }
    }
}

fn clause_json(clause: &Clause) -> String {
    let body = clause
        .body
        .iter()
        .map(stmt_json)
        .collect::<Vec<_>>()
        .join(",");
    format!(
        "{{\"kind\":{},\"head\":{},\"body\":[{}]}}",
        json_string(&clause.kind),
        json_string(&clause.head),
        body,
    )
}

fn optional_expr_json(kind: &str, value: &Option<Expr>) -> String {
    match value {
        Some(value) => format!(
            "{{\"type\":{},\"value\":{}}}",
            json_string(kind),
            expr_json(value)
        ),
        None => format!("{{\"type\":{},\"value\":null}}", json_string(kind)),
    }
}

fn expr_json(expr: &Expr) -> String {
    match expr {
        Expr::Name(value) => format!("{{\"type\":\"Name\",\"id\":{}}}", json_string(value)),
        Expr::Number(value) => format!("{{\"type\":\"Number\",\"value\":{}}}", json_string(value)),
        Expr::String(value) => format!("{{\"type\":\"String\",\"value\":{}}}", json_string(value)),
        Expr::Constant(value) => {
            format!("{{\"type\":\"Constant\",\"value\":{}}}", json_string(value))
        }
        Expr::List(items) => {
            let items = items.iter().map(expr_json).collect::<Vec<_>>().join(",");
            format!("{{\"type\":\"List\",\"items\":[{}]}}", items)
        }
        Expr::Tuple(items) => {
            let items = items.iter().map(expr_json).collect::<Vec<_>>().join(",");
            format!("{{\"type\":\"Tuple\",\"items\":[{}]}}", items)
        }
        Expr::Dict => "{\"type\":\"Dict\"}".to_string(),
        Expr::Attribute { value, attr } => format!(
            "{{\"type\":\"Attribute\",\"value\":{},\"attr\":{}}}",
            expr_json(value),
            json_string(attr),
        ),
        Expr::Subscript { value, slice } => format!(
            "{{\"type\":\"Subscript\",\"value\":{},\"slice\":{}}}",
            expr_json(value),
            expr_json(slice),
        ),
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
        Expr::Compare { left, op, right } => format!(
            "{{\"type\":\"Compare\",\"left\":{},\"op\":{},\"right\":{}}}",
            expr_json(left),
            json_string(cmp_op_name(*op)),
            expr_json(right),
        ),
        Expr::BoolOp { left, op, right } => format!(
            "{{\"type\":\"BoolOp\",\"left\":{},\"op\":{},\"right\":{}}}",
            expr_json(left),
            json_string(bool_op_name(*op)),
            expr_json(right),
        ),
        Expr::UnaryOp { op, value } => format!(
            "{{\"type\":\"UnaryOp\",\"op\":{},\"value\":{}}}",
            json_string(unary_op_name(*op)),
            expr_json(value),
        ),
        Expr::IfExp { body, test, orelse } => format!(
            "{{\"type\":\"IfExp\",\"body\":{},\"test\":{},\"orelse\":{}}}",
            expr_json(body),
            expr_json(test),
            expr_json(orelse),
        ),
        Expr::FunctionExpr { params, body } => function_json(None, params, body),
        Expr::Raw(value) => format!("{{\"type\":\"Raw\",\"value\":{}}}", json_string(value)),
    }
}

fn function_json(name: Option<&String>, params: &[String], body: &Expr) -> String {
    let name = match name {
        Some(value) => json_string(value),
        None => "null".to_string(),
    };
    let params = params
        .iter()
        .map(|param| json_string(param))
        .collect::<Vec<_>>()
        .join(",");
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
        BinOp::FloorDiv => "FloorDiv",
        BinOp::Mod => "Mod",
        BinOp::MatMult => "MatMult",
        BinOp::Pow => "Pow",
    }
}

fn cmp_op_name(op: CmpOp) -> &'static str {
    match op {
        CmpOp::Lt => "Lt",
        CmpOp::LtE => "LtE",
        CmpOp::Gt => "Gt",
        CmpOp::GtE => "GtE",
        CmpOp::Eq => "Eq",
        CmpOp::NotEq => "NotEq",
    }
}

fn bool_op_name(op: BoolOp) -> &'static str {
    match op {
        BoolOp::And => "And",
        BoolOp::Or => "Or",
    }
}

fn unary_op_name(op: UnaryOp) -> &'static str {
    match op {
        UnaryOp::UAdd => "UAdd",
        UnaryOp::Not => "Not",
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
