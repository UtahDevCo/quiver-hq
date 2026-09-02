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

### Lead-off line (every PR comment)

Any comment Claude posts to a PR (review bodies, inline comments, thread replies)
MUST begin with the line `Uncle Claude has thoughts 👇`, then a blank line, then
the conventional-comment body:

```
Uncle Claude has thoughts 👇

**suggestion (non-blocking):** Extract this into a shared util so both callers reuse it.
```

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

---

## PR Description

Follow the repo PR template, but the top two sections are:

1. **`## AI;dr`** — leave this **blank**. Chris fills it in himself, in his own voice
   (the human tl;dr / "why I bothered" story). Never write content here.
2. **`## Claude Summary 👇`** — the machine-written summary (this replaces the old
   `## Summary` heading; include the 👇 emoji literally). Keep it concise — what
   changed and why, a few lines, no essay, no restating the diff.

Then the rest of the template (`## Testing and risk reduction`, screenshots,
`## Notes for reviewers`) and any codesmith footer, unchanged.

Skeleton:

```
## AI;dr

## Claude Summary 👇

<concise generated summary>

## Testing and risk reduction

…
```

Still hand the description back to Chris to finalize — he owns `AI;dr` and rewrites
the rest as needed.

**Make descriptions rich.** Use Markdown tables for structured info (before/after
values, per-state results, config matrices) directly in the body — tables are plain
text, no attachment needed. Attach screenshots and other media as visual evidence with
`--attach` (see below). A PR that touches UI or observable behavior should include
before/after screenshots.

---

## Screenshots & Attachments

**Canonical method: native `gh --attach`.** As of GitHub CLI **v2.99.0**, `gh` uploads
media directly — no extension, no browser cookie, no release-tag hack. This replaces the
old `gh-attach` extension workflow (`atani/gh-attach --release`, `sudosubin/gh-attach`,
manual `github.com/user-attachments/...` URLs). Do not use those anymore.

**Supported commands:** `gh pr create`, `gh pr edit`, `gh pr comment`, and the matching
`gh issue create` / `gh issue edit` / `gh issue comment`.

**Usage** — `--attach` is repeatable and takes a local path:

```bash
gh pr create --title "OUT-793 …" --body-file pr-body.md \
  --attach scratch/linear/<date>/<ISSUE-ID>-before.png \
  --attach scratch/linear/<date>/<ISSUE-ID>-after.png

gh pr comment <PR> --body "Repro + fix below" \
  --attach './login-error.png#Login error state before the fix'
```

- **Alt text**: append `#alt text` after the path — `--attach './x.png#the error state'`.
- **Reference in body**: a local path already written as `![alt](./x.png)` in the body
  is rewritten in place to the uploaded asset, so inline placement is preserved.
- **Supported types**: PNG, JPEG, GIF, WebP, SVG, MP4, MOV, WebM. Size caps: 10 MB
  images/GIFs; video 10 MB (Free) / 100 MB (paid).
- **Requires `gh >= 2.99.0`.** If `gh --version` is older, the flag is silently absent —
  bump `gh` (it's pinned in the nix flake) before relying on it.

**Screenshot discipline:**

- When doing click-through Chrome DevTools testing, capture screenshots as you go —
  before/after pairs for any UI or behavior change — and attach them as PR evidence so
  reviewers see the result without checking out the branch.
- Write screenshots to `scratch/` (or `scratch/linear/<date>/`), never into the repo
  tree. Do **not** commit screenshots or create a `.screenshots/` directory.
