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
finished invoice or data report. This is a prepared comparison, not an executed
Nomi score, new API, fake-clock result or human study. It extends the existing
timing question without introducing a new global experiment ID.

### Fixed Starting Facts

Use two notes with distinct stable identities. Note A starts at beat 0; note B
starts at beat 1. Both last half a beat. The declared initial tempo is 120 beats
per minute with a constant beat-to-time mapping and no expressive timing.
The literal expectations below follow that supplied model:

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
