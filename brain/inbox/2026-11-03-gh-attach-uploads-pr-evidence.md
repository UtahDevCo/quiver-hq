---
type: Observation
title: Post screenshots and screencasts to a PR with gh --attach
description: gh 2.103+ uploads images and video to issues and PRs from the CLI and rewrites local Markdown references to the hosted URLs; gh pr review cannot attach.
kind: workflow
proposed_layer: meta
tags: [github, gh-cli, pull-requests, e2e, evidence]
generated: { by: claude/opus-5.5, at: 2026-11-03T17:59:48Z }
status: draft
sources:
  - id: docs
    resource: https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli
    title: Attaching files with GitHub CLI
    last_modified: 2026-11-03
  - id: run
    resource: https://github.com/zamptax/zamp/pull/10626#issuecomment-6611567167
    title: PR 10626 e2e comment posted with 6 PNG + 2 MP4 via gh 2.103.3
    last_modified: 2026-11-03
not:
  - term: "gh pr review 123 --comment --body-file review.md --attach shot.png"
    why: "gh pr review has no --attach flag (checked on gh 2.103.3); reviews cannot carry uploads"
    instead: "gh pr comment 123 --body-file review.md --attach ./shot.png"
  - term: "upload through the PR comment box in a driven browser"
    why: "needs a GitHub session in the automation browser and a file-input dance; the CLI already holds auth"
    instead: "gh pr comment --attach"
---

# Observation

`--attach <file>` exists on `gh issue create|edit|comment` and `gh pr create|edit|comment` (gh 2.103.3 confirmed; 2.94.0 lacks it). It is repeatable, up to 50 files per command.

Write the body file with ordinary local references, `![alt text](./shot.png)`, and pass the same path to `--attach`. gh uploads the file and rewrites that reference in place to a `https://github.com/user-attachments/assets/...` URL. Attachments the body does not reference are appended at the end, in flag order. A video reference, `![](./clip.mp4)`, must sit alone in its paragraph to render as a player; inside a sentence it renders as a link. Alt text for an appended file goes after `#`: `--attach './shot.png#Login error'`.

Types: png, gif, jpg/jpeg, svg, mp4, mov, webm. Limits: 10MB for images, 10MB for video on free plans and 100MB on paid plans. Needs push access; on private repos only people with repo access can view the uploads.

# Why it matters

E2E evidence (Chrome DevTools screenshots, screencast mp4s) can go straight from a scratch folder onto the PR with one command. Without this, the only route is a browser upload, which fails when the automation browser has no GitHub session (the private repo shows "Page not found"). Because `gh pr review` cannot attach, post the evidence as a PR comment and keep any formal review short.

# Evidence

```bash
gh pr comment 10626 --repo zamptax/zamp --body-file review-final.md \
  --attach ./admin-04-adjustment-lt5.png ... --attach ./admin-filters.mp4 --attach ./company-filters.mp4
```

All 8 local references in the body came back as `user-attachments/assets/<uuid>` URLs, with no local paths left (checked with `gh api repos/zamptax/zamp/issues/comments/6611567167 --jq .body`).
