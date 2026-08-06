---
type: Observation
title: A document's text layer can be clean while its rendered pixels are corrupt
description: Two PDF text operators that overlap on the page extract perfectly and render as one illegible glyph, so a vision model fails on a field that every text-based check says is present.
kind: failure-mode
proposed_layer: meta
tags: [pdf, extraction, ground-truth, fixtures, evaluation]
generated: { by: claude/opus-5, at: 2026-08-06T21:40:00Z }
status: draft
sources:
  - id: fix
    resource: projects/k1/data/K1_Corpus_v4/generator/render.py
    title: Part III code letter drawn at a fixed x that the box 18 label overran
    last_modified: 2026-08-06
  - id: commit
    resource: "k1@8cbc035"
    title: "fix(corpus): stop the Part III code letter being drawn on top of the label"
    last_modified: 2026-08-06
not:
  - term: "extract the PDF text layer to confirm the field is present, then blame the model"
    why: "overlapping draw operations are separate, intact strings in the content stream; position is the only thing that makes them illegible, and text extraction discards position"
    instead: "rasterize the page and look at it, and assert on geometry at draw time in whatever produced the document"
---

# Observation

A PDF's text layer and its rendered appearance can disagree completely. Two text
operators drawn at overlapping coordinates are two clean, separate strings in the
content stream, and every text-extraction check will report both as present. On the
page they are one smear of overlapping glyphs that no reader, human or model, can
resolve.

Any evaluation of a vision model reading documents has to be checked against the
rasterized page. Extracting the text layer answers a different question than the one
being asked.

# Why it matters

The divergence sends the investigation to the wrong component. A field extracted at 0
percent, with the text layer showing it clearly present, reads as a model failure, and
the natural response is to work on the prompt.

In k1, box 18 of a synthetic Schedule K-1 corpus scored 0 out of 132 against ground
truth while structurally identical coded boxes scored 83 to 95 percent. A prompt rule
telling the model to read the code letter from its column lifted overall accuracy from
63.5 to 77.8 percent and left box 18 at exactly 0, which is the signal that the target
was never reachable by prompting.

The generator drew the code letter at a fixed x+122 and the label at x+20. Box 18's
label, "Tax-exempt income and nondeductible expenses", is 128.5pt at 5.9pt Helvetica,
so it ran 26.5pt past the code column and the letter C landed on top of the e in
"expenses". The sidecar JSON still declared code C, so ground truth demanded a value
the document could not show, and the metric was unsatisfiable rather than merely bad.

Two things would have found this sooner. Accuracy correlated with label width across
every coded box, which is a layout signature and not a model one. And a single glance
at the rendered page shows it immediately.

# Evidence

Per-box accuracy against label width, all against the same corpus and model:

```
box   label width  clearance  accuracy
 18       128.5pt     -26.5     0%     Tax-exempt income and nondeductible expenses
 17        96.7pt      +5.3    89%     Alternative minimum tax (AMT) items
 14        84.6pt     +17.4    83%     Self-employment earnings (loss)
 13        44.9pt     +57.1    95%     Other deductions
```

What the page showed, versus what the text layer said:

```
rendered:    18  Tax-exempt income and nondeductibleCxpenses          820
text layer:  ... | 18 | Tax-exempt income and nondeductible expenses | C | 820 | ...
```

Both the broken and the fixed corpus emit the code as its own text operator, so a
structural check over the content stream passes on both and detects nothing. The only
reliable check is geometric, at draw time, in the generator:

```python
if LABEL_DX + stringWidth(label_txt, "Helvetica", 5.9) > CODE_DX:
    raise ValueError(f"Part III row {label_num}: label {label_txt!r} runs into the "
                     f"code column, so code {code!r} would be drawn on top of it.")
```

Restoring the old constant now fails generation with exactly that message, naming box
18. With the column moved and nothing else changed, on the same model and the same
unmodified prompt, box 18 went from 0/30 to 21/30 and the eleven cases of C being read
as A went to zero.
