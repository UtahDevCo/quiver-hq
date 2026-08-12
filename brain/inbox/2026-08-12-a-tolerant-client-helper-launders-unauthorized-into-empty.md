---
type: Observation
title: A tolerant client helper launders "unauthorized" into "empty"
description: Shared API helpers catch auth and not-found errors and return an empty list. An audit built on one reports full coverage it never had, and the swallowing is invisible at the call site.
kind: failure-mode
proposed_layer: meta
tags: [auditing, error-handling, api-clients]
generated: { by: claude/opus-5, at: 2026-08-12T19:40:27Z }
status: draft
sources:
  - id: evidence
    resource: projects/wiley/web/scripts/audit-quiet-hours-rule-order.ts
    title: audit reading the endpoints directly, after the helper hid a 401
    last_modified: 2026-08-12
  - id: helper
    resource: projects/wiley/web/lib/netsapiens/client.ts
    title: getAnsweringRules, whose fallback predicate treats 401 like 404
    last_modified: 2026-08-12
not:
  - term: "reuse the shared client helper in an audit because it handles the awkward cases"
    why: "the cases it handles include ones that mean the audit could not look, and it returns them as an empty result"
    instead: "call the endpoint directly in the audit, swallow only the error that genuinely means absent, and count everything else as unreadable"
---

# Observation

API client helpers accumulate tolerance. A fallback predicate written for one
caller's convenience ends up treating "not authorized" the same as "not found",
and the helper returns an empty array for both.

An audit calling that helper cannot tell the two apart, and empty reads as
"looked, nothing there". The audit then reports zero unreadable accounts, which
is a stronger claim than it is entitled to make and one that nothing in its
output contradicts.

An audit should call the endpoint itself and swallow only the error that means
the thing is genuinely absent. Everything else is unreadable, and unreadable is
a verdict, not a gap to be filled with a benign default.

# Why it matters

The first run of an audit over 289 accounts reported: 289 readable, 0
unreadable. One of those accounts was already known to return 401 on every call
to this vendor, from a different audit run the day before. It had been filed
under "has no rule of this type" and counted as fully inspected.

Had that account not already been known to fail, the audit's coverage line would
have been believed. A run claiming complete coverage attracts no scrutiny.

# Evidence

The helper's fallback predicate:

    private isAnsweringRuleFallbackError(error: unknown): boolean {
        const message = error instanceof Error ? error.message : String(error);
        return message.includes("404") || message.includes("401");
    }

and the loop it guards ends `return []` after every endpoint has been tried. A
401 arrives at the caller as an empty list.

Before and after, same fleet, same day:

    readable 289   unreadable 0   no-rule 1        <- the 401 account, miscounted
    readable 288   unreadable 1   no-rule 0        <- reading the endpoints directly

The corrected count is also labelled a floor in the output, because one account
that could not be read means the headline number is a lower bound.
