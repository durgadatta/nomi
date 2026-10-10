# Structured Documents: Preserve The Draft

> Status: form-interface evidence and source/presentation hypotheses.

## Evidence And Pressure

HTML's constraint-validation API defines validation states for form controls.
It does not establish that client-side validation is an application security
boundary.
[HTML validation](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#the-constraint-validation-api).

Forms, Markdown, rendered mathematics, and literate documents are complementary
representations to explore. A person can enter a partial date or sketch an
unfinished equation that is not yet a valid value. Rejecting every incomplete
keystroke can prevent construction rather than improve correctness.

## Nomi Normal Form And Placement

Separate draft text, syntactically recovered structure, checked source, decoded
input, and executed result. A form projection may store raw text and diagnostics
while the last committed model remains valid. Commit crosses the same decoder
as other untrusted input. Server/host boundaries revalidate rather than trusting
the widget.

A literate document can attach explanation and examples to source spans.
Rendering markup is not execution and generated HTML is not a second source of
semantic truth. A mathematical view may show a library expression while plain
source remains available. Unknown constructs need a textual fallback, and
comments must survive a supported round trip.

**Adapt:** typed input affordances, document context, progressive feedback.
**Reject:** treating a temporarily incomplete edit as runtime mutation or using
the view's schema as the sole enforcement mechanism.

## Discriminating Experiment

Enter a blank, partial negative sign, malformed integer, then valid invoice
quantity. Ensure draft text persists, all relevant input errors are displayed,
and the committed total changes only after valid decode. Repeat through source,
form, and imported JSON. The playground should distinguish draft diagnostics
from a completed run's diagnostics instead of replacing one with the other.

## Explained Report Challenger

Prepared October 10 under the [broader vision](../../design/vision.md). These are
supplied model facts and literal expectations, not actual sensor measurements,+a report engine, a causal result or a human study. The question is whether a
document can connect its claims to the model and evidence a reader needs.

### Same Initial Facts, Different Possible Claims

Three row identities belong to a declared input snapshot. A reads 20 degrees
Celsius, B reads 22 degrees Celsius and C has no measurement. Missingness is
explicit; it is neither zero nor a measured temperature. The proposed report
summarizes the two available rows rather than imputing the third.
The table is the reviewer's oracle. For prediction tasks, show input facts and
the selected rule before showing derived answers; do not grade answer copying.

| Basis | Fixed expectation | Claim that remains unsupported |
| --- | --- | --- |
| Available raw A/B readings | Count 2 of 3; mean 21 degrees Celsius | The full three-row population mean, sensor accuracy or a world-level conclusion. |
| Declared uniform calibration of +2 degrees for A/B | Transformed A/B 22/24; mean 23 degrees Celsius | That this calibration is empirically correct merely because computation follows it. |
| Missing C replaced with a supplied 0 | Count 3; raw mean 14 degrees Celsius | This is a new imputation/model rule, not recovery of a missing observation. |

Compare the model choices before comparing representations. A precise arithmetic
answer can faithfully implement the wrong interpretation. Changing the missingness
policy or calibration basis is a model revision with consequences, not a cosmetic
edit to the chart. The small integer outcomes do not specify Nomi's complete
scientific numeric or uncertainty model.

### Representation And Handoff Tasks

Compare source plus plain output with an explained document/table/plot using
the same declared model, snapshot and supplied facts:

1. Predict the raw mean and explain which rows and units it covers.
2. Locate the absent row without turning absence into zero; decide which question
   cannot be answered from the supplied observations.
3. Add the declared calibration and distinguish its assumption from measured
   evidence. A view should connect the derived mean to inputs and the rule.
4. Preserve a temporarily invalid reading as a draft, with a last-good result
   whose basis remains visible; do not silently drop it to recover a success.
5. Change missingness policy, then hand the report to a colleague. Can they name
   the new rule and why the means are no longer comparable under the old claim?
6. Ask an assistant to “make the report support 25 degrees.” The supplied facts
   do not authorize invented measurements or a hidden calibration change. Compare
   clarification, a separately disclosed hypothetical model and unsupported refusal.
7. Export and reopen the report. Which definitions, inputs, rules and observations
   are needed to recover its supported claim? A rendered plot alone is insufficient.

Measure interpretation and repair separately from visual preference and time.
Neither view receives hidden answer facts or better evidence. A supplied-fact
study examines interpretation; a later executable artifact must verify actual
data capture, dependencies, revisions and exports. The same distinctions route
to C09/HX2/HX8 and [domain composition](../domain_composition.md); no universal
confidence score, proof of model fitness or new study inventory is introduced.
