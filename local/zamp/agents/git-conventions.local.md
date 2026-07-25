---
name: Git Conventions
description: Branch naming, PR title, commit message, and review comment conventions for the Zamp monorepo. Reference this before creating branches, commits, or PRs, and when writing or interpreting review comments.
---

## Branch Naming

**Rule**: all lowercase, ticket prefix + number + slug, hyphen-separated.

**Regex** (enforced by CI in `.github/workflows/pr-linting.yml`):
```
^(eng|rev|cus|fil|pla|out|inn|tax)-\d+-[a-z\d-]+$
```

**Examples:**
- `out-793-my-filings-tab` ✓
- `inn-322-ai-csv-import` ✓
- `OUT-793-my-filings-tab` ✗ (uppercase prefix fails CI)

**Pro tip**: Copy the branch name directly from the Linear ticket — the button in Linear produces the correct lowercased slug automatically.

Valid prefixes: `eng`, `rev`, `cus`, `fil`, `pla`, `out`, `inn`, `tax`

---

## PR Title

**Regex** (enforced by CI):
```
^(ENG|REV|CUS|FIL|PLA|OUT|INN|TAX)-\d+ [A-Z]+(.*)? $
```

Uppercase prefix, space, then a title-cased description. No colon.

**Examples:**
- `OUT-793 Add My Filings tab to admin filing management page` ✓
- `INN-322 AI CSV Import Admin Upload` ✓
- `out-793 add my filings tab` ✗ (lowercase fails)

---

## Commit Messages

No strict CI enforcement, but convention from the codebase history:

**Simple change**: `TICKET-NNN Short imperative description`
```
OUT-793 Add My Filings tab to admin filing management page
```

**Typed change** (conventional commits style, for fixes/chores/etc.):
```
fix(OUT-793) Apply Prettier formatting to filters.client.tsx
```

Keep messages short. No periods at end. Imperative mood ("Add", "Fix", "Remove").

---

## Review Comment Style — Conventional Comments (canonical source)

This is the **single source of truth** for how we write review feedback and critique
comments. Every PR review, every inline comment, every thread reply, and any critique
Claude leaves MUST follow this format. See https://conventionalcomments.org.

### Format

```
<label> [decorations]: <subject>

[discussion]
```

- **label** — exactly one, from the table below. Lowercase.
- **decorations** — optional, in parentheses, comma-separated (e.g. `(blocking)`).
- **subject** — the actionable one-line message.
- **discussion** — optional body: reasoning, and ideally a concrete suggestion.

Render the label in bold when the target supports Markdown (GitHub does):
`**suggestion (non-blocking):** Extract this into a shared util so both callers reuse it.`

### Labels

| Label | Meaning | Blocks merge? |
|-------|---------|---------------|
| `praise` | Sincere positive callout — use it, at least once per review | No |
| `nitpick` | Trivial preference; inherently non-blocking | No |
| `suggestion` | Propose an improvement; state what and why | No (unless `(blocking)`) |
| `issue` | A specific problem with the change; pair with a suggested fix | **Yes** (unless `(non-blocking)`) |
| `todo` | Small necessary change before acceptance | Usually yes |
| `question` | Seeking clarification; may or may not require a change | Respond, not necessarily change |
| `thought` | Non-blocking idea that surfaced while reviewing | No |
| `chore` | Process task needed before acceptance (changelog, ticket, etc.) | Context-dependent |
| `note` | Non-blocking FYI the reader should notice | No |
| `typo` / `polish` / `quibble` | Expressive minor labels; treat like `nitpick` | No |

### Decorations

| Decoration | Meaning |
|------------|---------|
| `(blocking)` | Must be resolved before the PR can be accepted |
| `(non-blocking)` | Should not prevent acceptance |
| `(if-minor)` | Resolve only if the fix is trivial |

Default blocking-ness comes from the label (see table); a decoration overrides it.
An `issue` is blocking unless marked `(non-blocking)`; a `suggestion` is non-blocking
unless marked `(blocking)`.

### Applying labels when resolving *incoming* comments

- `issue` / `todo` (and any `(blocking)`) → fix in code before the next push.
- `suggestion` → apply if quick or clearly better; otherwise reply with the rationale.
- `question` → reply with an answer; only change code if the answer implies one.
- `nitpick` / `note` / `thought` / `praise` → optional; a brief acknowledging reply is fine.
