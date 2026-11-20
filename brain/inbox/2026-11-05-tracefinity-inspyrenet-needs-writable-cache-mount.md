---
type: Observation
title: Tracefinity image needs a writable /app/.transparent-background for InSPyReNet
description: In ghcr.io/tracefinity/tracefinity v0.10.1 every InSPyReNet trace 500s with PermissionError because the non-root container user can't write the model cache.
kind: failure-mode
proposed_layer: project
proposed_project: 3d-printing
tags: [tracefinity, docker]
generated: { by: claude/opus-5.5, at: 2026-11-05T19:36:56Z }
status: draft
sources:
  - id: image
    resource: https://github.com/tracefinity/tracefinity/blob/main/docs/gotchas.md
    title: Gotchas "Docker" section lists the world-writable dirs; .transparent-background is not among them
not:
  - term: "TRACERS=isnet,inspyrenet and nothing else"
    why: "every POST /sessions/{id}/trace with tracer=inspyrenet returns 500: PermissionError: [Errno 13] Permission denied: '/app/.transparent-background'"
    instead: "add -v <host-dir>:/app/.transparent-background"
---

# Observation

With `TRACERS=isnet,inspyrenet`, every InSPyReNet trace failed with
`PermissionError: [Errno 13] Permission denied: '/app/.transparent-background'`.
The container runs as UID 1000 and the image doesn't make that model-cache directory writable.
Mounting a host volume there fixed it. The first trace took 41s (weights download
and load), later ones about 6s, at 3.5 GB resident.

Related, same session: `birefnet-lite` OOM-killed the backend on Docker Desktop's
default ~7.75 GB VM (502 from nginx, `OOMKilled=true`). Raise Docker's memory to 10 GB+ first.

# Why it matters

The fallback for shiny tools silently doesn't exist until you read the container logs.
Worth an upstream issue (not filed).

# Evidence

`docker logs tracefinity` showed 8 identical PermissionError tracebacks, one per photo.
After restarting with `-v $PWD/tbcache:/app/.transparent-background`, InSPyReNet traced both test photos.
