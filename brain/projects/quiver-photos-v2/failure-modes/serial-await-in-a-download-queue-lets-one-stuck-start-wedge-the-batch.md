---
type: Failure Mode
title: A serially-awaited start in a work queue lets one stuck item wedge the whole batch
description: Awaiting chrome.downloads.download() inside the queue's dispatch loop meant one download that never started (stalled external volume) blocked every other item until a 300s downstream timeout, and a watchdog keyed on already-started downloads could not see it.
kind: failure-mode
tags: [chrome-extension, downloads, concurrency, queue, watchdog, timeout]
generated: { by: claude/opus-4.8, at: 2026-09-01T16:34:23Z }
status: stable
stale_after: 2027-09-14
sources:
  - id: evidence
    resource: projects/quiver-photos-v2/v3/internal/browser/extension/background.js
    title: processDownloadQueue / startDownloadSlot slot-reservation + start-timeout
    last_modified: 2026-09-01
  - id: commit
    resource: 1b5fac7
    title: "fix(v3): don't let one hanging chrome.downloads.download() wedge the whole batch"
    last_modified: 2026-09-01
  - id: report
    resource: Billy Hirsch 3.0.94 clean-folder log (2026-09-01)
    title: "0 completed, every item failed CHROME_DOWNLOAD_REJECTED: SLOT_WAIT_TIMEOUT, download target on an external USB volume"
    last_modified: 2026-09-01
---

# Failure Mode

A concurrency-limited work queue dispatched items with `await` on the start call
*inside the dispatch loop*:

```js
while (pending.length) {
  if (active >= MAX) break;
  const item = pending.shift();
  const id = await chrome.downloads.download(item);  // can hang forever
  active.set(id, item);
}
```

When the start itself hangs (here: `chrome.downloads.download()` to a stalled
external USB volume never resolves), the `await` blocks the loop, so no other
item is ever dispatched. Every trailing item sits in the queue until a far
downstream backstop (a 300s slot-wait timeout) rejects it. Symptom in the field:
0 completed for 25 minutes, every item failing `SLOT_WAIT_TIMEOUT`, no legible
cause.

The fix separates *reserving* the slot from *awaiting* the start. Increment an
in-flight counter synchronously, fire the start without awaiting it in the loop,
and give the start its own short deadline (30s) that frees the reserved slot and
fails just that one item:

```js
function processQueue() {
  while (pending.length) {
    if (active.size + starting >= MAX) break;
    startSlot(pending.shift());        // does not block the loop
  }
}
async function startSlot(item) {
  starting++;
  const t = setTimeout(() => { starting--; item.reject('START_TIMEOUT'); processQueue(); }, 30000);
  try { const id = await chrome.downloads.download(item);
        clearTimeout(t); starting--; active.set(id, item); processQueue(); }
  catch (e) { clearTimeout(t); starting--; item.reject(e); processQueue(); }
}
```

# Why it matters

One item that cannot make progress should cost one slot, not the whole queue.
Awaiting the start in the loop couples every item's fate to the head of the
queue. And the deadline has to sit on the *start*, not only on already-running
work: a watchdog that reconciles entries in `activeDownloads` (things that got an
id) is structurally blind to a start that never returned an id, so it early-
returns "nothing active" while the queue is fully wedged. The reservation counter
plus the start-timeout is what makes the never-started case observable and
recoverable, and it turns an opaque 5-minute stall into a fast, named failure the
log can point at (the drive).

# Evidence

Billy's 3.0.94 log: download target `/Volumes/6TB External/...`; server handed 5
items to the extension once, then `Completed: 0` held for 25 minutes while every
item failed `CHROME_DOWNLOAD_REJECTED: SLOT_WAIT_TIMEOUT: no download slot freed
within 300s`. The extension's 120s no-progress watchdog never fired because its
scan early-returns when `activeDownloads.size === 0`, and the hung starts never
populated `activeDownloads`.

not:
  - term: "rely on the existing no-progress watchdog to free the slot"
    why: "the watchdog only inspects downloads already in activeDownloads (state === 'in_progress' with no byte growth); a start that never returns an id is never in that map, so the watchdog early-returns and never acts"
    instead: "put a start deadline on the dispatch itself, tracked by a reserved-slot counter separate from activeDownloads"
  - term: "keep awaiting download() in the loop but add a downstream slot-wait timeout"
    why: "a downstream 300s backstop still lets the single hung head-of-queue block every trailing item for the full window; throughput collapses to a handful of failures per 5 minutes"
    instead: "don't await the start in the loop at all; reserve the slot synchronously and let each start settle independently"
