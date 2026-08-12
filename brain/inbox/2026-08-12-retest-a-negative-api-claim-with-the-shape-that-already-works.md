---
type: workflow
title: Re-test a negative API claim with the request shape that already works elsewhere
description: "The API cannot do X" usually rests on one probe of one shape. Your own codebase often contains a successful call of the same family, and copying its verb, casing and parameter names is the cheapest falsification available.
kind: workflow
proposed_layer: meta
tags: [probing, api-integration, legacy-apis]
generated: { by: claude/opus-5, at: 2026-08-12T19:40:27Z }
status: draft
sources:
  - id: evidence
    resource: projects/wiley/web/scripts/probe-answerrule-enable.ts
    title: probe falsifying a create-only claim that four cards were built on
    last_modified: 2026-08-12
  - id: commit
    resource: projects/wiley
    title: commit d036fba, "falsify rules are create-only"
    last_modified: 2026-08-12
not:
  - term: "treat a recorded negative result as settled because it was measured once"
    why: "the measurement fixes a verb, a path shape, a casing and a set of parameter names, and a legacy API can reject all but one combination"
    instead: "before extending the workaround, re-run the probe using the shape a working call in the same codebase already uses"
---

# Observation

A negative capability claim gets recorded once and then quoted forever. It was
usually established by a single probe, and a probe fixes several choices at
once: HTTP verb, path shape, parameter casing, parameter names. On an older or
partitioned API, changing one of those can be the difference between refusal and
success.

The cheapest falsification is already in the repository. Find a call in the same
family that is known to work in production, and copy its shape exactly, aiming
it at the operation the claim says is impossible.

Also worth re-running the claim in the opposite direction. A claim measured
while turning something off has not been measured for turning it on, though it
will be quoted as though it had.

# Why it matters

A codebase carried "answering rules are effectively CREATE-ONLY on this
instance" in a comment, with four cards' worth of workarounds built on it:
customers were shown an error telling them their account needed manual repair in
a vendor portal, and a disable path resorted to narrowing a schedule window to
one minute because it believed it could not switch a rule off.

The original probe had sent `POST action=update&...&enabled=no`. The same
codebase ran `PUT action=Update&...&dnd_control=d` daily, successfully, from a
different function. Different verb, different casing, different parameter names.
Aiming the working shape at the operation believed impossible returned 202 and
the change read back.

A second route turned up in the same session from a status code that was not a
404: addressing the collection rather than the item, with the identifier in the
body, updated the record in place.

# Evidence

Five routes, one staged state, each verified by reading the record back rather
than trusting the response code:

    v1 PUT action=Update, enable=yes                WORKS
    v1 PUT action=Update, enable=yes + dnd_control  WORKS
    v2 PUT /answerrules/{name}                      404 AnswerRule not found
    v2 PUT /answerrules/{id}                        200, changed nothing
    v2 POST create again                            409 already used

Reading back mattered: the legacy endpoint answered 202 for every request tried,
including ones with invented parameter names that changed nothing.

Two things stayed true after the re-test. One field remained unwritable by any
route, so the claim was narrowed rather than deleted. And one route failed for a
single record while its siblings accepted the same call, so callers still verify
instead of trusting the response.
