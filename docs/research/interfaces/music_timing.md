# Music And Timing: Choose The Clock

> Status: computer-music evidence and temporal-interface hypotheses.

## Evidence And Pressure

Miller Puckette's primary text distinguishes audio computations from control
streams and discusses conversions between them. This is the checked evidence
for the Pure Data thread; MIDI and score editors are additional probes, not
protocol implementations validated here.
[Audio/control text](https://msp.ucsd.edu/techniques/latest/book.pdf),
[Control streams](https://msp.ucsd.edu/techniques/latest/book-html/node43.html).

A score represents ordered intent; performance introduces tempo, scheduling,
latency, and physical time. A signal is not a list of events just because both
can be drawn as a line. A feedback edge requires temporal meaning, not merely
a graph cycle that happens to execute.

## Nomi Normal Form And Placement

Use explicit event, duration, instant, clock-domain, and signal values in a
library. Conversion declares sample/control rate, interpolation, buffering,
and failure policy. Ordinary `async` suspension does not promise real-time
deadlines; garbage collection and host scheduling remain profile constraints.

A timeline view can project events with stable IDs. Moving an event proposes
the same checked change as editing its time in source. Playback is an effectful
execution action with Stop, not a side effect of opening the score. A simulated
clock should be available without audio-device authority.

## Discriminating Experiment

Run a three-event score using a fake clock. Vary tempo, equal-time event order,
late arrival, Stop, and clock conversion. Compare trace and timeline while
checking identical event semantics. A useful playground experiment first shows
causality and timing without promising low-latency audio or hardware access.

## Creative Authoring Challenger — October 10

The [broader vision](../../design/vision.md) needs creation pressure beyond a
finished invoice or data report. The authoring comparison is prepared; the
[bounded model experiment](#bounded-model-experiment) now executes selected
schedule and revision cases. Neither executes a Nomi score, new API or device,
or supplies a human study. It extends the existing timing question without
introducing a new global experiment ID.

### Fixed Starting Facts

Use two notes with distinct stable identities. Note A starts at beat 0; note B
starts at beat 1. Both last half a beat. The declared initial tempo is 120 beats
per minute with a constant beat-to-time mapping and no expressive timing.
The literal expectations below follow that supplied model:
they are reviewer oracles, withheld until initial predictions are recorded for
tasks that ask the person to calculate the result.

| Model revision | A starts / ends | B starts / ends |
| --- | --- | --- |
| 120 beats/minute | 0 / 250 milliseconds | 500 / 750 milliseconds |
| 60 beats/minute, beat positions retained | 0 / 500 milliseconds | 1000 / 1500 milliseconds |

An absolute-time model initially set to 0/250 and 500/750 milliseconds has
different change semantics: changing tempo metadata alone does not move those
events. Compare the models explicitly before comparing views. Neither is the
intended interpretation merely because its timeline looks familiar.

### Creation, Explanation And Change

Compare source, structured event editing and a mixed timeline/source environment.
Give them the same beat-based model, rules and supplied diagnostics. A textual
fallback is one candidate interoperability route; a structured candidate must
also expose its saved meaning and change history.

1. Construct a different short pattern, then explain event identity, onset,
   duration and the tempo mapping. Record independently created outcomes rather
   than only whether someone copied the supplied pattern.
2. Predict the result of changing tempo to 60 before revealing the second row.
   Ask what would change under the absolute-time alternative separately.
3. Preserve an unfinished duration such as `1/` as a draft. Compare last-good
   inspection with a deliberately defined partial-model candidate. Neither may
   silently guess the intended duration or play that guess.
4. Request “make the second note slower.” Distinguish a later onset, longer
   duration and lower global tempo; retain the question when the goal is ambiguous.
5. Prepare a timeline edit under the old tempo, then change tempo before commit.
   The update must identify its base and intended coordinate domain. Revalidation
   or refusal needs explanation; pixel position alone cannot determine meaning.
6. Hand the model to another person, including a deliberate change from beat
   anchoring to absolute anchoring. Can they identify the new rule and its effect
   on future tempo edits, rather than only the changed display?
7. Inspect supplied playback records, edit the next revision and stop an active run.
   Recorded sound/event evidence, proposed schedule and acknowledged device
   actions stay distinct. An unavailable acknowledgment leaves the remote action
   unknown; source undo cannot reverse emitted sound.

Use a simulated clock for semantic preparation. An actual device trial measures
scheduling and latency on a declared host separately.
Evaluate keyboard and assistive access to identity, ordering and duration when
actual views exist; a written requirement is not accessibility evidence.

### What Can Change Nomi

Compare prediction, creation, repair and handoff before time or preference.
Record the costs of working with temporal concepts through ordinary source and
through a domain representation. Repeated difficulty may justify changes to
the library model, inspection surface, primary authoring representation or scoped
notation. The result must be allowed to challenge the architecture, while no
prepared answer here settles real-time behavior or representation superiority.

## Bounded Model Experiment

From a repository checkout, run:

```bash
python3 -m tools.creative_timing_experiment --check
python3 -m tools.creative_timing_experiment --case late-run-keeps-old-basis
pytest -n 0 prototype/tests/unit/tools/test_creative_timing_experiment.py
```

The standard-library [driver](../../../tools/creative_timing_experiment.py)
compares selected observations with independently written literal expectations
in [timing_cases.json](timing_cases.json). The
[tests](../../../prototype/tests/unit/tools/test_creative_timing_experiment.py)
also challenge empty selections, unknown paths, lost run identity and host
boolean/number coercion. The [experiment receipt](experiments.md#creative-timing-model)
owns the case inventory. No generated outcome capture replaces the expectations.
Checking is non-writing; a mismatch returns failure. An unknown case or malformed
fixture is an error, rather than an empty successful check.

### Declared Profile

- Onsets, durations and tempo are exact rational numbers supplied as integer
  numerator/positive-denominator pairs. Onsets are nonnegative; durations and
  tempo are positive. This does not choose Nomi's scalar system or draft codec.
- Beat coordinates scale by tempo; millisecond coordinates do not. Equal-time
  events use the laboratory rule off before on, then note identity. Neither
  this tie rule nor rejecting zero-duration notes is a music/device standard.
- A note change names the model incarnation, revision, coordinate basis, stable
  note identity and field. The serialized owner rejects a stale or mismatched
  base. Invalid field values remain raw drafts beside the unchanged model,
  retaining their original incarnation, revision and coordinate basis after reset.
- A reset supplies a distinct incarnation; this driver refuses previously used
  incarnations within the case. Supplied tokens do not establish authenticated
  identity, global fork history or an atomic concurrent publication operation.
- A run captures a model snapshot. Advancing its monotonic simulated clock
  records each due event once; opening an inspection does not advance it.
  Editing the model does not replace a retained run's basis or revision.
- Stop prevents later local delivery. It does not synthesize note-off events or
  establish device cleanup. Records expose unclosed note identities and whether
  all planned events were delivered; the external outcome remains unobserved.

The ambiguous-request case supplies an ambiguity label; it does not understand
natural language. The observations expose the Python host version and explicitly
exclude Nomi, device, concurrent and human execution. A deterministic delivery
record is neither real-time scheduling nor evidence that a person understands it.

### What The Model Changes And Leaves Open

Equal initial schedules do not establish equivalent change rules: beat and
absolute-time models diverge after a tempo edit. A late run can finish delivering
its old schedule without becoming evidence about the current revision. A stopped
run can retain an unmatched note-on. These distinctions sharpen model selection,
revision inspection and the Stop contract before an interface comparison.

Strict stale-base refusal is one candidate. Selective revalidation or an explicit
coordinate conversion may be better; those alternatives are not executed here.
The next discriminator starts with B's proposed onset at half a beat under
120 beats/minute, then changes tempo to 60 before commit. Repreparing the beat
intent gives a 500-millisecond onset. Preserving the original 250-millisecond
onset requires a quarter-beat coordinate. Strict refusal publishes neither.
These preserve different intentions; a revalidator cannot choose from pixels or
the new tempo alone. Compare explicit intent/basis policies and their read sets.
Last-good inspection versus typed partial programs, tie policy, schedule ownership,
overlapping voices and acknowledged release remain open. Source, structured and
mixed authoring views still require actual construction, matched tasks and people.
