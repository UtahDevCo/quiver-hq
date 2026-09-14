# quiver-photos-v2

Project knowledge for `projects/quiver-photos-v2`. Reachable from inside the repo
as `.brain/index.md`.

Resolve against the [meta layer](../../meta/index.md) — see
[conventions](../../conventions.md) for how `Practice Override` composes.

# Overrides

*Meta practices this project narrows, extends, replaces, or suspends. Empty.*

# Patterns

*Opt-in and portable. Empty.*

# Workflows

* [release-auto-publishes-on-tag](workflows/release-auto-publishes-on-tag.md) - Pushing a v3.* tag triggers the V3 Release workflow, which builds every platform and publishes the GitHub release directly (draft false); monitor with gh run watch.

# Failure modes

* [chrome-downloads-zero-byte-completes-as-success](failure-modes/chrome-downloads-zero-byte-completes-as-success.md) - A 200-OK empty body or a silently-served throttle/login page completes as a valid empty file, so any chrome.downloads-based downloader must guard on fileSize === 0.
* [serial-await-in-a-download-queue-lets-one-stuck-start-wedge-the-batch](failure-modes/serial-await-in-a-download-queue-lets-one-stuck-start-wedge-the-batch.md) - Awaiting chrome.downloads.download() inside the queue's dispatch loop meant one download that never started (stalled external volume) blocked every other item until a 300s downstream timeout, and a watchdog keyed on already-started downloads could not see it.
