---
name: brain-audit
description: Health check the brain — run invariant attesters, and surface stale, unverified, deprecated-but-linked, and structurally broken concepts. Use when the user says "audit the brain", "is the brain healthy", "check the brain", or asks what practices need review. Read-only; reports but never edits.
type: Skill
---

# brain-audit

Find the parts of the brain that stopped being true. This is the immune system —
without it a knowledge base rots silently and confidently.

**Read-only.** Report findings; never fix them. Fixing is `/brain-promote`'s job,
with Chris in the loop. The one exception is noted under *Attestation*.

## Checks

Run all of these over `~/dev/quiver-hq/brain/`.

### 1. Stale

Any concept where `today >= stale_after`. Group by how overdue. A practice
three months past review is a different problem from one a day past.

### 2. Expired suspensions — highest priority

`Practice Override` with `mode: suspend` and `stale_after` in the past. The
project is knowingly out of compliance with a meta practice **and** the
commitment to revisit has lapsed. Report these first, always, with the `why` and
the original date.

This is the check that justifies the whole `stale_after` mechanism. Everything
else is hygiene; this is a broken promise.

### 3. Unverified

Concepts outside `inbox/` with no `verified` entry, or verified only by non-`human:`
actors. These are `machine-confirmed` at best — an agent wrote them and no human
ever confirmed. Anything in `meta/` that is unverified is a real problem, because
it is being applied to every project on an agent's word.

### 4. Structural

**Parse YAML frontmatter only.** `conventions.md` and the skill files contain
illustrative `relations:` / `overrides:` examples in prose and fenced code blocks
(`/meta/patterns/headless-table.md`, `/path/to/new.md`). A naive `grep` for
`target:` across the bundle reports all of those as broken. Read the frontmatter
block, ignore the body.

- **Dangling `overrides:`** — a `Practice Override` pointing at a nonexistent
  path. An error, not a tolerated broken link (`brain/conventions.md`). The
  override is silently doing nothing.
- **Orphaned `relations:`** — a `target` that doesn't exist.
- **Body links** — resolve every relative markdown link in every body against the
  filesystem. Two failure shapes: a genuinely missing file, and a *bundle-absolute*
  path (`/meta/practices/x.md`) used where a relative one belongs — that one looks
  correct and resolves nowhere. Skip `skills/*/SKILL.md`, whose bodies contain
  illustrative links like `[Title](file.md)` by design.
- **Wikilinks** — `[[name]]` is the auto-memory format, not OKF. Its presence means
  an observation was hand-written into the bundle and promoted without conversion.
- **Asymmetric relations** — `supersedes` without a matching `superseded-by`.
- **Deprecated but referenced** — a `status: deprecated` concept still linked
  from a non-deprecated one, or still listed in an `index.md` without being
  marked deprecated. This is how retired practices get re-applied.
- **Missing from the meta index** — a concept in `meta/` absent from
  `brain/meta/index.md`. It is invisible to every session.
- **Conformance** (OKF §11) — a non-reserved `.md` with unparseable frontmatter
  or an empty `type`.
- **Inbox age** — observations older than ~30 days. The inbox is a queue, not
  storage; a backlog means harvest is outrunning promotion.

### 5. Attestation

For every `type: Invariant` concept with a `computation`:

1. Read the computation from its `# Computation` fence or `computation:` path.
2. Execute it via the skill at `executor.resource`.
3. Assemble the receipt exactly as `executor.receipt` declares. This bundle's
   shape is fixed in `brain/conventions.md`:
   ```json
   { "command": "<exact command run>", "exit_code": 0, "matches": [] }
   ```
4. Hand the receipt to `attester.resource` and report the verdict.

**Never modify a computation to make it pass.** If it errors, report
"sanctioned check failed to run" — which is a distinct finding from "the check
ran and the invariant is violated." Conflating those two hides real breakage.

**Surface every failing attestation** (OKF §11 requires this). A failing
invariant means the codebase drifted from a rule the brain claims it follows —
one of the two is now wrong, and that is the single most actionable thing this
skill produces.

The one permitted write: on a **passing** attestation, you may append
`verified: { by: process:brain-audit, at: <now> }` to that invariant. That is
machine re-confirmation, not human sign-off, and it is what keeps freshness
honest without Chris re-reviewing checks a machine can prove.

## Report

Ordered by actionability, not by check number:

```
## Broken promises
   expired suspensions — project, practice, why, days overdue

## Failing invariants
   invariant, project, what drifted, the receipt

## Needs review
   stale concepts — grouped by overdue duration
   unverified meta concepts

## Structural
   dangling overrides, orphaned relations, deprecated-but-linked, index gaps

## Queue
   inbox depth and oldest item
```

Every line cites a `brain/...` path.

**If everything passes, say so in one line.** Do not pad a clean audit into a
report — the value of this skill is that a short output means "healthy."

End with the single most important thing to do next, or state that nothing needs
attention.
