---
type: Observation
title: NEXT_PUBLIC_* is empty in Wiley server code; build URLs from request headers
description: In Wiley's App Hosting build, process.env.NEXT_PUBLIC_APP_URL is empty at runtime in route handlers/server actions, so links/redirects must come from x-forwarded-host, not the env var.
kind: failure-mode
proposed_layer: project
proposed_project: wiley
tags: [nextjs, apphosting, env-vars, ssr, wiley, gotcha]
generated: { by: claude/opus-4.8, at: 2026-09-18T17:04:11Z }
status: draft
sources:
  - id: symptom
    resource: "GET https://app.wileyphone.com/api/verify-billing-email?token=bogus"
    title: "307 redirected to https://0.0.0.0:8080/... (container bind addr) instead of the public host"
    last_modified: 2026-09-18
  - id: fix
    resource: projects/wiley/web/lib/request-url.ts
    title: "publicBaseUrl(): reads x-forwarded-host/x-forwarded-proto via next/headers"
    last_modified: 2026-09-18
  - id: apphosting-config
    resource: projects/wiley/web/apphosting.yaml
    title: "NEXT_PUBLIC_APP_URL declared with availability [BUILD, RUNTIME], value https://app.wileyphone.com"
    last_modified: 2026-09-18
  - id: also-affected
    resource: projects/wiley/web/app/actions/account-links.ts
    title: "buildJoinUrl had the same bug — invite links fell back to http://localhost:3600"
    last_modified: 2026-09-18
---

# Observation

In Wiley's Firebase App Hosting deployment, `process.env.NEXT_PUBLIC_APP_URL` is
**empty at runtime in server code** (route handlers and server actions), even
though `apphosting.yaml` declares it with `availability: [BUILD, RUNTIME]` and a
value of `https://app.wileyphone.com`. `NEXT_PUBLIC_*` vars are inlined by Next at
**build** time; the App Hosting build did not inline a usable value here, and the
`RUNTIME` flag can't rescue a reference Next already replaced.

For any server-side absolute URL (emailed links, redirects), derive the origin
from the request instead of the env var:

```ts
// lib/request-url.ts
export async function publicBaseUrl(): Promise<string> {
  const h = await headers();               // next/headers, request scope only
  const host = h.get("x-forwarded-host") ?? h.get("host");
  const proto = h.get("x-forwarded-proto") ?? "https";
  if (host) return `${proto}://${host}`.replace(/\/$/, "");
  return (process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3600").replace(/\/$/, "");
}
```

# Why it matters

Two user-facing flows shipped broken before this was caught:

- Billing-email verification: the emailed confirm link and the post-click redirect
  both resolved to `http://localhost:3600` / the container's `https://0.0.0.0:8080`,
  so clicking the link went nowhere.
- account-links invites (`buildJoinUrl`): join links in invite emails pointed at
  `http://localhost:3600/join?token=...` in production.

A build that "compiles and deploys" hides this — it only surfaces when you hit the
live endpoint and read the `Location` header. Always test the actual served URL.

# Evidence

`curl -s -o /dev/null -w "%{redirect_url}" https://app.wileyphone.com/api/verify-billing-email?token=bogus`
returned `https://0.0.0.0:8080/billing-email-verified?status=invalid` on the
env-var version, and `https://app.wileyphone.com/billing-email-verified?status=invalid`
after switching to the header-based `publicBaseUrl()` (serving build hash matched
the fix commit via Cloud Run).

# not

- term: "process.env.NEXT_PUBLIC_APP_URL for a server-side link/redirect on App Hosting"
  why: "inlined at build as empty here; falls back to localhost / 0.0.0.0:8080 in prod"
  instead: "derive origin from x-forwarded-host/proto via a publicBaseUrl() helper"
- term: "trust a green build + successful rollout to mean the link works"
  why: "the URL bug only appears at runtime in the Location header"
  instead: "curl the live endpoint and inspect the redirect_url / emailed link"
