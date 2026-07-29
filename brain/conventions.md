---
type: Convention
title: How this brain works
description: Override resolution, local OKF extensions, trust and freshness policy, and the promotion gate for this bundle.
tags: [meta, spec, governance]
generated: { by: claude/opus-5, at: 2026-07-28T00:00:00Z }
verified:
  - { by: human:christopher, at: 2026-07-28T00:00:00Z }
status: stable
stale_after: 2027-07-28
sources:
  - id: okf-spec
    resource: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
    title: Open Knowledge Format v0.2
    author: team:google-cloud-knowledge-catalog
    last_modified: 2026-07-25
  - id: acme-sample
    resource: https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf/bundles/acme_retail
    title: acme_retail reference bundle
    author: team:google-cloud-knowledge-catalog
    last_modified: 2026-07-25
---

# What this is

This bundle is OKF v0.2 conformant. [^okf-spec] OKF gives us provenance
(`sources`), trust (`generated` / `verified`), lifecycle (`status`,
`stale_after`), and attested computations. It deliberately does **not**
give us inheritance or typed relationships, so this document defines those
three extensions locally.

Everything here is producer-defined and legal under OKF §4.1 ("Producers MAY
include any additional keys"). It is **not** portable to other OKF consumers.
If OKF later specifies inheritance or a runtime protocol, this is the surface
that needs reconciling.

# The two layers

`meta/` holds practices that apply everywhere. `projects/<name>/` holds
per-project knowledge plus **overrides** of the meta layer.

A practice belongs in `meta/` only when it is about *how Chris works*, not
*how one repo is built*. The test: would you want this applied to a brand-new
empty repo? If yes, it's meta.

Corroboration is the strongest signal. A practice that appears independently
in two or more repos is genuinely general. A practice seen once is
project-specific until proven otherwise, and belongs in
`projects/<name>/` with a `relations: [{kind: instance-of, ...}]` link if it
looks like it might generalize later.

# Extension 1: `Practice Override`

OKF has no inheritance. A project narrows, extends, replaces, or suspends a
meta practice with a concept of `type: Practice Override`:

```yaml
---
type: Practice Override
title: Comments — document exported types
overrides: /meta/practices/minimal-comments.md
mode: narrow
why: "CodeRabbit flags undocumented exported types in this repo."
generated: { by: human:christopher, at: 2026-07-28T00:00:00Z }
status: stable
---
```

- `overrides`: REQUIRED. A bundle-relative path to the meta concept being
  modified. A dangling `overrides` path is an audit failure, not a tolerated
  broken link — this is the one place we are stricter than OKF §6.1.
- `mode`: REQUIRED. One of:
  - `narrow` — the meta rule holds, with a documented carve-out.
  - `extend` — the meta rule holds, plus additional project requirements.
  - `replace` — the meta rule does not apply here; this one does instead.
  - `suspend` — the meta rule is knowingly not followed yet.
- `why`: REQUIRED. An override without a reason is indistinguishable from
  drift.
- `stale_after`: REQUIRED when `mode: suspend`. See below.

## Resolution

A consumer resolving practices for project P:

1. Load every concept in `meta/` whose `status` is not `deprecated`.
2. Load every `Practice Override` in `projects/P/overrides/`.
3. For each override, find the meta concept at its `overrides` path and
   compose by `mode`: `replace` wins outright; `narrow` and `extend` layer
   onto the meta rule and both are reported; `suspend` removes the meta rule
   from the effective set but is surfaced separately as a known gap.
4. Report anything stale (`today >= stale_after`) as advisory, never silently.

## Suspensions expire, by construction

`mode: suspend` MUST carry `stale_after`. When that date passes,
[`/brain-audit`](skills/brain-audit/SKILL.md) surfaces it as an expired
suspension. This is the whole reason to bother with `stale_after`: it turns
"we'll fix this later" into a dated commitment that comes back on its own
instead of quietly becoming the new normal.

# Extension 2: `relations:`

OKF links are untyped — the kind of relationship is "conveyed by the
surrounding prose" (§6.1). That makes the graph unqueryable, so concepts MAY
carry typed edges in frontmatter:

```yaml
relations:
  - { kind: supersedes, target: /projects/zamp/gems/rt-table.md }
  - { kind: instance-of, target: /meta/patterns/headless-table.md }
```

`kind` is one of `supersedes`, `superseded-by`, `depends-on`,
`conflicts-with`, `instance-of`, `generalizes`.

`relations` supplements body links; it does not replace them. Prose links stay
because they carry the *why*.

# Extension 3: `not:`

Borrowed from the OKF `acme_retail` reference bundle. [^acme-sample] Negative
knowledge is the highest-value thing to give an agent, because it blocks a
plausible wrong answer rather than merely suggesting a right one:

```yaml
not:
  - term: "Err(new Error('failed', { cause: result.error }))"
    why: "rewrapping hides the inner stack and cause chain"
    instead: "if (result.isErr()) return result"
```

Every entry needs all three keys. A `not:` without an `instead:` tells an
agent to stop without telling it where to go.

# Trust and provenance

Actors follow OKF §7:

| Actor | Meaning |
|---|---|
| `human:christopher` | Hand-authored or human-reviewed. |
| `claude/opus-5` | Written by a Claude session (model id as the version). |
| `process:brain-audit` | Machine re-confirmation by the audit skill. |

`generated.by` records who wrote the current content. `verified` records who
confirmed it. They are separate on purpose: an agent writes, a human confirms.

## `verified` is the promotion gate

**Only `human:christopher` may add a `verified` entry with a `human:` prefix.**
Agents MUST NOT self-verify. This is what makes the trust tier (OKF §5.3)
mean something: `machine-confirmed` genuinely means no human has looked at it.

Consequence: an agent's output lands in `inbox/` as `status: draft`. It becomes
`stable` with a human `verified` entry only via
[`/brain-promote`](skills/brain-promote/SKILL.md).

# Freshness policy

`stale_after` is an absolute date (OKF §5.5). Defaults by type:

| Concept type | Default `stale_after` |
|---|---|
| `Practice` | 1 year |
| `Stack` | 6 months — dependency choices move fast |
| `Pattern`, `Module` | 1 year |
| `Invariant` | the next dependency upgrade window |
| `Practice Override` with `mode: suspend` | 90 days, and never more than 1 year |
| `Decision` (ADR) | none — decisions are historical facts |

# Lifecycle: deprecate, never delete

When a practice changes, do **not** overwrite it. Set the old concept to
`status: deprecated`, add `relations: [{kind: superseded-by, target: ...}]`,
and keep the body explaining what changed and why. The reasoning behind a
reversal is usually more valuable than the rule itself, and it is exactly what
gets lost when a file is overwritten.

Deleting is reserved for things that were simply *wrong* — a hallucinated
practice, a misread of the code. Those leave a `log.md` entry and nothing else.

# Attestation

`type: Invariant` concepts carry an executable check, following OKF §10. The
runtime protocol is deferred by the spec (§12), so this bundle fixes its own
receipt shape:

```json
{ "command": "<the exact command run>", "exit_code": 0, "matches": [] }
```

An attester is deterministic code with no LLM in the loop. The generic
`expect_empty.py` fails the verdict when `matches` is non-empty. A failing
attestation MUST be surfaced, never silently dropped (OKF §11).

# Conformance notes

This bundle satisfies OKF §11: every non-reserved `.md` carries parseable
frontmatter with a non-empty `type`; `index.md` and `log.md` follow §8 and §9.

Two deliberate deviations:

1. A dangling `overrides:` path is an error here, not a tolerated broken link.
2. `skills/*/SKILL.md` files carry both `type: Skill` (for OKF) and
   `name`/`description` (for Claude Code skill discovery). They are concepts
   and tooling at the same time.

[^okf-spec]: Open Knowledge Format v0.2
[^acme-sample]: acme_retail reference bundle
