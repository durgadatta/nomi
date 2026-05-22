#[derive(Debug, Clone)]
pub(crate) enum Stmt {
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
pub(crate) struct Clause {
    pub(crate) kind: String,
    pub(crate) head: String,
    pub(crate) body: Vec<Stmt>,
}

#[derive(Debug, Clone)]
pub(crate) enum Expr {
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
pub(crate) enum BinOp {
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
pub(crate) enum CmpOp {
    Lt,
    LtE,
    Gt,
    GtE,
    Eq,
    NotEq,
}

#[derive(Debug, Clone, Copy)]
pub(crate) enum BoolOp {
    And,
    Or,
}

#[derive(Debug, Clone, Copy)]
pub(crate) enum UnaryOp {
    UAdd,
    Not,
}

#[derive(Debug, Clone, Copy)]
pub(crate) enum InfixOp {
    Bin(BinOp),
    Cmp(CmpOp),
    Bool(BoolOp),
}
impl Expr {
    pub(crate) fn brief(&self) -> String {
        match self {
            Expr::Name(value) => value.clone(),
            Expr::Call { func, .. } => format!("{}(...)", func.brief()),
            Expr::Attribute { value, attr } => format!("{}.{}", value.brief(), attr),
            Expr::Raw(value) => value.clone(),
            _ => format!("{self:?}"),
        }
    }
}
pub(crate) fn module_json(body: &[Stmt]) -> String {
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
