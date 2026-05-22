mod ast;
mod error;
mod lexer;
mod parser;
mod token;

use std::env;
use std::fs;
use std::process;

use ast::module_json;
use lexer::lex;
use parser::Parser;

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
