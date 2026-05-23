use pest::Parser;
use pest_derive::Parser;
use pest::iterators::{Pair, Pairs};
use std::env;
use std::fs;
use std::path::Path;
use std::fmt::Write as FmtWrite;

#[derive(Parser)]
#[grammar = "grammar.pest"]
struct NomiPegParser;

/// INDENT / DEDENT markers injected into the source before parsing.
const INDENT: char = '\u{0001}';
const DEDENT: char = '\u{0002}';

fn main() {
    if let Err(error) = run() {
        eprintln!("{error}");
        std::process::exit(1);
    }
}

fn run() -> Result<(), String> {
    let mut args = env::args().skip(1);
    let command = args
        .next()
        .ok_or_else(|| "usage: nomi-pest-readable-cst cst-json <source>".to_string())?;
    let source_path = args
        .next()
        .ok_or_else(|| "usage: nomi-pest-readable-cst cst-json <source>".to_string())?;
    if args.next().is_some() {
        return Err("usage: nomi-pest-readable-cst cst-json <source>".to_string());
    }
    if command != "cst-json" {
        return Err(format!("unknown command: {command}"));
    }

    let raw_source = fs::read_to_string(&source_path)
        .map_err(|error| format!("failed to read {source_path}: {error}"))?;

    let source = preprocess_indentation(&raw_source);

    let pairs = NomiPegParser::parse(Rule::file_input, &source)
        .map_err(|error| format!("parse failed for {source_path}: {error}"))?;

    let json = pairs_to_json(pairs, Path::new(&source_path), &raw_source);
    println!("{json}");
    Ok(())
}

// ── Indentation preprocessing ──────────────────────────────────────────

fn preprocess_indentation(source: &str) -> String {
    let lines: Vec<&str> = source.lines().collect();
    let mut output = String::with_capacity(source.len() + 256);
    let mut indent_stack: Vec<usize> = vec![0];
    let mut first = true;

    // Detect the original line endings for reconstruction.
    let newline = if source.contains("\r\n") { "\r\n" } else { "\n" };

    for line in &lines {
        let trimmed = line.trim();

        if !first {
            output.push_str(newline);
        }
        first = false;

        // Blank lines and comment-only lines pass through unchanged.
        if trimmed.is_empty() || trimmed.starts_with('#') {
            output.push_str(line);
            continue;
        }

        let indent = leading_ws(line);

        if indent > *indent_stack.last().unwrap_or(&0) {
            output.push(INDENT);
            indent_stack.push(indent);
        } else {
            while indent < *indent_stack.last().unwrap_or(&0) {
                output.push(DEDENT);
                indent_stack.pop();
                // DEDENT on its own line so it is always consumed by
                // suite_body / body_block newline* ~ dedent patterns.
                output.push_str(newline);
            }
        }

        // Push the line content (strip the leading whitespace we just tracked).
        output.push_str(trimmed);
    }

    // Close remaining indentation levels at EOF.
    while indent_stack.len() > 1 {
        output.push_str(newline);
        output.push(DEDENT);
        indent_stack.pop();
        output.push_str(newline);
    }

    // Ensure trailing newline so the final simple_stmt is terminated.
    if !output.is_empty() && !output.ends_with('\n') {
        output.push('\n');
    }

    output
}

fn leading_ws(line: &str) -> usize {
    line.chars().take_while(|c| *c == ' ' || *c == '\t').count()
}

// ── CST JSON emission ──────────────────────────────────────────────────

fn pairs_to_json(pairs: Pairs<Rule>, source_path: &Path, source: &str) -> String {
    let mut buf = String::with_capacity(4096);
    buf.push('{');
    buf.push_str(&format!(
        "\"frontend\":\"pest-readable-cst\",\"source\":{},\"bytes\":{},\"lines\":{}",
        json_string(&source_path.display().to_string()),
        source.len(),
        source.lines().count(),
    ));
    buf.push_str(",\"cst\":");
    pairs_to_json_value(&mut buf, pairs);
    buf.push('}');
    buf
}

fn pairs_to_json_value(buf: &mut String, pairs: Pairs<Rule>) {
    let mut items: Vec<(String, String)> = Vec::new();
    for pair in pairs {
        let key = format!("{:?}", pair.as_rule());
        let value = pair_to_json(pair);
        items.push((key, value));
    }

    if items.is_empty() {
        buf.push_str("null");
        return;
    }

    if items.len() == 1 && items[0].1 == "null" {
        buf.push('{');
        buf.push_str(&format!("\"{}\":null", items[0].0));
        buf.push('}');
        return;
    }

    // Collect identical keys into arrays.
    buf.push('{');
    let mut i = 0;
    while i < items.len() {
        if i > 0 {
            buf.push(',');
        }
        let key = &items[i].0;
        let mut end = i + 1;
        while end < items.len() && items[end].0 == *key {
            end += 1;
        }
        if end - i == 1 {
            buf.push_str(&format!("\"{}\":{}", key, items[i].1));
        } else {
            buf.push_str(&format!("\"{}\":[", key));
            for j in i..end {
                if j > i {
                    buf.push(',');
                }
                buf.push_str(&items[j].1);
            }
            buf.push(']');
        }
        i = end;
    }
    buf.push('}');
}

fn pair_to_json(pair: Pair<Rule>) -> String {
    let inner = pair.clone().into_inner();
    if inner.peek().is_none() {
        // Leaf node — emit its span text.
        return json_string(pair.as_str());
    }
    let mut buf = String::new();
    pairs_to_json_value(&mut buf, inner);
    buf
}

fn json_string(value: &str) -> String {
    let mut output = String::from("\"");
    for ch in value.chars() {
        match ch {
            '"' => output.push_str("\\\""),
            '\\' => output.push_str("\\\\"),
            '\n' => output.push_str("\\n"),
            '\r' => output.push_str("\\r"),
            '\t' => output.push_str("\\t"),
            INDENT => output.push_str("«INDENT»"),
            DEDENT => output.push_str("«DEDENT»"),
            ch if ch.is_control() => {
                write!(&mut output, "\\u{:04x}", ch as u32).unwrap();
            }
            ch => output.push(ch),
        }
    }
    output.push('"');
    output
}
