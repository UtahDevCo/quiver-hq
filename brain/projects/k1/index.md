# k1

Project knowledge for `projects/k1`. Reachable from inside the repo as
`.brain/index.md`.

Resolve against the [meta layer](../../meta/index.md) — see
[conventions](../../conventions.md) for how `Practice Override` composes.

# Overrides

*Meta practices this project narrows, extends, replaces, or suspends. Empty.*

# Patterns

*Opt-in and portable. Empty.*

# Workflows

* [prompt-length-costs-accuracy-on-fields-the-words-never-mention](workflows/prompt-length-costs-accuracy-on-fields-the-words-never-mention.md) - The same schema change, described in 1618 characters of prose and then in 655, went from significantly worse than baseline to significantly better on a paired measurement. The loss and the gain both landed on unrelated fields, so the cost was the length rather than the content.

# Failure modes

* [a-checkbox-a-model-misreads-cannot-gate-a-check](failure-modes/a-checkbox-a-model-misreads-cannot-gate-a-check.md) - A validation rule was gated on a newly extracted checkbox. Across three prompt revisions the extractor read that box wrong on 4, 14 and 13 of the same 20 documents, moving with wording that had nothing to do with checkboxes. The rule was rewritten to read two numbers that say the same thing.
* [a-consensus-merge-inherits-whichever-sample-it-clones](failure-modes/a-consensus-merge-inherits-whichever-sample-it-clones.md) - Anchoring the merge on the first sample scored 93.1% against 95.2% for anchoring on the sample that agrees most with the others, and at n=2 the merge scored exactly the primary's own rate.
* [an-idempotency-guard-makes-a-dropped-write-look-like-success](failure-modes/an-idempotency-guard-makes-a-dropped-write-look-like-success.md) - Asking the identical question in a fresh conversation returned HTTP 200 with nothing rendered and nothing stored, six attempts each on two questions, while 38 other runs on the same page succeeded.
* [re-rendering-a-page-costs-the-boxes-where-a-code-sits-beside-an-amount](failure-modes/re-rendering-a-page-costs-the-boxes-where-a-code-sits-beside-an-amount.md) - Rasterizing a digital K-1 at 200 DPI lost 51 of 61 discordant rows in box 20 alone, the box where a code letter is printed beside its amount, while single-value boxes barely moved.

# Practices

*Project-local rules. Empty.*

# Modules

*What the major pieces are and how they fit. Empty.*

# Invariants

*Rules with an executable check attached. Empty.*

# Decisions

*Why things are the way they are. Empty.*

# Gems

*Project-local patterns worth promoting to meta. Empty.*

# Candidates for meta

Both concepts above were written proposing `meta` and were demoted on
2026-08-12 for having single-system evidence. Each names what would lift it, in a
closing section. Neither has an `instance-of` target yet because no meta concept
covers the same ground.
