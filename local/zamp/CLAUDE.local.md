# Local instructions (git-ignored, not committed)

## Code comments: keep absolutely minimal

- Prefer self-documenting code over comments. Do not add a comment that merely
  restates what the code already says.
- Only comment a genuinely non-obvious **why** (a subtle invariant, a workaround,
  a gotcha), and keep it to a single terse line where possible.
- No multi-line explanatory block comments in implementation files.
- No docblocks that just paraphrase a function's name/signature.
- Storybook story descriptions: one concise line.
- This applies to code you write or edit. **Do not touch pre-existing comments
  authored by others** — only trim comments that are part of your own change.

