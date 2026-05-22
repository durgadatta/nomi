use crate::ast::{BinOp, BoolOp, Clause, CmpOp, Expr, InfixOp, Stmt, UnaryOp};
use crate::error::ParseError;
use crate::token::{same_variant, token_name, token_text, Token, TokenKind};

pub(crate) struct Parser {
    tokens: Vec<Token>,
    cursor: usize,
    suite_closed: bool,
}

impl Parser {
    pub(crate) fn new(tokens: Vec<Token>) -> Self {
        Self {
            tokens,
            cursor: 0,
            suite_closed: false,
        }
    }

    pub(crate) fn parse_module(&mut self) -> Result<Vec<Stmt>, ParseError> {
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
        if self.is_keyword("class") {
            return self.parse_head_suite("Class");
        }
        if self.is_keyword("with") {
            return self.parse_head_suite("With");
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
            return Ok(Stmt::Return(self.parse_optional_expr_or_raw()));
        }
        if self.is_keyword("yield") {
            self.advance();
            return Ok(Stmt::Yield(self.parse_optional_expr_or_raw()));
        }
        if self.is_keyword("raise") {
            self.advance();
            return Ok(Stmt::Raise(self.parse_optional_expr_or_raw()));
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
            return Ok(Stmt::BlockCall {
                call: expr,
                params: Some(params),
                body,
            });
        }
        if matches!(self.peek().kind, TokenKind::Colon) {
            let body = self.parse_suite_from_current_colon()?;
            return Ok(Stmt::BlockCall {
                call: expr,
                params: None,
                body,
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
        self.skip_separators();
        if self.is_keyword("finally") {
            self.advance();
            let clause_body = self.parse_suite_from_current_colon()?;
            clauses.push(Clause {
                kind: "Finally".to_string(),
                head: String::new(),
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
            let mut body = Vec::new();
            loop {
                body.push(self.parse_stmt()?);
                if matches!(self.peek().kind, TokenKind::Semi) {
                    self.advance();
                    if self.at_inline_suite_end() {
                        break;
                    }
                    continue;
                }
                break;
            }
            Ok(body)
        }
    }

    fn at_inline_suite_end(&self) -> bool {
        matches!(
            self.peek().kind,
            TokenKind::Newline | TokenKind::Dedent | TokenKind::Eof
        ) || self.is_keyword("except")
            || self.is_keyword("finally")
            || self.is_keyword("elif")
            || self.is_keyword("else")
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
        if self.is_keyword("where") {
            self.advance();
            if matches!(self.peek().kind, TokenKind::Colon) {
                let where_body = self.parse_suite_from_current_colon()?;
                return Ok(Some(Stmt::WhereFunction {
                    name,
                    params,
                    value: body,
                    body: where_body,
                }));
            }
            let where_body = self.parse_inline_suite_until_stmt_end()?;
            return Ok(Some(Stmt::WhereFunction {
                name,
                params,
                value: body,
                body: where_body,
            }));
        }
        Ok(Some(Stmt::FunctionDef { name, params, body }))
    }

    fn parse_inline_suite_until_stmt_end(&mut self) -> Result<Vec<Stmt>, ParseError> {
        let mut body = Vec::new();
        while !self.at_stmt_end() {
            body.push(self.parse_stmt()?);
            if matches!(self.peek().kind, TokenKind::Semi) {
                self.advance();
            } else {
                break;
            }
        }
        Ok(body)
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
            if matches!(self.peek().kind, TokenKind::Colon) {
                let body = self.parse_suite_from_current_colon()?;
                return Ok(Some(Stmt::WhereAssign {
                    target,
                    value,
                    body,
                }));
            }
            let body = self.parse_inline_suite_until_stmt_end()?;
            return Ok(Some(Stmt::WhereAssign {
                target,
                value,
                body,
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

    fn parse_optional_expr_or_raw(&mut self) -> Option<Expr> {
        if self.at_stmt_end() {
            return None;
        }
        let mark = self.cursor;
        match self.parse_expr(0) {
            Ok(value) if self.at_stmt_end() => Some(value),
            Ok(_) | Err(_) => {
                self.cursor = mark;
                Some(Expr::Raw(self.collect_raw_until_line_end()))
            }
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
            TokenKind::String { value, source } => Ok(Expr::String { value, source }),
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
            TokenKind::LBrace => self.parse_dict(),
            TokenKind::Plus => Ok(Expr::UnaryOp {
                op: UnaryOp::UAdd,
                value: Box::new(self.parse_expr(13)?),
            }),
            TokenKind::Minus => {
                let value = self.parse_expr(13)?;
                Ok(Expr::UnaryOp {
                    op: UnaryOp::USub,
                    value: Box::new(value),
                })
            }
            _ => Err(ParseError::new("expected expression", token.offset)),
        }
    }

    fn parse_parenthesized(&mut self) -> Result<Expr, ParseError> {
        if self.eat(&TokenKind::RParen) {
            return Ok(Expr::Tuple(Vec::new()));
        }
        if let Some(section) = self.try_prefix_operator_section()? {
            return Ok(section);
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

    fn try_prefix_operator_section(&mut self) -> Result<Option<Expr>, ParseError> {
        let mark = self.cursor;
        let op = match self.advance().kind {
            TokenKind::Plus => BinOp::Add,
            TokenKind::Minus => BinOp::Sub,
            TokenKind::Star => BinOp::Mult,
            TokenKind::Slash => BinOp::Div,
            _ => {
                self.cursor = mark;
                return Ok(None);
            }
        };
        let right = match self.parse_expr(0) {
            Ok(value) => value,
            Err(_) => {
                self.cursor = mark;
                return Ok(None);
            }
        };
        if !self.eat(&TokenKind::RParen) {
            self.cursor = mark;
            return Ok(None);
        }
        Ok(Some(Expr::FunctionExpr {
            params: vec!["__s".to_string()],
            body: Box::new(Expr::BinOp {
                left: Box::new(Expr::Name("__s".to_string())),
                op,
                right: Box::new(right),
            }),
        }))
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

    fn parse_dict(&mut self) -> Result<Expr, ParseError> {
        let mut items = Vec::new();
        if self.eat(&TokenKind::RBrace) {
            return Ok(Expr::Dict(items));
        }
        loop {
            let key = self.parse_arrow_or_expr()?;
            self.expect(&TokenKind::Colon)?;
            let value = self.parse_arrow_or_expr()?;
            items.push((key, value));
            if !self.eat(&TokenKind::Comma) {
                break;
            }
            if matches!(self.peek().kind, TokenKind::RBrace) {
                break;
            }
        }
        self.expect(&TokenKind::RBrace)?;
        Ok(Expr::Dict(items))
    }

    fn current_infix(&self) -> Option<(InfixOp, u8, u8)> {
        match self.peek().kind {
            TokenKind::Name(ref value) if value == "or" => Some((InfixOp::Bool(BoolOp::Or), 4, 5)),
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
                    return Err(ParseError::new(
                        "unexpected end of file",
                        self.peek().offset,
                    ));
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
            Err(ParseError::new(
                "expected statement end",
                self.peek().offset,
            ))
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
