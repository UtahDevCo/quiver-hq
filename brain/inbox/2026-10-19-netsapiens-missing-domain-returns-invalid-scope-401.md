---
type: Observation
title: NetSapiens answers a nonexistent domain with 401 Invalid Scope
description: User-level v2 and v1 calls against a deleted domain return 401 "Invalid Scope [APP001]", which reads as a missing API permission.
kind: failure-mode
proposed_layer: project
proposed_project: wiley
tags: [netsapiens, altaworx, api, errors, wiley]
generated: { by: claude/opus-5.5, at: 2026-10-19T23:11:18Z }
status: draft
sources:
  - id: thread
    resource: "Gmail thread 19dd4bc2242dbcae (Altaworx ticket 107697)"
    title: "2026-09-18 email blamed API scope; Edwin replied the key had the scope"
    last_modified: 2026-10-19
not:
  - term: "401 Invalid Scope [APP001] means the API key lacks a scope"
    why: "the same key got 200 on the same endpoints for an existing domain; the 401 domain had been deleted"
    instead: "GET ns-api/v2/domains/{domain} first; a 404 there means the domain is gone"
---

# Observation

With a valid key, `GET ns-api/v2/domains/{domain}` returns 404 for a deleted domain, but every
user-level call under it (`/users`, `/users/{u}`, `/answerrules`, and v1
`object=answerrule&action=Read`) returns `401 {"code":401,"message":"Invalid Scope [APP001]"}`.

# Why it matters

The 401 was reported to the carrier as a missing permission on our API application, and it
also raised a false alarm that in-app allow-list writes were failing. Both were wrong. The
test domain had been removed.

# Evidence

2026-10-19, key `nsr_3I…`, both hosts (nsb1.unifiedsolutions.cloud, portal.altaworx.cloud):
christopheresplinMTG9U7 gave 404 on the domain and 401 on user paths; chrisHVQEBL and
208pondhillrdKG8F3Z gave 200 on the same paths.
