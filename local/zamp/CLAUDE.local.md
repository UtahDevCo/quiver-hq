# Local instructions (git-ignored, not committed)

## Code comments: keep absolutely minimal

- Prefer self-documenting code over comment. No comment that just restate what code already say.
- Only comment genuinely non-obvious **why** (subtle invariant, workaround, gotcha). One terse line where possible.
- No multi-line block comment in implementation file.
- No docblock that just paraphrase function name/signature.
- Storybook story description: one concise line.
- Apply to code you write or edit. **Do not touch pre-existing comment from others** — only trim comment part of your own change.