---
type: Failure Mode
title: Measure through the input container production actually accepts
description: Sending bare PNGs to a model that production only ever feeds PDFs produced a 45-point accuracy collapse that does not exist in the product, and it pointed at building a pipeline stage to fix it.
tags: [evaluation, benchmarking, extraction, multimodal, confounds]
generated: { by: claude/opus-5, at: 2026-08-12T18:20:00Z }
verified:
  - { by: human:christopher, at: 2026-08-12T19:34:21Z }
status: stable
stale_after: 2027-08-12
relations:
  - { kind: depends-on, target: /meta/workflows/pair-both-arms-in-one-window-or-drift-picks-the-winner.md }
sources:
  - id: measurement
    resource: projects/k1/data/stored-extractions/2026-08-12-gemini-2.5-flash-f55283cd-degraded.meta.json
    title: Degraded fixture, bare-image arm
    last_modified: 2026-08-12
  - id: upload-path
    resource: projects/k1/web/apps/web/app/api/projects/[tenantSlug]/[projectId]/uploads/route.ts
    title: The upload route accepts application/pdf and nothing else
    last_modified: 2026-08-12
not:
  - term: "the bytes are the same image either way, so the container cannot matter"
    why: "a multimodal model receives a declared MIME type and a container the provider decodes differently; measured, the same raster scored 92.1% bare and 100% inside a PDF"
    instead: "submit through the same container, MIME type and code path the product submits"
  - term: "test the hardest input you can construct"
    why: "an input the product cannot accept produces a number about nothing, and it can be dramatic enough to reorder the roadmap"
    instead: "enumerate what the intake actually accepts first, then degrade within that set"
  - term: "the container comparison found a large improvement, so re-encode the input in production"
    why: "that comparison was made between two captures taken hours apart, so provider drift and the container change were the same variable; see the workflow this depends on"
    instead: "re-run it with both containers interleaved per document before believing any part of it"
---

# The trap

An evaluation of a model on documents must submit them the way production submits
them: same container, same declared MIME type, same call path. The container is a
variable, not packaging.

Measured, one model, one prompt, byte-identical rasters, differing only in whether
each was sent as a bare image or wrapped in a single-page PDF:

```
                       bare image   inside a PDF
200 DPI raster            92.1%        100.0%
JPEG quality 45           92.1%        100.0%
rotated 1.5 degrees       48.0%         92.9%
```

The 48.0% was the finding of the day. It read as a catastrophic sensitivity to
page skew, it was reproducible, it had a plausible mechanism, and it pointed at
building a deskew stage. It was an artifact of a container the product cannot
accept: the upload route takes `application/pdf` and rejects everything else, so
no bare image has ever reached that code path.

The check that caught it was cheap and should have come first: read the intake
code and list the input shapes it accepts, before generating a corpus of shapes.

# Why it matters

The failure mode is not a slightly wrong number. It is a confident,
mechanism-shaped conclusion pointing at work that would have delivered nothing.
Skew costs about 7 points inside a PDF, not 44, and a deskew stage sized against
the artifact would have been the top priority for no reason.

Generalization beyond documents: any place a payload crosses a boundary with a
declared type, the declaration is part of the input. Measuring a parser on decoded
objects when production hands it a byte stream, or a model on plain text when
production sends markdown, is the same mistake.

# Evidence

The container comparison, same 36 rasters through the same capture script, the
only difference being `sips -s format pdf` and the MIME type sent:

```
bun scripts/capture-extractions.ts --corpus degraded      --out bare.jsonl
bun scripts/capture-extractions.ts --corpus <pdf-wrapped> --out wrapped.jsonl
bun run score --ledger bare.jsonl    --variant rot1.5deg   # 48.0%
bun run score --ledger wrapped.jsonl --variant rot1.5deg   # 92.9%
```

The intake constraint that should have been read first:

```ts
// uploads/route.ts
return file.type === "application/pdf" || fileExtension(file.name) === ".pdf"
```

The capture script had to be extended to walk `.png` and `.jpg` at all, since it
previously found only `.pdf`. That extension was the moment to ask whether the
product ever sees a bare image, and the question was not asked.

# What this experiment did NOT establish

The same session read a second, larger result out of the same setup: that
rasterizing a digital PDF and re-wrapping it beat sending the original PDF by 8.0
points across 103 documents, 130 boxes fixed against 24 broken, sign test
p = 8e-19, with code-letter confusion falling from 16 occurrences to zero.

**That number is not evidence of anything.** The two arms were separate captures
taken hours apart, so the comparison is the unpaired design that
[pair both arms in one window](../workflows/pair-both-arms-in-one-window-or-drift-picks-the-winner.md)
exists to rule out. On this provider, two identical captures of one corpus have
read 11.3 points apart, which is larger than the claimed effect. Applying the
identical unpaired shortcut to a prompt edit in the same session produced 197
fixed against 15 broken at p ≈ 0, where the paired instrument read 0 fixed and 5
broken at p = 0.0625.

It is recorded here because the temptation is specific and worth naming: an
artifact and a plausible real effect can live in the same experiment, and having
just caught the artifact makes the other result feel audited. Catching one
confound does not clear the rest.

It was run on 2026-08-13, twice, over 103 documents and 1327 box rows with both
arms adjacent per document. Rasterizing **costs** 2.3 points: 33 fixed against 91
broken, pooled. The unpaired run had it 8.0 points the other way.

Two further things the paired runs settled. Skew inside a real PDF costs about 5
points rather than the 44 the bare-image rows imply, measured as 0 fixed against 13
broken over 254 paired rows. And the damage from re-rendering concentrates in the
boxes that print a code letter beside an amount, which is the exact failure the
unpaired run had credited rasterizing with removing.
