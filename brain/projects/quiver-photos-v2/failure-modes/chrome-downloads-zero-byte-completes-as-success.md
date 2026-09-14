---
type: Failure Mode
title: chrome.downloads reports a 0-byte transfer as a successful complete
description: A 200-OK empty body or a silently-served throttle/login page completes as a valid empty file, so any chrome.downloads-based downloader must guard on fileSize === 0.
kind: failure-mode
tags: [chrome-extension, downloads, error-handling, rate-limiting]
generated: { by: claude/opus-4.8, at: 2026-09-01T12:12:13Z }
status: stable
stale_after: 2027-09-14
sources:
  - id: evidence
    resource: projects/quiver-photos-v2/v3/internal/browser/extension/background.js
    title: 0-byte guard in the download-complete handler
    last_modified: 2026-09-01
  - id: commit
    resource: 91a19d5ea525e49d3c55fe3424303a9aedd69cd0
    title: "feat(v3): make 0-byte downloads legible (instrumentation + guard)"
    last_modified: 2026-09-01
---

# Failure Mode

`chrome.downloads.download()` fires `onChanged` with `state.current === 'complete'`
even when the download transferred 0 bytes. A server that returns 200 OK with an
empty body, or that silently serves a throttle / login / error page, produces a
`complete` download whose `fileSize` is 0. Chrome treats that as success, not an
error.

Any downloader built on `chrome.downloads` must therefore guard on
`fileSize === 0` (equivalently `bytesReceived === 0`) inside the
`onChanged('complete')` handler and treat it as a failure with a distinct,
greppable error, rather than reporting the empty file as a downloaded item.

The watchdog that cancels a download stuck `in_progress` with no byte progress does
NOT cover this case: that path only catches connections held open with zero bytes,
never a download that *completes* empty. The two failure modes need separate
handling — the watchdog for the held-open case, the fileSize guard for the
completed-empty case.

# Why it matters

Without the guard, a bad, expired, or rate-limited URL surfaces as a phantom
success: an empty file lands on disk, the item is marked downloaded, and the real
failure mode is invisible in the logs. In Quiver Photos v3 this produced the
large-library symptom "queues but 0 complete" with no legible cause: every
media-page re-scrape was throttled by Google, `extractMediaUrls` fell back to an
unsigned `lh3.googleusercontent.com/{id}=d` URL, and Chrome downloaded 0 bytes and
called it done. The user saw a stalled backup; the app saw successes. A checker or
a "downloaded" flag built on that success signal is measuring nothing.

# Evidence

The fix reports `ZERO_BYTE_DOWNLOAD` from the complete handler, mirroring the
existing interrupted-download failure path, and routes scrape failures to the app
log so the throttling signature is visible:

```javascript
// onChanged('complete'), after chrome.downloads.search returns the record:
if (!download.fileSize) {
  const urlSource = req.usedScrapedUrl ? 'scraped' : 'fallback';
  sendBgExtensionLog('Download completed with 0 bytes (url=' + urlSource +
    '); treating as failed: ' + req.id.substring(0, 20), 'error', 'download');
  reportDownloadResult({
    id: req.id, success: false,
    error: 'ZERO_BYTE_DOWNLOAD: completed with 0 bytes (url=' + urlSource + ')',
    url: req.url, mediaPageUrl: req.mediaPageUrl || ''
  });
  activeDownloads.delete(delta.id);
  processDownloadQueue();
  return;
}
```

# Notes

`not:` below records the tempting-but-wrong reads.

not:
  - term: "rely on the no-progress watchdog to catch empty downloads"
    why: "the watchdog only fires for downloads stuck in_progress with no bytes; a download that completes at 0 bytes is never in_progress long enough to trip it"
    instead: "guard fileSize === 0 in the onChanged('complete') handler, separately from the watchdog"
  - term: "trust state.current === 'complete' as download success"
    why: "Chrome completes a 200-OK empty body or a served error/login page as success with fileSize 0"
    instead: "treat a complete with fileSize === 0 as a failure"
