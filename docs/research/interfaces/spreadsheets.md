# Spreadsheets: Name The Dependency

> Status: interface evidence and bounded Nomi hypotheses.

The [data source-form study](../data_workflows/source_forms.md) extends this
thread into LET/LAMBDA/FILTER, VBA Formula2/events, Power Query M and DAX context.
It owns those detailed comparisons rather than duplicating them here.

## Evidence And Pressure

Excel distinguishes relative, absolute, and mixed references when copying a
formula. Table structured references use table/column names; dynamic-array
spills can fail when the output region cannot accommodate them.
[References](https://support.microsoft.com/en-us/excel/switch-between-relative-absolute-and-mixed-references),
[Table names](https://support.microsoft.com/en-us/excel/using-structured-references-with-excel-tables),
[Spill boundary](https://support.microsoft.com/en-us/excel/spill-error-extends-beyond-the-worksheet-s-edge).

The cognitive contribution is inspecting intermediate quantities near the
objects they describe. The cost is that location can become identity and
copying can change meaning. A plausible-looking number is weak evidence that
the intended rows and units were used.

## Nomi Normal Form

```nomi
func line_total(line: Line) -> Int:
    return line.quantity * line.unit_price_minor

amounts = map(lines, line_total)
total_minor = fold(amounts, 0, (sum, amount) => sum + amount)
```

These proposed collection contracts already occur in the target suite. A grid
could project named fields and derived values from this source. It must show
input versus derived cells and the exact computation. Row sorting must not
change a reference keyed by a domain ID. Copy/fill should become an explicit
transformation over a selected collection, not hidden relative addressing.

**Adapt:** visible dependencies, named inputs, immediate pure feedback.
**Defer:** editable formula graphs until binding identities and cycles have
contracts. **Reject for core:** coordinate variables, implicit coercion, or
automatic effectful recalculation. A spreadsheet facade that only renders
text poorly earns no special status.

## Discriminating Experiment

Use the [invoice target](../../design/interaction_model_target.nomi). Compare
text-only, read-only grid, and editable input grid on six tasks: change quantity,
explain total, sort rows, insert a row, submit negative input, and trace an old
result after editing. Measure wrong-reference and stale-value errors, repair
time, and ability to export readable source. A source-synchronized input grid
wins only if it reduces errors without adding a second authoritative program.
Keep it out of runnable playground samples until the source contract exists.
