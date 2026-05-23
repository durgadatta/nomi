pub(crate) mod ast;
mod error;
pub(crate) mod lexer;
pub(crate) mod parser;
mod payload;
pub(crate) mod token;

use wasm_bindgen::prelude::*;

use lexer::lex;
use parser::Parser;
use ast::module_json;

pub fn parse_to_json(source: &str) -> Result<String, String> {
    let tokens = lex(source).map_err(|e| e.to_string())?;
    let module = Parser::new(tokens)
        .parse_module()
        .map_err(|e| e.to_string())?;
    Ok(module_json(&module))
}

#[wasm_bindgen]
pub fn parse_nomi(source: &str) -> Result<String, JsValue> {
    parse_to_json(source).map_err(|e| JsValue::from_str(&e))
}
