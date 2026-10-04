# Local Composition Experiments

> Status: executed original finite models and named standard-library host
> observations, 2026-10-04; no Nomi or foreign-framework conformance.

[Data/time](dependencies_and_time.md) · [AI/ML](ai_ml.md) ·
[Domain composition](../domain_composition.md)

Run from the repository root:

```bash
python3 docs/research/data_workflows/probe_composition.py --check docs/research/data_workflows/composition_probe_results.json
pytest -n 0 prototype/tests/unit/tools/test_domain_composition_research.py
```

[Script](probe_composition.py) and [capture](composition_probe_results.json)
own the actual inventory and historical host versions. `--output PATH` produces
an explicitly requested generated capture; check mode never rewrites it.
Repeated JSON object fields and changed outcomes/scope are rejected. Historical
version differences alone are provenance, not a semantic regression.

| Probe | Executed discriminator | What it does not establish |
| --- | --- | --- |
| CP01 | `graphlib` accepts two of 24 diamond permutations and rejects a cycle | A scheduler, tasks, fairness, conflict-free effects or distributed execution |
| CP02 | Same drawn edge has two roles; task owner rejects attribution | Nomi typechecking or a universal graph algebra |
| CP03 | SQLite queries original half-open valid/known intervals: 100 then 120; upper boundary absent | XTDB/Datomic behavior, clock semantics or concurrency |
| CP04 | Missing backing content and unknown version fail without latest fallback | Retention, lease, privacy or durable-store enforcement |
| CP05 | Individually pinned sources do not establish a shared transaction basis | Actual inconsistency or a distributed snapshot protocol |
| CP06 | Signed bag update preserves sum; naive subtraction fails for deleted minimum | General incremental SQL, negative multiplicity or numeric reassociation laws |
| CP07 | Changed input/profile changes a fixture key; cache availability is not current read permission | Read-set completeness, authorization, canonical JSON or authenticity |
| CP08 | Training-only mean stays 2; held-out inclusion yields 104/3 or 68 | An estimator, model quality, general leakage detection or statistical validity |
| CP09 | Fact valid before prediction is unavailable until its recording time | Feature-store correctness, causal validity or clock mappings |
| CP10 | Equal extents with swapped axis names fail a named-axis policy | Tensor, AD, shape checker, contraction or device behavior |
| CP11 | Weights lack four required training-state fields; complete metadata still does not prove exact resume | Model loading, state semantics, safe deserialization or training execution |
| CP12 | Mutable model alias changes resolution; equal catalog titles retain different work IDs | Registry/bibliographic authentication, resolution or ID generation |
| CP13 | Only one of 16 supplied scope/grant combinations meets exact-review policy | Authenticated review, human understanding, capability enforcement or publication |

The imposed policies are visible in code and capture limits. A checker accepting
the fields we supplied is not evidence that a real type/effect system can prove
them. Graphlib and SQLite are actually called; no Airflow, Dagster, lakehouse,
ML/AD engine, network/device or human participant is called.

The existing [interaction probes](../interfaces/experiments.md) retain the
stronger uncertain-outcome, publication-race, revision-reuse and incomplete-clock
counterexamples. Do not count them again as new domain integrations. DT1-DT5,
ML1-ML6 and DC1-DC6 are candidate comparisons; these local discriminators execute
selected subcases only. DW1-DW8 have not become completed experiments by being
linked here.

Next: actual D1-D3 typed descriptions and one established engine adapter with
independent fixtures. A source formatter, real capability/region checker,
device/runtime execution, authenticated approval, usability study and
cross-backend equivalence remain unperformed.
