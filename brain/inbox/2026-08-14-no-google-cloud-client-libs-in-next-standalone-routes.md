---
type: Observation
title: Don't import @google-cloud/* gRPC clients into a Next standalone route
description: Next's standalone tracer skips the client's dynamically-loaded gRPC config JSON, so the route builds green then 500s with MODULE_NOT_FOUND at runtime; use the REST API instead.
kind: failure-mode
proposed_layer: meta
proposed_project: k1
tags: [nextjs, cloud-run, app-hosting, google-cloud, standalone, bundling]
generated: { by: claude/opus-4-8, at: 2026-08-14T19:11:07Z }
status: draft
sources:
  - id: evidence
    resource: projects/k1/web/apps/web/lib/server/drain-task-enqueue.ts
    title: Cloud Tasks enqueue rewritten to REST after the client library failed at runtime
    last_modified: 2026-08-14
  - id: commit
    resource: projects/k1
    title: "a49976a fix(ingest): enqueue drain tasks via REST, drop @google-cloud/tasks"
    last_modified: 2026-08-14
---

# Observation

In a Next.js app built with `output: "standalone"` (Firebase App Hosting / Cloud Run),
do not import `@google-cloud/tasks` — or any of the google-cloud gRPC client libraries
that load config JSON through a dynamic path — into a route or anything a route imports.

The build succeeds. At runtime the route throws `MODULE_NOT_FOUND` on the first request,
because Next's standalone file tracer does not copy the client's dynamically-referenced
files into `.next/standalone/node_modules`. Observed missing:
`@google-cloud/tasks/build/esm/src/v2/cloud_tasks_client_config.json` and
`json-helper.cjs`.

Enqueue Cloud Tasks over the REST API instead, dropping the client dependency entirely:
`POST https://cloudtasks.googleapis.com/v2/{parent}/tasks` with an OAuth access token from
the Cloud Run metadata server
(`http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token`,
header `Metadata-Flavor: Google`). Pure `fetch`, nothing for the tracer to miss.

# Why it matters

The failure is invisible until production traffic hits the route: `tsc`, `next build`, and
the App Hosting rollout all report success. Two deploys were burned here — build-2026-08-14-003
built clean and then returned HTTP 500 (plain "Internal Server Error", not the route's own
JSON, because the module fails at import before the handler runs) on every call. On a
`minInstances: 0` service there is no long-lived process to surface the crash earlier.

The trap within the trap: `serverExternalPackages` (Next config) fixes the *build-time*
"Collecting page data" MODULE_NOT_FOUND by keeping the package unbundled, which makes the
build pass — and looks like the fix — but it does NOT close the *runtime* standalone-trace
gap, so the 500s persist. The build-time symptom and the runtime symptom are the same error
string in two different phases.

# Evidence

build-2026-08-14-002 (bundled): failed at build, "Collecting page data ... Cannot find module
'.../cloud_tasks_client_config.json'".
build-2026-08-14-003 (serverExternalPackages added): built READY, then runtime logs showed
`⨯ Error: Cannot find module '/workspace/web/apps/web/.next/standalone/node_modules/@google-cloud/tasks/build/esm/src/v2/cloud_tasks_client_config.json'` and every `POST /api/tasks/drain-project` returned 500.
build-2026-08-14-004 (REST + metadata token, dependency removed): route returns a clean 401
fail-closed and later drained a 29-doc chain end to end.

# not

- term: "import { CloudTasksClient } from '@google-cloud/tasks' at module scope in a route"
  why: "standalone tracer omits its dynamic gRPC config JSON; green build, runtime 500"
  instead: "POST the Cloud Tasks REST API with a metadata-server access token"
- term: "serverExternalPackages: ['@google-cloud/tasks'] as the fix"
  why: "fixes the build-time collect-page-data error but not the runtime trace gap"
  instead: "remove the client library; call REST over fetch"
