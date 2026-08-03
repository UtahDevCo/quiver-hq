---
type: Observation
title: A model's account of what it can see describes the payload, not the database
description: When a user insists data exists and the model insists it cannot see it, both are usually right — count the readers of the record.
kind: failure-mode
proposed_layer: meta
tags: [llm, context-assembly, debugging]
generated: { by: claude/opus-5, at: 2026-07-31T14:26:40Z }
status: draft
sources:
  - id: evidence
    resource: projects/k1/web/packages/db/src/project-query-reasoning.ts
    title: k1 reasoning bundle builder — extractK1Metrics reads only normalizedK1.boxes
    last_modified: 2026-07-31
  - id: fix
    resource: projects/k1 commit 98d32a3
    title: "fix(reasoning): put Box L and Box K in the evidence bundle"
    last_modified: 2026-07-31
not:
  - term: "treating \"the model says the data is missing\" as a hallucination"
    why: "the model is reporting its payload accurately; the bug is upstream in assembly"
    instead: "grep the field name across the repo and count how many places read the record"
---

# Observation

A model asked what it can see is describing the payload it was handed. It has no
other vantage point. So when a user points at a populated screen and the model
reports the same data as absent, the likely fault is that the screen and the
payload read the same record through different accessors, and only one of them was
extended when fields were added.

Diagnosis is mechanical: grep the field name across the repo and count the
readers. Two readers of one record, one feeding a UI and one feeding a model, is
the smell. The UI is usually the one that is right, because a human notices a
blank cell immediately and nobody notices an absent JSON key.

# Why it matters

The failure is invisible from both ends. The UI is correct, the model is honest,
the database has the data, and no error is raised anywhere. It surfaces only when
a user happens to ask the model about a field they can see on screen, and it
presents as a hallucination, which sends the investigation toward the prompt
instead of toward the twenty lines that build the payload.

Cost scales with how long it hides: every answer the model gave over that field's
absence was wrong in a way that looked like a reasoning limitation.

# Evidence

k1's analyst chat told a user "Box L (Partner's Capital Account Analysis ...) is
not present in the provided database bundle" while the matrix UI displayed Box L
capital contributions for the same documents.

The bundle builder:

```ts
const metrics = extractK1Metrics(normalizedK1.boxes as Record<string, unknown>)
```

Box L and Box K live on `normalizedK1.recipient`, not `normalizedK1.boxes`. The
builder touched `recipient` exactly once, for `recipient.name`. The matrix read
the same normalized record the other way:

```ts
getValue: (form: K1Form) => form.recipient[key as keyof typeof form.recipient]
```

`grep -rn "capitalBeginning"` returned two files: the matrix and its test. That
count was the diagnosis.
