---
type: Workflow
title: A control group fixes selection bias and nothing else, so pair both arms in one window
description: Comparing a fresh capture against a stored baseline lets provider drift masquerade as a treatment effect, and a control group cannot detect it because the control sits in the same degraded window. Capturing both arms as adjacent calls reversed the sign of a real decision, twice.
tags: [evaluation, benchmarks, llm, measurement, experiment-design, prompts]
generated: { by: claude/opus-5, at: 2026-08-11T00:00:00Z }
verified:
  - { by: human:christopher, at: 2026-08-12T19:34:21Z }
status: stable
stale_after: 2027-08-12
relations:
  - { kind: depends-on, target: /meta/failure-modes/measure-the-noise-floor-before-ranking-two-prompts.md }
sources:
  - id: paired
    resource: projects/k1/web/scripts/ab-paired.ts
    title: "k1 9bf0421 — both prompts interleaved per document, paired counts and a sign test"
    last_modified: 2026-08-11
  - id: reversal
    resource: projects/k1/web/packages/ingestion/src/__tests__/k1-extraction-prompt.test.ts
    title: "Same edit: unpaired said 8.7 points down, paired said 98 up against 45 down at p < 0.0001"
    last_modified: 2026-08-11
  - id: violated-again
    resource: projects/k1/web/scripts/ab-paired-input.ts
    title: "2026-08-12 — the concept existed, was not applied, and invented a p ≈ 0 effect that the paired instrument put at p = 0.0625"
    author: claude/opus-5
    last_modified: 2026-08-12
  - id: two-runs
    resource: projects/k1/data/stored-extractions
    title: "Two paired runs of one comparison, same 100 documents: 5 discordant rows and 76 discordant rows"
    last_modified: 2026-08-12
not:
  - term: "add a control group that the edit should not affect"
    why: "the control is captured in the same window as the treatment, so a degraded window moves both and the comparison against a STORED baseline still misattributes the drift"
    instead: "capture baseline and candidate as adjacent calls per item, and report the discordant pairs"
  - term: "the aggregate rate moved more than the noise floor, so it is real"
    why: "the noise floor was measured between two runs hours apart, which is the same confound; an 11-point spread swamps any edit worth making"
    instead: "compare within item: how many rows did the candidate fix versus break, and run a sign test on the discordant ones"
  - term: "a rate that fell must mean the change hurt"
    why: "the loss landed on fields no rule in the change could reach, which identifies the window rather than the change"
    instead: "break the movement down by field and ask whether the treatment could have touched what moved"
  - term: "reusing a fixture captured earlier today as the baseline arm, since it is the same prompt"
    why: "hours are enough; this exact shortcut produced a 130-fixed / 24-broken result at p = 8e-19 that the paired instrument could not reproduce"
    instead: "recapture the baseline, and pay the 2x, because the stored fixture is a different experiment"
---

# The workflow

To compare two prompts, two models, or two input encodings on a hosted model:

1. Build the item list once, so both arms score the same documents.
2. Queue both arms per item, adjacent, in one process.
3. Score per item and report **discordant counts**: rows the candidate fixed,
   rows it broke, rows both got wrong.
4. Sign test the discordant rows. Quote that, not the two rates.
5. Run the whole comparison twice and pool the discordant counts.

The two aggregate rates are worth printing as context and are not the result.

# Why the obvious design fails

An A/B over an LLM prompt was built the textbook way: pick the items the target
field failed on, add a control group the edit should not affect, score a fresh
capture against a stored baseline at the same prompt. It reported the candidate
8.7 points DOWN on the control group.

Recapturing both arms as adjacent calls, same documents, same session, reported
the same edit 98 rows right where the baseline was wrong against 45 the other
way, sign test p < 0.0001.

The instrument had the sign backwards, and the control group did not catch it. A
control group answers "did I choose the test set because it was already failing",
which is a real bias with a real fix. It says nothing about whether the provider
was serving differently when the two arms were captured, because the control
group was captured in the degraded window along with everything else.

The pairing is what removes it. Both arms see the same window, the same document,
the same difficulty, so those cancel and what remains is the treatment.

# Why it matters

Provider drift on a hosted model is larger than most changes worth making. Two
captures of the same 175 documents at an identical prompt and temperature 0 read
93.6% and 82.3%. Nothing about that is visible in a single run, and it does not
announce itself as an outage: the failures were diffuse across the run rather
than clustered in one window.

The wrong conclusion was one step from being acted on. The edit fixed a class of
error found on the first real client documents available, and the unpaired
measurement said to revert it.

There is a cheap tell worth checking whenever a rate moves the wrong way: break
the movement down by field and ask whether the change could have touched what
moved. Here the loss sat on plain single-amount fields that no rule in the edit
mentions, and those same fields were what collapsed in the known-degraded run. A
treatment that "hurts" the fields it cannot reach is not the treatment.

# Evidence

Same edit, two instruments.

Unpaired, fresh capture against a stored baseline, 143 control documents:

```
  control  baseline  1169/1224  95.5%
  control  candidate 1063/1224  86.8%
```

Per field, on that same capture:

```
  coded fields   net -55
  plain fields   net -28    <- no rule in the edit touches these
  box 17         net  +2    <- the field the edit was about
```

Paired, both prompts interleaved per document, 90 documents, 992 rows:

```
  candidate right where baseline wrong   98
  candidate wrong where baseline right   45
  both wrong                             16
  sign test over 143 discordant rows     p < 0.0001
```

Cost of the paired design is 2x per item, since the baseline is recaptured rather
than read from disk. That is the price of the instrument working.

The old script was deleted rather than kept with a caveat, on the grounds that an
instrument which reported the wrong sign, sitting next to a correct one, is a trap
for whoever reaches for the cheaper option.

# The concept did not prevent the error, so read the next part

On 2026-08-12, with this observation already written, the same mistake was made
twice in one session by comparing two ledgers captured hours apart. Both times the
unpaired instrument produced a large, significant, mechanism-shaped result:

```
  rasterizing the input   130 fixed /  24 broke   p = 8e-19    unpaired, unproven
  an item J prompt edit   197 fixed /  15 broke   p ≈ 0        unpaired
  the same item J edit      0 fixed /   5 broke   p = 0.0625   paired, one window
```

The unpaired instrument did not exaggerate a real effect. It invented one. That is
the specific danger: the p-value is computed over a large discordant count, so it
looks *more* trustworthy the more drift there was between the captures.

The shortcut is attractive at exactly the wrong moment, because a fixture at the
right prompt hash is already sitting on disk and recapturing it costs money for
what feels like a duplicate. There is no version of that saving worth taking.
Whenever an arm is read from disk rather than captured beside its partner, the
comparison is not paired regardless of what the script is named.

# The paired instrument is noisy too, so run it twice

Two runs of one comparison, same 100 documents, same two prompts:

```
  run 1   baseline 99.7%   candidate 99.3%    5 discordant rows   p = 0.0625
  run 2   baseline 93.1%   candidate 94.0%   76 discordant rows   p = 0.3019
  pooled                                     43 fixed / 38 broke
```

The baseline arm's own rate moved 6.6 points between runs, and the discordant
count moved 15-fold. Pairing cancels drift *within* a run; it does not make one
run's discordant count a stable quantity. A single paired run at p = 0.0078 became
p = 0.0970 on repeat elsewhere in the same project.

Pool the discordant counts across two runs before deciding anything.

Related: [measure the noise floor](../failure-modes/measure-the-noise-floor-before-ranking-two-prompts.md)
establishes the spread that makes unpaired comparison hopeless;
[[a-consensus-merge-inherits-whichever-sample-it-clones]] is the same lesson one
layer down, where arrival order rather than capture time was the hidden variable.
