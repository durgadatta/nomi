# Executed String-Boundary Probes

> Status: reproducible local research observations, recorded 2026-10-01.
>
> Host-library behavior only. No Nomi, GitHub runner, Kubernetes, Helm,
> Kustomize, actual shell, browser renderer or remote service was executed.

## Environment And Reproduction

The [probe script](probe_boundaries.py) uses Python standard-library modules,
PyYAML and jsonschema already installed in the local environment. It performs
in-memory parsing/encoding, an in-memory SQLite query, regular-expression
matching, POSIX lexical serialization and Unicode operations. The shell-like
fixture is data and is never executed.

Recorded versions:

| Component | Version |
| --- | --- |
| Python | 3.14.0rc3 |
| PyYAML | 6.0.3 |
| jsonschema | 4.25.1 |
| SQLite | 3.50.4 |
| Python Unicode database | 16.0.0 |

From the repository root:

```bash
python3 docs/research/dsls/probe_boundaries.py
```

The checked-in [JSON report](probe_results.json) records exact inputs and
outputs. The script defaults to the local current date; `--observed-on` accepts
an explicit ISO date for a capture. Later runs should use their actual
observation date and versions. No dependency install or network access is part
of the script.

## Observations And Their Limits

| Probe | Captured result | Supported inference | Does not establish |
| --- | --- | --- | --- |
| YAML key resolution | `on` becomes Boolean `True`; quoted `"on"` remains text | Adapter policy must name the loader/schema | GitHub's loader or all YAML editions |
| Duplicate keys | Two `replicas` definitions produce final value `2` | This loader silently loses conflicting source evidence | A permitted YAML/Nomi duplicate policy |
| Scalar styles | `|` gives `alpha\nbeta\n`; `>` gives `alpha beta\n`; `|-` strips the final break; `|+` retains two final breaks | Multiline presentation affects decoded text | Every folding/indentation edge case |
| Alias identity | Anchored mapping and alias are the same Python object | A tree adapter needs an explicit alias policy | Required Nomi identity or safe arbitrary graph loading |
| Text versus value | A newline payload adds an `extra` field under naive substitution; whole-value encoding preserves one message | A scalar value must not be confused with document source | General safety of every YAML encoder/config system |
| SQL parameter | Text-built query returns both rows; bound parameter returns none | Bound values preserve this query's data/program boundary | All drivers, identifiers or SQL dialects |
| Regex literal | Pattern `a.+` matches `a.+` and `abc`; quoted literal matches only `a.+` | Pattern source and literal text are different inputs | RE2 behavior, replacement rules or runtime complexity |
| POSIX argv serialization | `shlex.join` then `split` reproduces three arguments exactly | A named lexical serializer preserves this fixture | Actual process launch, Windows or every POSIX shell construct |
| Schema format | Invalid timestamp has zero errors without the format checker and one with it | Validator configuration changes the guarantee | Live admission or every format implementation |
| Unicode units | Composed/decomposed accents differ before NFC; emoji is 1 scalar / 4 UTF-8 bytes / 2 UTF-16 units | Length/equality units must be explicit | Grapheme segmentation or Nomi backend behavior |

The SQL, YAML-value and argv cases include assertions for the intended captured
boundary. Other cases deliberately report the installed libraries' behavior;
the script is not a conformance suite that endorses every observed result.

## Relation To Primary Evidence

YAML's specification requires unique mapping keys and defines scalar styles.
The duplicate result above exposes a loader policy mismatch, not a change to
the standard.
[YAML 1.2.2](https://yaml.org/spec/1.2.2/).

SQL interfaces separate parameters from command source; the SQLite observation
illustrates that distinction locally without claiming libpq was run.
[PostgreSQL parameter API](https://www.postgresql.org/docs/17/libpq-exec.html).

JSON Schema separates annotation and assertion vocabularies; the observation
is specific to jsonschema's default validator and explicit format checker.
[2020-12 validation](https://json-schema.org/draft/2020-12/json-schema-validation).

Unicode normalization supplies a canonical-equivalence operation; it does not
implicitly change ordinary equality in the tested host.
[Unicode normalization](https://unicode.org/reports/tr15/).

## What The Probes Change In The Research

They justify making E2/E3/E6/E7/E9 concrete instead of researching interpolation
punctuation in isolation. They do not select a new Nomi syntax or prove an
architecture. The next experiments must compare Nomi candidates on the three
[representative programs](nomi_candidates.md), retain mapped diagnostics, and
state the exact supported host/dialect contract.

A future integration should use pinned versions and original fixtures to test
GitHub context availability, Kubernetes schema/admission, Helm reevaluation,
Kustomize patches, Compose merge order, policy environments and browser/editor
source ranges. Those are explicitly unperformed here and must not be reported
as passing because the local data probes passed.
