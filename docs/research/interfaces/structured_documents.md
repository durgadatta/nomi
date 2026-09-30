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
