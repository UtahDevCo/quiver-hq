---
name: lead
description: Run one lead-agent pass over every Solo project — sweep the board, triage the flags, act on what's safe, record to the scratchpad, and report what needs you. Use when the user asks to check on their projects, run a sweep, do a standup/triage pass, or manage agents across projects. Pair with /loop for a standing loop.
---

# Lead agent pass

One pass over the whole portfolio. The protocol is
`~/dev/quiver-hq/solo/solo-lead-agent.md` — **read it first**, it is the source of
truth for the flag table, the triage buckets, and the intervention rules.

```bash
cat ~/dev/quiver-hq/solo/solo-lead-agent.md
cd ~/dev/quiver-hq && solo-orch sweep
```

Then work the pass: **SWEEP → TRIAGE → ACT → RECORD → REPORT**.

## Arguments

`$ARGUMENTS` narrows or changes the pass:

- *(empty)* — normal pass over all projects.
- `<project>` — only that project; still sweep everything, but only act there.
- `quiet` — `solo-orch sweep --quiet`, report only if a flag needs the human.
- `close` — run the closing pass from §"Closing pass" in the protocol.

## Non-negotiables

- **Ask before spending.** Spawning agents, killing processes, pushing, deploying:
  propose, don't perform. Bookkeeping (todo status, scratchpad notes) is yours.
- **Other people's work is untouchable.** The board shows agents and dirty trees
  from other sessions and from Chris. Report them; never revert or commit them.
- **Read the agent's output before deciding it's stalled.** Most stalls are an
  agent waiting on a question, answerable with `mcp__solo__send_input`.
- **A clean board gets one line, not a report.** Don't manufacture work.

## Standing loop

`/loop /lead` self-paces; `/loop 20m /lead` fixes the interval. When self-pacing,
set the next wake from the board: babysitting live agents → 5–10m, work in flight
→ 20–30m, clean and idle → 60m or stop.
