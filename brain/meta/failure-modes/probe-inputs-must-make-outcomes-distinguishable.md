---
type: Failure Mode
title: Choose probe inputs so every candidate outcome produces a different reading
description: A probe whose input is already in the target state collapses two behaviours into one observation, and "no effect" gets read as the stronger of the two.
tags: [third-party-apis, verification, probes, experiment-design, debugging]
generated: { by: claude/opus-5, at: 2026-08-12T14:25:42Z }
verified:
  - { by: human:christopher, at: 2026-08-12T19:34:21Z }
status: stable
stale_after: 2027-08-12
relations:
  - { kind: depends-on, target: /meta/failure-modes/probe-before-trusting-an-api-claim.md }
  - { kind: depends-on, target: /meta/failure-modes/request-parameters-may-not-reach-the-wire.md }
sources:
  - id: probe
    resource: projects/wiley/web/scripts/_probe-put-vs-post.ts
    title: wiley — PUT vs POST on number-filters, using a value not already present
    last_modified: 2026-08-08
  - id: first-probe
    resource: projects/wiley/web/scripts/_probe-allowlist-removal-matrix.ts
    title: wiley — the matrix whose inputs restated values already on the list
    last_modified: 2026-08-08
  - id: fix
    resource: projects/wiley
    title: "wiley 60d9eb8 — deleting a repair step that was the other repair step renamed"
    last_modified: 2026-08-08
not:
  - term: "probe a replace by sending the list you want to end up with"
    why: "if the API appends, the result is identical to a correct replace whenever your input is a superset of what is there, so the strongest and weakest possible behaviours produce the same bytes"
    instead: "send a value that is NOT currently present, so append, replace and no-op each produce a different list"
  - term: "reading 'no effect' as 'the verb is unsupported'"
    why: "no effect against an input already satisfied is the expected result for every implementation, including a fully working one"
    instead: "before believing a negative, ask which other behaviours would have produced this same reading"
---

# The trap

When probing what an operation does, pick inputs such that each behaviour you are
trying to distinguish yields a different observable result. Enumerate the candidate
behaviours first, then choose the input that separates them.

The trap is an input that is already satisfied. Sending the state you want as the
state you request means a no-op, an append, and a correct replace can all leave the
store byte-identical. The probe runs, reports cleanly, and has measured nothing.

# Why it matters

The reading you get in this situation is "no effect", and "no effect" is easy to
over-read as "the verb is not supported". It is weaker than that. It is consistent
with unsupported, with supported-and-already-satisfied, and with
supported-but-silently-partial. Acting on the strongest interpretation is how a
probe becomes the justification for deleting a code path that was doing something,
or for keeping one that was not.

In wiley the first probe tried ten allow-list removal forms, and every form restated
numbers already on the list. All ten reported "no effect", which was correct and
insufficient: it could not separate *PUT appends* from *PUT does nothing at all*.
Those two imply opposite things about the repair code. If PUT is inert, the repair
path is dead weight. If PUT appends, the repair path is the additive sync under a
different name, printing "PUT replace succeeded" for an operation that has never
replaced anything.

A second probe sending a number that was not present settled it in one line each,
and that distinction is what justified deleting a step rather than merely
relabelling it. The generalized question, worth asking before believing any negative
result: *which other behaviours would have produced this same reading?*

# Evidence

The first matrix, whose inputs could not discriminate. `baseline` is by construction
already on the list:

```ts
{ label: "v2 PUT number-filters with the survivors only",
  run: () => attempt("PUT", NF, { "phone-numbers-to-allow": { parameters: baseline } }) },
```

The follow-up, stating the ambiguity and choosing inputs that break it. Each verb
gets its own number, and neither is present beforehand:

```ts
const VIA_PUT = "18885550471";
const VIA_POST = "18885550472";

for (const n of [VIA_PUT, VIA_POST]) {
    if (before.includes(n)) {
        console.error(`\nABORT: ${n} is already present, so its appearance would prove nothing.`);
        process.exit(2);
    }
}
```

The three-way verdict, so each candidate behaviour has somewhere distinct to land:

```ts
if (putAppended && putPreservedOthers && postAppended) {
    // PUT and POST are the same operation: append-and-dedupe.
} else if (putAppended && !putPreservedOthers) {
    // PUT IS A REAL REPLACE. The card's premise is wrong.
} else if (!putAppended) {
    // PUT is inert: returns 2xx and writes nothing. Weaker than POST, not equal to it.
}
```

Result: both verbs appended and both preserved the existing entries, so `--repair`'s
first step was its second step with a name that promised a replace. Both were
deleted.

Related: [a capability probe needs a positive control](a-capability-probe-needs-a-positive-control.md)
(the same probe's other defect),
[probe before trusting an API claim](probe-before-trusting-an-api-claim.md),
[request parameters may not reach the wire](request-parameters-may-not-reach-the-wire.md).
