---
type: Observation
title: Playwright ariaSnapshot records password field values
description: ariaSnapshot() includes every textbox's current value, so a capture taken after filling a login form writes the password in plain text.
kind: failure-mode
proposed_layer: meta
tags: [playwright, secrets, browser-automation, logging]
generated: { by: claude/opus-5, at: 2026-11-05T22:37:48Z }
status: draft
sources:
  - id: evidence
    resource: projects/trikin/maple-draft/src/browser.ts
    title: capture() with password scrubbing and screenshot mask (uncommitted, 2026-11-05)
    last_modified: 2026-11-05
not:
  - term: "writeFileSync(path, await page.locator('body').ariaSnapshot())"
    why: "the tree carries filled textbox values, including type=password inputs"
    instead: "scrub the secret string and the 'textbox \"Password\": …' line before writing; pass mask: [passwordLocator] to page.screenshot"
---

# Observation

`locator.ariaSnapshot()` renders each textbox with its current value (`textbox "Password": <value>`), and type=password inputs aren't exempt. Any debug capture taken after a login form is filled writes the password to disk, and an agent reading that capture puts it in its transcript. Scrub every capture: replace the secret string itself and the password textbox line, and mask the password field in screenshots in case "Show Password" was toggled.

# Why it matters

On Trikin's maple-draft bot the first post-fill capture wrote the MapleMark bank password to a run file on the nix box and into the agent conversation, which meant rotating the bank password.

# Evidence

Capture after filling the MapleMark login form, 2026-11-05: the aria file contained the line `textbox "Password": <the password>`. After the fix, grepping a capture of the same filled form for the password returned 0 matches.
