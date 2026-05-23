# pest-readable-cst

Readable PEG parser spike for Nomi.

This crate is deliberately a scaffold, not a promoted parser frontend. It
exists so the Python parser registry can address a PEG candidate by name while
the grammar grows behind the same gates as the Rust direct-AST parser.

Current command contract:

```bash
cargo run --manifest-path parsers/pest_readable_cst/Cargo.toml -- cst-json samples/demo.nomi
```

Output is a JSON debug/CST payload on stdout. A nonzero exit means parse or CLI
failure with diagnostics on stderr.

Promotion order:

1. Replace the permissive catch-all grammar with a real Nomi PEG grammar slice
   by slice.
2. Set `parse_current_grammar=True` only after the shared parser-acceptance
   matrix passes against Lark.
3. Add a Python payload adapter and set `lower_to_python_ast=True` only after
   exact Python AST parity.
4. Set `selectable_for_execution=True` only after runtime, regression, and CLI
   parity match Lark when this frontend is selected.
