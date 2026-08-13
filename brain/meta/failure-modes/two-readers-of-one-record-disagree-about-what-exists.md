---
type: Failure Mode
title: Two readers of one record disagree about what exists
description: The matrix UI displayed Box L while the model reported it absent, because the bundle builder read normalizedK1.boxes and Box L lives on normalizedK1.recipient; a grep returned two readers and that count was the diagnosis.
tags: [llm, context-assembly, prompt-engineering, debugging, testing]
generated: { by: claude/opus-5, at: 2026-07-31T14:26:40Z }
status: stable
stale_after: 2027-08-13
relations:
  - { kind: depends-on, target: /meta/failure-modes/score-through-the-shipping-accessor.md }
sources:
  - id: bundle-builder
    resource: projects/k1/web/packages/db/src/project-query-reasoning.ts
    title: k1 reasoning bundle builder — extractK1Metrics reads only normalizedK1.boxes
    last_modified: 2026-07-31
  - id: fix
    resource: projects/k1 commit 98d32a3
    title: "fix(reasoning): put Box L and Box K in the evidence bundle"
    last_modified: 2026-07-31
  - id: prompt
    resource: projects/k1/web/packages/ai/src/project-query-reasoning.ts
    title: k1 REASONING_SYSTEM_PROMPT — TABLES section asked for a capital-contributions column
    last_modified: 2026-07-31
  - id: test
    resource: projects/k1/web/packages/ai/src/__tests__/project-query-reasoning-provider.test.ts
    title: assertions pinning the prompt to the field names the bundle ships
    last_modified: 2026-07-31
not:
  - term: "treating \"the model says the data is missing\" as a hallucination"
    why: "the model is reporting its payload accurately; the bug is upstream in assembly"
    instead: "grep the field name across the repo and count how many places read the record"
  - term: "reviewing the prompt and the payload builder in the same PR and calling that the check"
    why: "they drift independently afterward, and the next payload change has no reason to open the prompt"
    instead: "assert.match(prompt, /fieldName/) for every field the prompt names, and doesNotMatch for renamed ones"
---

# The trap

A model asked what it can see is describing the payload it was handed. It has no
other vantage point. So when a user points at a populated screen and the model
reports the same data as absent, both are right: the screen and the payload read
one record through different accessors, and only one of them was extended when
fields were added.

Diagnosis is mechanical. Grep the field name across the repo and count the readers.
Two readers of one record, one feeding a UI and one feeding a model, is the smell.
The UI is usually the correct one, because a human notices a blank cell immediately
and nobody notices an absent JSON key.

# Why it matters

The failure is invisible from both ends. The UI is correct, the model is honest, the
database has the data, and no error is raised anywhere. It surfaces only when a user
happens to ask the model about a field they can see on screen, and it presents as a
hallucination, which sends the investigation toward the prompt instead of toward the
twenty lines that build the payload. Cost scales with how long it hides: every answer
the model gave over that field's absence was wrong in a way that looked like a
reasoning limitation.

# Evidence

k1's analyst chat told a user "Box L (Partner's Capital Account Analysis ...) is not
present in the provided database bundle" while the matrix UI displayed Box L capital
contributions for the same documents.

The bundle builder:

```ts
const metrics = extractK1Metrics(normalizedK1.boxes as Record<string, unknown>)
```

Box L and Box K live on `normalizedK1.recipient`. The builder touched `recipient`
exactly once, for `recipient.name`. The matrix read the same normalized record the
other way:

```ts
getValue: (form: K1Form) => form.recipient[key as keyof typeof form.recipient]
```

`grep -rn "capitalBeginning"` returned two files, the matrix and its test. That count
was the diagnosis.

# The remedy: test that the prompt names the fields the payload ships

A prompt is a string. The compiler will not tell you it references a field the
payload never contains, and the model will not tell you either: it improvises a
plausible answer over the gap. Assert in a test that the prompt names the fields the
payload ships, and that it does not name fields renamed away. Pin the statement
rather than the phrasing, so the prompt can be reworded without silently losing the
contract:

```ts
assert.match(prompt, /capitalAccountOfThePartner/)
assert.doesNotMatch(prompt, /issuerName|recipientName/)
```

An instruction asking for something the data cannot supply is worse than silence,
because it invites invention. k1's prompt had a whole paragraph asking the model to
build a basis walk with a capital-contributions column, and the bundle had never
carried a capital-contributions figure. The model complied, populating the column
from whatever it could reach. Prompt v5's TABLES section had been unchanged since
before the bundle existed in its current form:

> "A basis walk, for example, should have one row per year ... plus one column for
> each item that raises or lowers basis (capital contributions and income increase
> it; distributions and losses decrease it)"

Two prior prompt revisions (v2, v3) were written against this same bundle without
anyone noticing, because nothing compared the two artifacts. The `doesNotMatch` half
catches the reverse drift, where a payload field is renamed and the prompt keeps
describing the old shape. The v4 note in the same file records that case:

> "a prompt describing issuerName/recipientName would now be describing a shape the
> model never sees — worse than silence, because it invites invention."
