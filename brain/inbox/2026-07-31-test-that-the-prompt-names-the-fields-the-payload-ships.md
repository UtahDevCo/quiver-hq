---
type: Observation
title: Test that the prompt names the fields the payload actually ships
description: Nothing type-checks a prompt against its data, so a prompt can ask for a column the payload has never carried and stay wrong for months.
kind: practice
proposed_layer: meta
tags: [llm, prompt-engineering, testing]
generated: { by: claude/opus-5, at: 2026-07-31T14:26:40Z }
status: draft
sources:
  - id: evidence
    resource: projects/k1/web/packages/ai/src/project-query-reasoning.ts
    title: k1 REASONING_SYSTEM_PROMPT — TABLES section asked for a capital-contributions column
    last_modified: 2026-07-31
  - id: test
    resource: projects/k1/web/packages/ai/src/__tests__/project-query-reasoning-provider.test.ts
    title: assertions pinning the prompt to the field names the bundle ships
    last_modified: 2026-07-31
not:
  - term: "reviewing the prompt and the payload builder in the same PR and calling that the check"
    why: "they drift independently afterward, and the next payload change has no reason to open the prompt"
    instead: "assert.match(prompt, /fieldName/) for every field the prompt names, and doesNotMatch for renamed ones"
---

# Observation

A prompt is a string. The compiler will not tell you it references a field the
payload never contains, and the model will not tell you either: it will improvise
a plausible answer over the gap. Assert, in a test, that the prompt names the
fields the payload actually ships, and that it does not name fields that were
renamed away.

Pin the statement rather than the phrasing, so the prompt can be reworded but not
silently lose the contract:

```ts
assert.match(prompt, /capitalAccountOfThePartner/)
assert.doesNotMatch(prompt, /issuerName|recipientName/)
```

# Why it matters

An instruction that asks for something the data cannot supply is worse than
silence, because it invites invention. k1's prompt had an entire paragraph asking
the model to build a basis walk with a capital-contributions column, and the
bundle had never carried a capital-contributions figure. The model complied by
producing walks with the column populated from whatever it could reach.

The `doesNotMatch` half catches the reverse drift: a field gets renamed in the
payload and the prompt keeps describing the old shape, so the prompt is now
documenting a structure the model never sees.

# Evidence

k1 prompt v5. The TABLES section, unchanged since before the bundle existed in its
current form:

> "A basis walk, for example, should have one row per year ... plus one column for
> each item that raises or lowers basis (capital contributions and income increase
> it; distributions and losses decrease it)"

`extractK1Metrics` had never emitted a contributions figure — Box L lives on a
part of the record the bundle builder did not read. Two prior prompt revisions (v2,
v3) had been written against this same bundle without anyone noticing, because
nothing compared the two artifacts.

The v4 note in the same file records the mirror-image case, where the payload's
field names changed and the prompt had to be chased to match:

> "a prompt describing issuerName/recipientName would now be describing a shape the
> model never sees — worse than silence, because it invites invention."
