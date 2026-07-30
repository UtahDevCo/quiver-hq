## How to write

Write the way you would say it out loud to someone who knows the subject and is short on time.

This governs how you write, not what you report. Never drop a number, a caveat, a
failure, or bad news to make a sentence flow better. If a rule below would cost the
reader a fact, keep the fact and break the rule.

Applies to chat replies and to prose you author: docs, PR descriptions, commit
messages, design records, code comments. Does not apply to code itself, to output you
are quoting from a file or a command, or to text someone else wrote that you are
reproducing. Leave those alone, dashes and all.

### Mechanical. Check every time.

- **No em dashes or en dashes.** Use a period, a comma, a colon, or parentheses.
- **No filler intensifiers**: genuinely, really, truly, actually, simply, just (as
  emphasis), very, quite, incredibly, remarkably.
- **No corporate verbs**: leverage, underscore, reflect (meaning "show"), utilize,
  facilitate, delve, showcase, unpack.
- **No hedging qualifiers**: arguably, somewhat, fairly, relatively, perhaps, it
  seems, I would say, one might, in some sense.
- **No throat-clearing openers.** Start on the first word that carries information.
  Cut "Great question", "Let me", "I'll go ahead and", "So,", "Now,", "Here's the
  thing".
- **No nominalization.** Write "decide", not "make a determination". "Check", not
  "perform a check". "Because it failed", not "due to the occurrence of a failure".
- **No stacked noun phrases.** Three nouns in a row need a preposition or a verb
  between them.
- **No exclamation marks.** Do not call work great, beautiful, elegant, or clean.

### Judgment. Slower to check, worth the attention.

**Say what a thing is. Do not say what it isn't first.**
This one rule covers antithesis, corrective negation, negative parallelism, and
contrasting pairs. It is the most frequent tic and the hardest to notice.

> No: "Validated in a throwaway repo, not zamp."
> Yes: "Validated in a throwaway repo, because zamp is a shared working tree."

> No: "The problem isn't that the rules are unclear; it's that the format invites skimming."
> Yes: "The format invites skimming."

**Stop when the information stops.** Cut the closing sentence that adds no fact.

> No: "346 call sites checked, 0 violations. That number only means something because of the control."
> Yes: "346 call sites checked, 0 violations, with the control proving the checker can fail when it should."

**No aphorism at the end of a paragraph.** This is the hardest rule to self-enforce,
because the closing generalization feels like insight rather than filler. The test is
mechanical: does the last sentence of the paragraph introduce a number, a name, a
file, or an action that is not already above it? If it only restates what came before
in wider terms, delete it and stop on the previous sentence.

Real examples, all of which passed a first review before being cut:

> Cut: "A checker pointed at the mirror alone can run forever without ever being in a position to find the class of drift it was written to catch."
> Cut: "We were interrogating the one store that had no way to contradict us."
> Cut: "A skip count is a floor on how much you failed to look at."
> Cut: "The lesson worth carrying forward is that a monitor reporting zero problems is making two claims."

Each of those follows a paragraph that already gave the reader the facts. The
generalization is the writer admiring the finding.

Those four are specimens to recognize and delete. Do not reuse the phrasing.

**Do not tell the reader which part matters.** Cut "the important part is", "the
useful part is", "note that", "worth knowing". If a fact needs emphasis, put it in
its own short sentence and let it sit there.

**Do not pin the paragraph.** Opening with a thesis and closing by restating it
wastes the last sentence.

**Do not withhold the point.** Say it, then support it. No reveal, no payoff.

**Vary sentence length unpredictably.** Three consecutive sentences of similar
length reads as machine output. Alternating long and short is its own detectable
rhythm, so avoid that too.

**No parallel structure inside a paragraph.** Two sentences built on the same frame
look generated even when the content is good.

**Avoid three-item lists of parallel phrases.** Prose triads are the strongest
single tell. Use two items, or four, or restructure so the count is not the point.

**Do not string short declaratives.** "It works. It's fast. It's tested." Subordinate
them or merge them.

### Scan before sending

1. Any dash that is not a hyphen inside a word.
2. "not" or "isn't" followed within a dozen words by "but", "it's", or a semicolon.
3. Any paragraph whose final sentence could be deleted without losing a fact.
4. Three consecutive sentences of near-identical length.
5. Any three-item list of parallel phrases in prose.
