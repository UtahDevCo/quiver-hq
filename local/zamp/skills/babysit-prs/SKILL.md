---
name: babysit-prs
description: "Use when: driving your open PR stacks + free-standing PRs toward merge on a loop — monitoring CodeRabbit rounds, requesting the reviewer roster once CodeRabbit is quiet, running PR Resolve on incoming review comments, and reporting merge-readiness. Runs ONE sweep across ALL your authored PRs; drive repetition with `/loop /babysit-prs`. Gates on you for the two human calls: marking a PR ready (undraft) and merging."
argument-hint: "optional: a PR number or stack to scope the sweep to (default: all your open PRs)"
---

You are the **stack babysitter**. One invocation = **one sweep** across every open PR the user authored, grouped into stacks. You drive each stack's *bottom* PR toward merge-ready: wait out CodeRabbit, request the reviewer roster, run PR Resolve on incoming comments, and report. You do **not** undraft and do **not** merge — those are the user's calls. The `/loop` skill drives repetition (~10–15 min ticks).

## Ground truth — read before anything else

Every fact you report MUST trace to a real tool call you made THIS sweep. Never fabricate PR state, thread IDs, review decisions, or CodeRabbit activity.

- **Prefer `gh`/`git` over GitHub MCP tools** — deterministic and always present. If an MCP call returns empty, assume it's unavailable and fall back to `gh`; never invent a result.
- **No `jq`/`python3` on this box** (exit 127). Parse JSON with `gh`'s embedded jq via `--jq`, never a standalone `jq`.
- **On the first sign of tool trouble** (empty output, error, a thread ID that won't resolve) STOP that PR and report it. A partial sweep reported honestly beats a complete-looking one built on assumed output.
- A **no-op sweep is a valid result.** If nothing is actionable, say so and stop — don't manufacture activity.

## Policy (the rules this skill enforces)

**Stack shape — one PR reviewed at a time**
- Each stack's **bottom** PR (base = `main`, the trunk-most, and the one you've marked ready) is the **active** PR. A free-standing PR is its own bottom.
- Every PR **above** the bottom stays a **draft**. Do not request reviewers on drafts and do not solicit human review for them.
- If an upper PR is currently non-draft (violates one-at-a-time), **recommend** drafting it — do NOT convert it yourself. Draft-state changes are the user's call.

**CodeRabbit first, then humans**
- Whenever the active PR's base is instantiated or changed — a new bottom (previous bottom merged, next undrafted) or **any new push** to the active PR — CodeRabbit gets time to review before humans are pulled in. Pushes also dismiss stale approvals (ruleset), so don't churn needlessly.
- **CodeRabbit is "quiet"** when ALL hold: (a) its summary review is present for the current head SHA, (b) no new `coderabbitai`/`coderabbitai[bot]` comment in the last **~10 min**, and (c) it is not mid-re-review of the latest push. Until quiet, do not request human reviewers.

**Reviewer roster (request only on the active PR, only once CodeRabbit is quiet)**
- **Always:** `TroyRCampbell`, `BuiltByWalsh`, `sjsimpson`, `benefacto`, `hhinkezamp`.
- **`bressain` only when the design system is touched** — and then always. "DS touched" = the diff changes any CODEOWNERS path owned by `@bressain`: `utils/design-system/`, `utils/design-system-next/`, `utils/tailwind/`, `utils/ui/`, `tooling/eslint/kebab-case-exceptions.mjs`, or the app `postcss.config.cjs` / `tailwind.config.cjs` / `src/styles` entries. Confirm from the real changed-file list; CODEOWNERS auto-requests `bressain`+`BuiltByWalsh` on those paths, but request `bressain` explicitly so it's deterministic. Do NOT add `bressain` otherwise.
- Never request the author (the user) as a reviewer. The user leaves their own reviews independently.

**Respond to comments in the loop**
- On the active PR, run **PR Resolve** (`.claude/agents/pr-resolve.local.md`) each sweep to clear the current round of review threads (human + CodeRabbit), then commit + push so the fixes land and CodeRabbit re-reviews. Keep going across ticks until 0 unresolved actionable threads AND the merge gate is met.

**The two gates you never cross**
- **Never undraft** a PR (never `--ready`). When a next PR *should* come off draft, recommend it and stop.
- **Never merge.** When the bottom PR is merge-ready, recommend the merge + the next undraft, and let the user do both.

## Merge gate (authoritative — from the active `Branch Protection SOC2` ruleset)

A PR is **merge-ready** only when ALL of:
- **≥ 1 approving review** on the current head (approvals are **dismissed on push**, so a post-push cycle needs a fresh approval).
- **CODEOWNER approval** if the diff touches an owned path (DS ⇒ needs a `bressain`/`BuiltByWalsh` approval).
- **All review threads resolved** (`required_review_thread_resolution`).
- **`Check` status green** and the branch **up to date with `main`** (`strict` required status checks).
- Merge method is **squash** only.

Report readiness against this exact checklist — don't call a PR ready if any item is unmet.

## One sweep — the algorithm

### Step 0 — Preserve the user's working state
Note the current branch (`git rev-parse --abbrev-ref HEAD`) and whether the tree is dirty (`git status --porcelain`). You will check out PR branches to run PR Resolve; **restore the user's original branch at the end**, and never operate on a dirty tree you didn't create. If the tree is dirty with the user's own work, do PR Resolve work in a scratch worktree (`git worktree add`) instead of switching branches under them, or skip write-actions for that PR and report why.

### Step 1 — Enumerate stacks + free-standing PRs
Print the live picture, then get machine-readable state:
```sh
gh-stacks                      # human-readable forest of all your stacks (see bin/gh-stacks)
gh pr list --author @me --state open --limit 200 \
  --json number,title,headRefName,baseRefName,isDraft,reviewDecision,mergeStateStatus,statusCheckRollup
```
Group into stacks by base←head edges (a PR whose base is another of your heads is a child). Each root tree is a stack; the root is its **bottom**. A size-1 tree is a free-standing PR.

### Step 2 — Per stack, pick the active PR
The active PR = the **bottom** (root) PR **if it is non-draft**. If the bottom is a draft, there's nothing to solicit — note it and recommend the user undraft it to begin the cycle. Upper (non-bottom) PRs: leave draft; if non-draft, recommend drafting. You may still run PR Resolve on an upper draft's CodeRabbit comments to keep it clean, but never request human reviewers there.

### Step 3 — Per active PR, determine phase and act
For each active PR, establish the anchor (real changed-file list, head SHA, branch) the same way PR Resolve does, then:

1. **CodeRabbit phase.** Fetch reviews + comments (`gh pr view <n> --json reviews,comments,statusCheckRollup` and the reviewThreads GraphQL query PR Resolve uses). Determine quiet per the heuristic above.
   - **Not quiet / mid-review:** if a CodeRabbit round has already landed, run PR Resolve now to clear it (Step 4); otherwise just wait. Do NOT request human reviewers this tick.
   - **Quiet:** proceed to request reviewers (Step 3a) and handle any human/bot comments (Step 4).

2. **(3a) Request the reviewer roster** (only when quiet, only on the active PR). Compute the DS flag from the changed-file list, then:
   ```sh
   # base roster + bressain iff DS touched; skip anyone already a reviewer or the author
   gh pr edit <n> --add-reviewer TroyRCampbell,BuiltByWalsh,sjsimpson,benefacto,hhinkezamp
   # if DS touched:
   gh pr edit <n> --add-reviewer bressain
   ```
   Requesting an already-requested reviewer is a harmless no-op; still, read current reviewers first and only add the missing ones so the report is truthful. If a handle isn't a collaborator, note it rather than failing the sweep.

### Step 4 — Respond to comments (delegate to PR Resolve)
Invoke the **PR Resolve** agent on the active PR (via the Agent tool, `subagent_type: "PR Resolve"`, passing the PR number). It edits the working tree, replies to each thread in conventional-comments format, and resolves the threads it addressed — but it does **not** commit or push. After it returns:
- Review what it changed (`git status`, `git diff --stat`).
- If it changed files: run prettier on them, commit, and push so the round lands and CodeRabbit re-reviews:
  ```sh
  pnpm exec prettier --write <changed files>   # CI runs prettier --check
  git add -A && git commit -m "<conventional msg referencing the round>" && git push
  ```
  End the commit message with the `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` trailer.
- If it changed nothing (0 unresolved actionable threads): don't push.
- Never push a branch that isn't the active PR's head; verify identity first.

### Step 5 — Evaluate merge-readiness
Check the active PR against the **Merge gate** checklist above using real data (`reviewDecision`, `mergeStateStatus`, `statusCheckRollup`, and the resolved-thread count from GraphQL). Classify each active PR as: `waiting-on-coderabbit`, `awaiting-review`, `changes-in-flight`, `blocked-on-user` (needs undraft/merge), or `merge-ready`.

### Step 6 — Capture durable feedback
When a review round surfaces a **new, durable** convention or lesson (a reviewer rule you'll hit again, a repeated CodeRabbit false-positive worth pre-empting, a merge-gate gotcha):
- Append it to the **Zamp convention checklist** in `.claude/agents/pr-review.local.md` (match the existing sectioning + attribution style, e.g. "(bressain, OUT-890)").
- And/or write a memory file per the memory rules (feedback/project/reference), then add its one-line pointer to `MEMORY.md`.
Only capture what's genuinely reusable — skip one-off, PR-specific noise. Don't duplicate a rule already in `pr-review.local.md`.

### Step 7 — Restore + report
Restore the user's original branch (Step 0). Then print a compact per-stack report:

```markdown
# babysit-prs — sweep @ <UTC time>

## Stack: <bottom #> (base main)   [<phase>]
- Active: #<n> "<title>"  · CodeRabbit: <quiet|reviewing|none> · reviewers: <requested/missing> · gate: <met items / unmet items>
- Drafts above (left as-is): #<n>, #<n>
- Did this sweep: <requested X reviewers | ran PR Resolve: N fixed, M resolved, K left | pushed <sha> | no-op>
- ⛳ Needs you: <undraft #<n> | merge #<n> (squash) then undraft #<m> | nothing>

## Free-standing: #<n> ...

## Loop
- Suggest next tick in ~10–15 min (CodeRabbit re-review window). Stop when every active PR is `merge-ready` or `blocked-on-user`.
```

## Notes on driving the loop
- Kick off with `/loop /babysit-prs` (self-paced) — or `/loop 12m /babysit-prs` for a fixed cadence.
- Each sweep is idempotent: it only requests missing reviewers and only touches unresolved threads, so re-running is safe.
- The loop's job is done when there's nothing left but your two gated actions (undraft / merge). Surface those clearly every sweep so you can act between ticks.
