---
type: Observation
title: A missing runtime secret ships a healthy build with the feature inert
description: A feature that falls back by design plus a config file the platform never reads equals a green deploy, a passing smoke test, and nothing switched on.
kind: failure-mode
proposed_layer: meta
observed_in: k1
tags: [deployment, configuration, feature-flags, firebase, observability]
status: draft
not:
  - term: "add the runtime secret and flag to the apphosting.yaml at the repo's web root"
    why: "the backend's codebase.rootDirectory is /web/apps/web, so that file is only read by the source-deploy path — every git rollout parsed the other copy, and the drift produced no warning from either side"
    instead: "confirm which config the platform actually parses (App Hosting: the backend's rootDirectory, readable from the builds API), change that one first, and have the feature log once at startup when it is disabled and why"
generated: { by: claude/opus-5, at: 2026-07-31T13:31:08Z }
sources:
  - { id: shipped, resource: "projects/k1/web/apps/web/apphosting.yaml:89-102", title: "the file a git rollout reads; where the panel config had to go" }
  - { id: ignored, resource: "projects/k1/web/apphosting.yaml:1-9", title: "the copy that is only reachable through npm run deploy:hosting, now carrying a header saying so" }
  - { id: fix, resource: "projects/k1 commit 707bf64", title: "fix(deploy): put the panel config in the apphosting.yaml that actually ships" }
---

# Observation

Three things combined to deploy a release that served no part of the feature it
was released for, while every signal read green.

The feature needed two provider secrets and a flag. Its composer returns null
unless at least two distinct provider/model pairs are reachable, and its trigger
checks the flag first and returns null on its own. Both behaviours are correct and
deliberate: the feature is additive and falls through to the previous code path.

The config went into the wrong file. A monorepo had `apphosting.yaml` at two
levels, and the platform backend's `rootDirectory` pointed at the inner one.
Nothing validates that the two agree.

Referencing a secret that is not granted, or omitting a variable a running service
needs, is not a build error. The build succeeded, the service was healthy, and the
smoke test passed because the fall-through answer looks like a normal answer.

# Why it matters

Every check available reported success, so the only way to find this was to
compare the parsed build config against what the code requires. That is not a step
anybody performs by habit.

Two countermeasures, in order of value. First, the feature should log once at
startup that it is disabled and name the missing input, which converts an
invisible state into a greppable line. Second, when a platform reads one of
several candidate config files, the unread copies need a header saying which one
ships, because the next person to add a variable will open whichever they find
first.

A related trap in the same investigation: I asserted that the platform's default
request timeout was 60s and that every request would therefore fail. The running
service reported 300s and the parsed build config set no timeout at all. Asserting
a platform default without reading it back is the same error in the opposite
direction, and it was already written into a code comment before it was checked.

Related: [[probe-before-trusting-an-api-claim]] and
[[verify-a-write-actually-happened]].

# Evidence

The header now on the unread copy:

```
# NOT the file App Hosting reads for a git rollout. The k1-backend backend has
# `rootDirectory: /web/apps/web`, so `apps/web/apphosting.yaml` is what every build
# to date has actually parsed
```

Listing rollouts and reading the parsed config needs the REST API. The CLI has no
`apphosting:rollouts:list`:

```
GET firebaseapphosting.googleapis.com/v1beta/projects/{p}/locations/{l}/backends/{b}/rollouts
```
