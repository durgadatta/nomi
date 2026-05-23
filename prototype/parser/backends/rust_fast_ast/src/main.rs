use std::env;
use std::fs;
use std::process;

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
    let json = nomi_rust_fast_ast::parse_to_json(&source)?;
    println!("{json}");
    Ok(())
}
