---
type: Pattern
title: Render a signed artifact once, hash it, and content-address it
description: '"Capable of accurate reproduction" fails the moment a referenced record changes. Freeze the bytes, store the hash, pin the template version, and re-verify on a schedule.'
tags: [e-signature, immutability, hashing, storage, compliance, esign, ueta]
generated: { by: claude/opus-5, at: 2026-07-30T14:55:05Z }
status: stable
stale_after: 2027-08-13
not:
  - term: "renderAgreement(await db.query.contract.findFirst(...)) on each view"
    why: "the rendered document silently changes whenever any joined row changes, so what you can reproduce is no longer what was signed"
    instead: "render once from frozen columns via a pure function, store the bytes at a key derived from their own sha256, and compare on every subsequent read"
sources:
  - id: bma
    resource: "Broker Master Commission Purchase Program Agreement §16.2-16.3"
    title: "electronic records retained in a form capable of accurate reproduction; opportunity to print or download before accepting"
  - id: charter
    resource: projects/trikin/docs/trikin-capital/invariants.md
    title: "the invariant and its test strategy as written into the repo"
---

# The pattern

For any document a person signs, the thing that must survive is **the bytes they
saw**, and the data those bytes were derived from is a separate concern.

- `render()` is a **pure function** of a frozen row plus a pinned template version.
  No database access, no `Date.now()`, no locale- or timezone-dependent formatting,
  so no `toLocaleDateString` and no default number formatting. Byte-for-byte
  deterministic, and tested under a deliberately foreign `TZ`.
- Templates are **versioned files, never edited once used**. A wording change
  creates the next version; the record pins which version applies to it.
- The storage key is derived from the content's own hash (`.../{sha256}.html`). A
  re-render producing different bytes therefore writes a *different key* and the
  comparison fails loudly, instead of overwriting the evidence with something that
  merely looks similar.
- The hash is stored on the record too, and re-verified on read and on a schedule. A
  nightly job re-renders everything from frozen columns and compares.

Freezing the columns is the part most easily skipped. If the artifact references the
counterparty by join rather than by a value copied at signing, a later legal-name
correction changes what the document reproduces to.

# Why it matters

The legal standard is retention "in a form capable of accurate reproduction", and
the failure is silent by construction: regenerating from live data always succeeds
and always produces a plausible document. Nothing surfaces that it is no longer the
document that was agreed to. You discover it when a counterparty disputes a term and
the system confidently renders a version that supports neither party's recollection.

The engineering value generalises past compliance. This is the discipline that makes
a build reproducible, and the reason lockfiles pin hashes rather than ranges.
Content-addressing turns "did this change?" from a question requiring trust into one
requiring a comparison.

The timezone detail is worth stating because it is where determinism usually leaks: a
date formatted with the ambient locale renders differently on a machine in a
different region, so the hash of the "same" document differs by deploy target.

# Evidence

BMA §16.3 makes enforceability conditional on the signer having had "the opportunity
to print or download a copy of this Agreement **prior to** electronic acceptance",
which is also why serving that copy has to be recorded as an observed event rather
than assumed from the page having rendered a link.
