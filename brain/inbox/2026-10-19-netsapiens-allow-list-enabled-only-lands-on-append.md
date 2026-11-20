---
type: Observation
title: NetSapiens allow list switches on only when a PUT appends a new number
description: The number-filters POST disables the whole allow list on every call; the answerrules PUT with enabled "yes" enables it, but only while appending a number not already present.
kind: failure-mode
proposed_layer: project
proposed_project: wiley
tags: [netsapiens, altaworx, allow-list, api, wiley]
generated: { by: claude/opus-5.5, at: 2026-10-19T23:11:18Z }
status: draft
sources:
  - id: commit
    resource: "projects/wiley commit 46b8cad"
    title: "fix(allow-list): send approved contacts in enabled, stop disabling the list"
    last_modified: 2026-10-19
  - id: code
    resource: projects/wiley/web/lib/netsapiens/client.ts
    title: "addAllowedNumbers doc comment records the measured forms"
    last_modified: 2026-10-19
  - id: probe
    resource: projects/wiley/web/scripts/_probe-allowlist-enable-put.ts
    title: "Re-runnable probe: before/after acp_control around addAllowedNumbers"
    last_modified: 2026-10-19
not:
  - term: "POST ns-api/v2/domains/{d}/users/{u}/number-filters with phone-numbers-to-allow"
    why: "sends no enabled flag and sets acp_control to d on every call, switching off the customer's list"
    instead: "PUT ns-api/v2/domains/{d}/users/{u}/answerrules/%2A with {phone-numbers-to-allow: {parameters, enabled: \"yes\"}}"
  - term: "a 202 from an enable-only write means the list is on"
    why: "enabled with no parameters, re-sending a present number, v2 PATCH, and v1 Update acp_control=e all return 202 and leave acp_control d"
    instead: "read v1 answerrule acp_control back and require \"e\""
---

# Observation

The on/off flag of a NetSapiens (Altaworx) allow list is the v1 answerrule field
`acp_control` (`e` or `d`). `acp_parameters` holds the numbers.

- v2 `POST .../number-filters` with `phone-numbers-to-allow` and no `enabled` appends the
  number and sets `acp_control` to `d`, every call.
- v2 `PUT .../answerrules/%2A` with `{"phone-numbers-to-allow":{"parameters":[...],"enabled":"yes"}}`
  appends and sets `e`, but only when the array holds a number not already on the list.
- Four enable-only forms returned 202 and changed nothing: `enabled` with no parameters,
  re-sending a present number with `enabled: "yes"`, v2 PATCH of `enabled`, and v1
  `object=answerrule&action=Update&acp_control=e`.

So a list that is disabled with every number already present cannot be switched on through
the API. Altaworx has to do it.

# Why it matters

Customers reported approved contacts not ringing through. Each in-app contact add disabled the
whole list again, undoing Altaworx's manual repairs, while every call returned 2xx.

# Evidence

Measured 2026-10-19 on test domain chrisHVQEBL, users 1001 and 1002, by v1 readback of
`acp_control` before and after each write: PUT moved 1002 from d to e; the old POST moved it
back to d; the four enable-only forms left d. The PUT left every other field of the rule
unchanged (full v2 and v1 JSON diff).
