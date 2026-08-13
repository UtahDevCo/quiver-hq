---
type: Failure Mode
title: A missing runtime secret ships a healthy build with the feature inert
description: A feature that falls back by design, plus a config file the platform never reads, produces a green deploy and a passing smoke test with nothing switched on.
tags: [deployment, configuration, feature-flags, firebase, observability, monorepo]
generated: { by: claude/opus-5, at: 2026-07-31T13:31:08Z }
status: stable
stale_after: 2027-08-13
not:
  - term: "adding the runtime secret and flag to the apphosting.yaml at the repo's web root"
    why: "the backend's codebase.rootDirectory is /web/apps/web, so that file is only read by the source-deploy path; every git rollout parsed the other copy and the drift produced no warning from either side"
    instead: "confirm which config the platform parses (App Hosting: the backend's rootDirectory, readable from the builds API), change that one first, and have the feature log once at startup when it is disabled and why"
  - term: "treating a passing smoke test as evidence the feature is on"
    why: "an additive feature falls through to the previous code path, and the fall-through answer looks like a normal answer"
    instead: "assert on something only the new path can produce, or read the startup line that names the disabled state"
  - term: "asserting a platform default in a comment without reading it back"
    why: "I wrote that the request timeout was 60s and every request would fail; the running service reported 300s and the parsed build config set no timeout at all"
    instead: "read the deployed service's own configuration before building an argument on top of a documented default"
sources:
  - id: shipped
    resource: "projects/k1/web/apps/web/apphosting.yaml:89-102"
    title: the file a git rollout reads, where the panel config had to go
    author: claude/opus-5
    last_modified: 2026-07-31
  - id: ignored
    resource: "projects/k1/web/apphosting.yaml:1-9"
    title: the copy that is only reachable through npm run deploy:hosting, now carrying a header saying so
    author: claude/opus-5
    last_modified: 2026-07-31
  - id: fix
    resource: "projects/k1 commit 707bf64"
    title: "fix(deploy): put the panel config in the apphosting.yaml that actually ships"
    author: claude/opus-5
    last_modified: 2026-07-31
---

# The trap

Three things combined to deploy a release that served no part of the feature it was
released for, while every signal read green.

The feature needed two provider secrets and a flag. Its composer returns null unless
at least two distinct provider/model pairs are reachable, and its trigger checks the
flag first and returns null on its own. Both behaviours are deliberate, because the
feature is additive and falls through to the previous code path.

The config went into the wrong file. The monorepo had `apphosting.yaml` at two
levels and the platform backend's `rootDirectory` pointed at the inner one. Nothing
validates that the two agree.

Referencing a secret that is not granted, or omitting a variable a running service
needs, is not a build error. The build succeeded, the service was healthy, and the
smoke test passed because the fall-through answer is shaped like a real answer.

# Why nothing caught it

Every check available reported success. The only way to find this was to compare the
parsed build config against what the code requires, which is not a step anybody
performs by habit.

Two countermeasures, in order of value. The feature should log once at startup that
it is disabled and name the missing input, which turns an invisible state into a
greppable line. And when a platform reads one of several candidate config files, the
unread copies need a header saying which one ships, because the next person to add a
variable will open whichever they find first.

# Evidence

The header now on the unread copy:

```
# NOT the file App Hosting reads for a git rollout. The k1-backend backend has
# `rootDirectory: /web/apps/web`, so `apps/web/apphosting.yaml` is what every build
# to date has actually parsed
```

Listing rollouts and reading the parsed config needs the REST API, because the CLI
has no `apphosting:rollouts:list`:

```
GET firebaseapphosting.googleapis.com/v1beta/projects/{p}/locations/{l}/backends/{b}/rollouts
```

The same investigation carried the mirror error. I asserted the platform's default
request timeout was 60s and that every request would therefore fail, and it was
already written into a code comment before it was checked. The running service
reported 300s. That is
[probe-before-trusting-an-api-claim](probe-before-trusting-an-api-claim.md), and the
inert deploy itself is
[verify-a-write-actually-happened](verify-a-write-actually-happened.md) applied to
configuration.
