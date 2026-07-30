#!/usr/bin/env python3
"""Score prose against the CLAUDE.style.md rules. Mechanical only.

    usage: style-check.py <file> [<file> ...]

Counts what can be counted, and compares files side by side. Judgment rules
(paragraph pinning, withheld points, whether a fact got dropped) need a reader and
are not scored here, so every number below is a floor.

Use it to re-verify after editing CLAUDE.style.md: have subagents write the same
document with and without the spec, then compare violations per sentence. Measured
on 2026-07-30, over six subagents and two document types:

    bug report        control 0.64 / 0.55  ->  with spec 0.20 / 0.12
    decision record   control 0.48         ->  with spec 0.10

A caution learned the hard way. The first version of the paragraph-final aphorism
detector matched any closing sentence containing "always" or "any", which caught
source facts and reported a regression that was not there. Detectors that fire on
plausible-looking prose will send you at the wrong fix, so keep them narrow and read
what they flag before believing a delta.
"""
import re
import sys
import statistics

FILLER = r"\b(genuinely|really|truly|actually|simply|very|quite|incredibly|remarkably)\b"
CORPORATE = r"\b(leverage[sd]?|leveraging|underscore[sd]?|underscoring|utiliz\w+|facilitat\w+|delv\w+|showcas\w+|unpack\w*)\b"
HEDGE = r"\b(arguably|somewhat|fairly|relatively|perhaps|it seems|I would say|one might|in some sense)\b"
OPENERS = r"^\s*(Great question|Let me|I'll go ahead|So,|Now,|Here's the thing|Sure[,!]|Certainly)"
NOMINAL = r"\b(make a determination|perform a check|conduct an? \w+|provide an? \w+ation|the occurrence of)\b"


def sentences(text):
    prose = "\n".join(
        ln for ln in text.splitlines()
        if not ln.strip().startswith(("#", "|", "```", ">", "-", "*", "1.", "2.", "3.", "4.", "5."))
    )
    prose = re.sub(r"`[^`]*`", "X", prose)
    out = [s.strip() for s in re.split(r"(?<=[.!?])\s+", prose) if len(s.strip()) > 15]
    return out


def score(path):
    text = open(path).read()
    sents = sentences(text)
    words = [len(s.split()) for s in sents]

    # three consecutive sentences within 15% of the same length
    runs = 0
    for i in range(len(words) - 2):
        w = words[i:i + 3]
        if max(w) and (max(w) - min(w)) / max(w) <= 0.15:
            runs += 1

    # corrective negation: a negation followed closely by the corrected version
    corrective = 0
    for s in sents:
        for m in re.finditer(r"\b(not|isn't|wasn't|aren't|doesn't|don't|never|no)\b", s, re.I):
            tail = " ".join(s[m.end():].split()[:14])
            if re.search(r"\b(but|it's|it is|rather|instead|the real|what it is)\b|;", tail, re.I):
                corrective += 1

    # negative-first construction: ", not X" / "X, not Y" appositive
    neg_appositive = len(re.findall(r",\s+(not|never|rather than|instead of)\s+\w", text, re.I))

    # corrective markers used to displace a wrong alternative
    displacers = len(re.findall(r"\b(rather than|instead of|as opposed to)\b", text, re.I))

    # prose triads: a, b, and c  (three parallel comma items)
    triads = len(re.findall(r"\b\w[\w\s]{2,28},\s+\w[\w\s]{2,28},\s+and\s+\w[\w\s]{2,28}\b", text))

    # cross-sentence corrective negation: "was not X. It was Y."
    cross_neg = len(re.findall(
        r"\b(was|is|were|are|had)\s+(not|no)\b[^.!?]*[.!?]\s+(It|That|They|This)\s+(was|is|were|are)\b",
        text, re.I))

    # contrasting pair joined by while/whereas
    contrast = len(re.findall(r",\s+(while|whereas)\s+the\b", text, re.I))

    # landing sentence: a closing beat announcing its own significance
    landing = len(re.findall(
        r"\b(the (lesson|takeaway|point|upshot|moral)|what (matters|this means)|worth (carrying|remembering)|"
        r"the real (lesson|question|problem)|in the end|ultimately)\b", text, re.I))

    # paragraph-final aphorism, narrowed to the gnomic shape:
    # an abstract subject ("a checker", "any monitor") plus a timeless modal.
    # The earlier broad version flagged source facts containing "always", so it
    # produced more noise than signal and drove a wrong conclusion once already.
    aphorism = 0
    GNOMIC = re.compile(
        r"^(A|An|Any|Every|Each|No)\s+\w+[\w\s]{0,40}?\s(can|cannot|can't|will|would|never|always)\b"
        r"|^(You|One)\s+(can|cannot|can't|never|always)\b"
        r"|\bis\s+(a|the)\s+\w+\s+(of|on)\s+how\b", re.I)
    for para in [x.strip() for x in text.split("\n\n")]:
        if para.startswith(("#", "```", ">", "-", "*")) or len(para) < 80:
            continue
        ss = [x.strip() for x in re.split(r"(?<=[.!?])\s+", para) if x.strip()]
        if len(ss) < 2 or ss[-1].endswith(":"):
            continue
        last = ss[-1]
        if re.search(r"\d|`", last):
            continue
        if GNOMIC.search(last):
            aphorism += 1

    # announcing significance
    signposts = len(re.findall(r"\b(the (important|useful|key|interesting) part|worth (knowing|noting)|note that)\b", text, re.I))

    # short declarative runs (parataxis)
    para = sum(1 for i in range(len(words) - 2) if all(x <= 7 for x in words[i:i + 3]))

    m = {
        "em/en dashes": len(re.findall(r"[—–]", text)),
        "filler intensifiers": len(re.findall(FILLER, text, re.I)),
        "corporate verbs": len(re.findall(CORPORATE, text, re.I)),
        "hedges": len(re.findall(HEDGE, text, re.I)),
        "throat-clearing": len(re.findall(OPENERS, text, re.M)),
        "nominalizations": len(re.findall(NOMINAL, text, re.I)),
        "corrective negation": corrective,
        "', not X' appositive": neg_appositive,
        "rather-than displacers": displacers,
        "prose triads": triads,
        "cross-sentence negation": cross_neg,
        "while/whereas contrast": contrast,
        "landing beats": landing,
        "para-final aphorism": aphorism,
        "significance signposts": signposts,
        "3 same-length runs": runs,
        "parataxis runs": para,
        "exclamations": text.count("!"),
    }
    total = sum(m.values())
    return m, total, words


def main():
    reports = []
    for path in sys.argv[1:]:
        m, total, words = score(path)
        reports.append((path, m, total, words))

    keys = list(reports[0][1].keys())
    w = max(len(k) for k in keys) + 2
    names = [p.split("/")[-1].replace(".md", "")[:22] for p, _, _, _ in reports]
    print(" " * w + "".join(f"{n:>24}" for n in names))
    for k in keys:
        row = "".join(f"{r[1][k]:>24}" for r in reports)
        print(f"{k:<{w}}{row}")
    print("-" * (w + 24 * len(reports)))
    print(f"{'TOTAL VIOLATIONS':<{w}}" + "".join(f"{r[2]:>24}" for r in reports))
    print(f"{'sentences':<{w}}" + "".join(f"{len(r[3]):>24}" for r in reports))
    print(f"{'len stdev':<{w}}" + "".join(
        f"{(statistics.stdev(r[3]) if len(r[3]) > 1 else 0):>24.1f}" for r in reports))
    print(f"{'violations/sentence':<{w}}" + "".join(
        f"{(r[2] / max(1, len(r[3]))):>24.2f}" for r in reports))


if __name__ == "__main__":
    main()
