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
    BlockCall {
        call: Expr,
        params: Option<String>,
        body: Vec<Stmt>,
    },
    WhereAssign {
        target: String,
        value: Expr,
        body: Vec<Stmt>,
    },
    WhereFunction {
        name: String,
        params: Vec<String>,
        value: Expr,
        body: Vec<Stmt>,
    },
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
    String {
        value: String,
        source: String,
    },
    Constant(String),
    List(Vec<Expr>),
    Tuple(Vec<Expr>),
    Dict(Vec<(Expr, Expr)>),
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
    BitAnd,
    BitOr,
    BitXor,
    LShift,
    RShift,
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
    USub,
    Not,
    Invert,
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
    json_object(vec![
        ("schema", json_string("nomi.rust-ast")),
        ("version", "1".to_string()),
        ("type", json_string("Module")),
        ("body", json_array(body.iter().map(stmt_json))),
    ])
}

fn stmt_json(stmt: &Stmt) -> String {
    match stmt {
        Stmt::Assign { target, value } => json_object(vec![
            ("type", json_string("Assign")),
            ("target", json_string(target)),
            ("value", expr_json(value)),
        ]),
        Stmt::AugAssign { target, op, value } => json_object(vec![
            ("type", json_string("AugAssign")),
            ("target", json_string(target)),
            ("op", json_string(op)),
            ("value", expr_json(value)),
        ]),
        Stmt::Expr(value) => json_object(vec![
            ("type", json_string("Expr")),
            ("value", expr_json(value)),
        ]),
        Stmt::FunctionDef { name, params, body } => function_json(Some(name), params, body),
        Stmt::Return(value) => optional_expr_json("Return", value),
        Stmt::Yield(value) => optional_expr_json("Yield", value),
        Stmt::Raise(value) => optional_expr_json("Raise", value),
        Stmt::Simple(kind) => json_object(vec![("type", json_string(kind))]),
        Stmt::BlockCall { call, params, body } => {
            let head = match params {
                Some(params) => format!("{} -> {}", call.brief(), params),
                None => call.brief(),
            };
            let params = match params {
                Some(value) => json_string(value),
                None => json_null(),
            };
            json_object(vec![
                ("type", json_string("Suite")),
                ("kind", json_string("BlockCall")),
                ("head", json_string(&head)),
                ("body", json_array(body.iter().map(stmt_json))),
                ("clauses", json_array(std::iter::empty())),
                ("call", expr_json(call)),
                ("params", params),
            ])
        }
        Stmt::WhereAssign {
            target,
            value,
            body,
        } => json_object(vec![
            ("type", json_string("Suite")),
            ("kind", json_string("WhereAssign")),
            (
                "head",
                json_string(&format!("{target} = {}", value.brief())),
            ),
            ("body", json_array(body.iter().map(stmt_json))),
            ("clauses", json_array(std::iter::empty())),
            ("target", json_string(target)),
            ("value", expr_json(value)),
        ]),
        Stmt::WhereFunction {
            name,
            params,
            value,
            body,
        } => json_object(vec![
            ("type", json_string("Suite")),
            ("kind", json_string("WhereFunction")),
            (
                "head",
                json_string(&format!(
                    "{name}({}) = {}",
                    params.join(", "),
                    value.brief()
                )),
            ),
            ("body", json_array(body.iter().map(stmt_json))),
            ("clauses", json_array(std::iter::empty())),
            ("name", json_string(name)),
            (
                "params",
                json_array(params.iter().map(|param| json_string(param))),
            ),
            ("value", expr_json(value)),
        ]),
        Stmt::Suite {
            kind,
            head,
            body,
            clauses,
        } => json_object(vec![
            ("type", json_string("Suite")),
            ("kind", json_string(kind)),
            ("head", json_string(head)),
            ("body", json_array(body.iter().map(stmt_json))),
            ("clauses", json_array(clauses.iter().map(clause_json))),
        ]),
    }
}

fn clause_json(clause: &Clause) -> String {
    json_object(vec![
        ("kind", json_string(&clause.kind)),
        ("head", json_string(&clause.head)),
        ("body", json_array(clause.body.iter().map(stmt_json))),
    ])
}

fn optional_expr_json(kind: &str, value: &Option<Expr>) -> String {
    match value {
        Some(value) => json_object(vec![
            ("type", json_string(kind)),
            ("value", expr_json(value)),
        ]),
        None => json_object(vec![("type", json_string(kind)), ("value", json_null())]),
    }
}

fn expr_json(expr: &Expr) -> String {
    match expr {
        Expr::Name(value) => json_object(vec![
            ("type", json_string("Name")),
            ("id", json_string(value)),
        ]),
        Expr::Number(value) => json_object(vec![
            ("type", json_string("Number")),
            ("value", json_string(value)),
        ]),
        Expr::String { value, source } => json_object(vec![
            ("type", json_string("String")),
            ("value", json_string(value)),
            ("source", json_string(source)),
        ]),
        Expr::Constant(value) => json_object(vec![
            ("type", json_string("Constant")),
            ("value", json_string(value)),
        ]),
        Expr::List(items) => json_object(vec![
            ("type", json_string("List")),
            ("items", json_array(items.iter().map(expr_json))),
        ]),
        Expr::Tuple(items) => json_object(vec![
            ("type", json_string("Tuple")),
            ("items", json_array(items.iter().map(expr_json))),
        ]),
        Expr::Dict(items) => json_object(vec![
            ("type", json_string("Dict")),
            (
                "keys",
                json_array(items.iter().map(|(key, _)| expr_json(key))),
            ),
            (
                "values",
                json_array(items.iter().map(|(_, value)| expr_json(value))),
            ),
        ]),
        Expr::Attribute { value, attr } => json_object(vec![
            ("type", json_string("Attribute")),
            ("value", expr_json(value)),
            ("attr", json_string(attr)),
        ]),
        Expr::Subscript { value, slice } => json_object(vec![
            ("type", json_string("Subscript")),
            ("value", expr_json(value)),
            ("slice", expr_json(slice)),
        ]),
        Expr::Call { func, args } => json_object(vec![
            ("type", json_string("Call")),
            ("func", expr_json(func)),
            ("args", json_array(args.iter().map(expr_json))),
        ]),
        Expr::BinOp { left, op, right } => json_object(vec![
            ("type", json_string("BinOp")),
            ("left", expr_json(left)),
            ("op", json_string(op_name(*op))),
            ("right", expr_json(right)),
        ]),
        Expr::Compare { left, op, right } => json_object(vec![
            ("type", json_string("Compare")),
            ("left", expr_json(left)),
            ("op", json_string(cmp_op_name(*op))),
            ("right", expr_json(right)),
        ]),
        Expr::BoolOp { left, op, right } => json_object(vec![
            ("type", json_string("BoolOp")),
            ("left", expr_json(left)),
            ("op", json_string(bool_op_name(*op))),
            ("right", expr_json(right)),
        ]),
        Expr::UnaryOp { op, value } => json_object(vec![
            ("type", json_string("UnaryOp")),
            ("op", json_string(unary_op_name(*op))),
            ("value", expr_json(value)),
        ]),
        Expr::IfExp { body, test, orelse } => json_object(vec![
            ("type", json_string("IfExp")),
            ("body", expr_json(body)),
            ("test", expr_json(test)),
            ("orelse", expr_json(orelse)),
        ]),
        Expr::FunctionExpr { params, body } => function_json(None, params, body),
        Expr::Raw(value) => json_object(vec![
            ("type", json_string("Raw")),
            ("value", json_string(value)),
        ]),
    }
}

fn function_json(name: Option<&String>, params: &[String], body: &Expr) -> String {
    let name = match name {
        Some(value) => json_string(value),
        None => json_null(),
    };
    json_object(vec![
        ("type", json_string("FunctionDef")),
        ("name", name),
        (
            "params",
            json_array(params.iter().map(|param| json_string(param))),
        ),
        ("body", expr_json(body)),
    ])
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
        BinOp::BitAnd => "BitAnd",
        BinOp::BitOr => "BitOr",
        BinOp::BitXor => "BitXor",
        BinOp::LShift => "LShift",
        BinOp::RShift => "RShift",
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
        UnaryOp::USub => "USub",
        UnaryOp::Not => "Not",
        UnaryOp::Invert => "Invert",
    }
}

use crate::payload::{json_array, json_null, json_object, json_string};
