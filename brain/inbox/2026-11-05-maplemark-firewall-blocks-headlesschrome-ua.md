---
type: Observation
title: MapleMark login firewall blocks the HeadlessChrome user agent
description: The bank's WAF returns Access Denied to headless Chrome; headed Chrome under xvfb-run with a once-trusted persistent profile logs in with no 2FA.
kind: module
proposed_layer: project
proposed_project: trikin
tags: [maplemark, playwright, browser-automation, banking]
generated: { by: claude/opus-5, at: 2026-11-05T22:37:48Z }
status: draft
sources:
  - id: evidence
    resource: projects/trikin/maple-draft/src/dev/serve.sh
    title: Chrome launched headed under xvfb-run with remote debugging on the bot profile (uncommitted, 2026-11-05)
    last_modified: 2026-11-05
not:
  - term: "chrome --headless=new (or Playwright's default headless launch)"
    why: "UA contains HeadlessChrome; MapleMark's login returns an Access Denied iframe and 'An unknown error has occurred'"
    instead: "headed Chrome under xvfb-run, attached with chromium.connectOverCDP"
---

# Observation

Submitting the MapleMark online-banking login from headless Chrome (UA `HeadlessChrome/156`) gets an "Access Denied" iframe from the bank's firewall. Real Chrome running headed under `xvfb-run`, with a persistent `--user-data-dir` and driven over CDP (`chromium.connectOverCDP`), logs in fine. Once Chris logged in by hand in that profile and trusted the device, later automated logins skipped 2FA. Session cookies don't survive closing the browser, so every run logs in again.

# Why it matters

Each blocked attempt is a failed login on the real bank account. Repeating them risks a lockout and looks like an attack to the bank.

# Evidence

2026-11-05 on the nix box: the headless attempt was blocked (reference ID a5e2b3058f). After Chris's manual trusted login, the headed xvfb Chrome logged in automatically to #/landingPage with no challenge.
