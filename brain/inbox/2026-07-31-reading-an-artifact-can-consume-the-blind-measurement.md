---
type: Observation
title: A debugging read can consume the blind measurement it was built to serve
description: A status probe that scraped the verdict off the page would have destroyed blindness for every case before the human labeller opened one, and nothing would have recorded that it happened.
kind: failure-mode
proposed_layer: meta
observed_in: k1
tags: [evaluation, blinding, observability, measurement, human-labelling]
status: draft
not:
  - term: "scrape the whole result card to check whether a run finished"
    why: "the card carries the verdict, so the act of polling reveals the answer the human is supposed to label independently — and a revealed label is unrecoverable without regenerating the case"
    instead: "probe only the field that answers the question (member count, busy state), and give the debugging path its own read-only script that prints no verdict"
generated: { by: claude/opus-5, at: 2026-07-31T13:31:08Z }
sources:
  - { id: show-run, resource: "projects/k1/web/scripts/show-panel-run.ts:1-6", title: "read-only inspector, documented as unable to consume a label" }
  - { id: captured-blind, resource: "projects/k1/web/packages/db/src/panel-label-export.ts:17", title: "capturedBlind — a label taken with the verdict on screen is kept but excluded from the gate" }
  - { id: dev-flight, resource: "projects/k1/web/apps/web/app/[tenantSlug]/projects/[projectId]/panel-runs", title: "the dev RSC flight stream carries the verdict in an orphan chunk, so localhost cannot be used for blind labelling at all" }
---

# Observation

A gate that requires human judgement requires the human not to have seen the
machine's answer first. That makes every read of the artifact a potential
expenditure, including reads whose purpose has nothing to do with labelling.

Two ways it nearly went wrong here, both while automating the generation of cases
rather than while labelling them:

A polling probe, written to answer "has this run finished", captured the result
card. The card contains the verdict chip. Running it across the queue would have
revealed the answer for every constructed case before the labeller opened the
first one, and the labels would still have been recorded as blind because nothing
in the system can tell that an agent read the page.

Separately, localhost turns out to be unusable for blind labelling regardless of
care taken in the UI: the development RSC flight stream ships the verdict in an
orphan chunk, so the value is in the page source even when no component renders
it.

# Why it matters

Blinding failures are silent and they do not reverse. `capturedBlind` exists to
mark a label taken with the verdict on screen, and such labels are kept but
excluded from the gate set. That control only works for reveals the *application*
performs. A probe reading the DOM out of band, or a developer reading the database
to debug, leaves the flag saying `true`.

So the design rule is that the debugging path needs its own reader that is
structurally incapable of revealing the measured value, and the polling path needs
to request the narrowest field that answers its question. Both are cheap to build
before the labelling starts and impossible to retrofit after.

The concrete instance: one verdict was seen and withheld from the report, and the
probe was rewritten to return a member count only.

# Evidence

The header the read-only inspector carries, stating the constraint as its reason
for existing:

```ts
// Read-only. It does not reveal or record anything through the UI, so it cannot
// consume the blind-labelling gate a run is waiting on (PRD 17 M4) — which is the
// point: inspecting a run to debug it must not spend a label.
```
