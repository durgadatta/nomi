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
