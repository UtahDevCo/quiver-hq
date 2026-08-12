---
type: Failure Mode
title: A probe that an API cannot do X needs a positive control, or absence proves nothing
description: Without seeding a value and proving it landed, "the thing is gone" and "the thing was never there" are the same reading, and the probe certifies a limitation it never demonstrated.
tags: [third-party-apis, verification, probes, controls, debugging]
generated: { by: claude/opus-5, at: 2026-08-12T14:25:42Z }
verified:
  - { by: human:christopher, at: 2026-08-12T19:34:21Z }
status: stable
stale_after: 2027-08-12
relations:
  - { kind: depends-on, target: /meta/failure-modes/probe-before-trusting-an-api-claim.md }
  - { kind: depends-on, target: /meta/failure-modes/verify-a-write-actually-happened.md }
sources:
  - id: probe
    resource: projects/wiley/web/scripts/_probe-allowlist-removal-matrix.ts
    title: wiley — allow-list removal matrix, ten forms against a seeded fixture
    last_modified: 2026-08-08
  - id: fix
    resource: projects/wiley
    title: "wiley 60d9eb8 — fix(netsapiens): delete the allow-list replace paths the API never had"
    last_modified: 2026-08-08
not:
  - term: "try the removal, read the list, conclude it cannot remove"
    why: "if the target was never present, or the read path cannot see it, every removal form 'succeeds' at leaving it absent and the probe reports a limitation on evidence that would look identical if the API worked perfectly"
    instead: "seed a distinctive value, read it back and assert it is there, and abort the probe if that step fails"
  - term: "reusing a value already on the list as the removal target"
    why: "you cannot tell your seed from pre-existing data, so a partial success is unattributable"
    instead: "a value chosen to be unique to this probe, so its presence and absence are both attributable"
  - term: "a 2xx on the seed write is proof the seed landed"
    why: "six of ten forms in this probe returned 202 Accepted while changing nothing"
    instead: "read the value back through the same path the probe will use to observe its absence"
---

# The trap

Before probing whether an API can remove, clear, or overwrite something, seed a
distinctive value and prove it landed. Then attempt the removal. Abort if the seed
step fails.

The seed is the positive control. It establishes that the write path works, that
the read-back path can see what the write path produces, and that the target was
present at the moment the removal was attempted. Skip it and a negative result has
two explanations that the evidence cannot separate: the API cannot remove the
thing, or the thing was never there for it to remove.

This is not the same as probing the claim at all, which
[probe before trusting an API claim](probe-before-trusting-an-api-claim.md) already
covers. That concept gets you to run the probe. This one is about whether the probe
you ran could have come out the other way.

# Why it matters

A probe is usually written to decide whether to keep a workaround. A false
confirmation is therefore expensive in a specific way: it converts an untested
comment into a *measured* comment, with a date and a committed script, and the next
reader is right to trust it more. The failure mode upgrades the confidence without
touching the correctness.

In wiley the conclusion happened to be true, and the control still earned its
place. Ten removal forms all reported "no effect". That sentence means something
only because the probe had already printed `CONTROL PASSED` on the line above it.
Had the seed silently failed, the same ten lines would have been produced by an API
that removes flawlessly, and the recommended action, an external batch-clear
request to a vendor, would have been raised against a capability that existed.

The read-back path is the part most likely to betray you, because it is easy to
assume. Here the v2 `GET` on the same endpoint that accepts allow-list writes does
not return the allow list at all: it reports only `phone-numbers-to-reject`. A
probe that wrote through v2 and read back through v2 would have observed every
seeded number as absent immediately, then observed every removal as a success.

# Evidence

The control, and the refusal to continue without it:

```ts
console.log(`  POST  → ${await attempt("POST", NF, { "phone-numbers-to-allow": { parameters: [PROBE_NUMBER] } })}`);

const seeded = await readList();
if (!seeded.includes(PROBE_NUMBER)) {
    console.error(`\nABORT: the control add did not land. Nothing below would be interpretable.`);
    process.exit(2);
}
console.log(`  CONTROL PASSED: an add is visible through this read path, so a disappearance means something.`);
```

A pre-flight assertion that the seed is not already present, so its later absence
is attributable to the removal rather than to the fixture:

```ts
if (baseline.includes(PROBE_NUMBER)) {
    console.error(`\nABORT: ${PROBE_NUMBER} is already present, so a later "it is gone" reading would be ambiguous.`);
    process.exit(2);
}
```

Each form's verdict was then computed against both the target and the survivors, so
an endpoint that emptied the whole list was recorded as destructive rather than as
a success:

```ts
if (probeGone && survivorsKept) verdict = "REMOVED THE TARGET";
else if (probeGone && after.length === 0) verdict = "DESTRUCTIVE: emptied the whole list";
```

Ten forms, zero removals, and six of them returned `202 Accepted` while changing
nothing, which is why the status code could not have served as the control.

Related: [probe before trusting an API claim](probe-before-trusting-an-api-claim.md)
(probe the claim; this is how to make the probe falsifiable),
[probe inputs must make outcomes distinguishable](probe-inputs-must-make-outcomes-distinguishable.md)
(the same probe's other defect),
[verify a write actually happened](verify-a-write-actually-happened.md),
[audits must report their own coverage](audits-must-report-their-own-coverage.md).
