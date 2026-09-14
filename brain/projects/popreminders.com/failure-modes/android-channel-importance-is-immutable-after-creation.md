---
type: Failure Mode
title: Android notification-channel importance is frozen after first creation
description: createChannel cannot raise a channel's importance later; same-id recreate is ignored and delete+recreate restores the old value, so importance bumps only take on a fresh install.
kind: failure-mode
tags: [android, notifications, notifee, channels, mobile]
generated: { by: claude/opus-4-8, at: 2026-09-14T19:30:55Z }
status: stable
stale_after: 2027-09-14
sources:
  - id: evidence
    resource: projects/popreminders.com/src/features/notifications/alerts.native.ts
    title: IMPORTANCE map + ensureAlertChannels upsert-on-launch
    last_modified: 2026-09-14
---

# Failure Mode

Android fixes a notification channel's importance when the channel is first
created. Raising `importance` in code and re-running `createChannel` with the same
id does nothing — Android ignores importance changes to an existing channel (the
user may only lower it). Deleting the channel and recreating it with the same id
does not reset it either: Android remembers deleted channels and restores the
prior importance to stop apps from doing exactly that.

Consequence: a change like `DEFAULT -> HIGH` (needed so a full-screen intent can
launch over the lock screen) takes effect only on a **fresh install** or after the
user clears the app's data. A JS/OTA reload on an existing install keeps the old
importance, so the new behavior silently doesn't appear.

To change importance for already-installed users without a reinstall, you must use
a **new channel id** (version the id, e.g. append a suffix) and point the push's
`channelId` at the new channel.

# Why it matters

You bump importance, reload, test, and see no change — then waste time looking for
a bug in the push payload or the full-screen-intent code when the real cause is
that the channel was created once at the old importance and is now immutable. In a
shipped app, existing users never get the upgraded behavior unless the channel id
changes; only new installs do.

# Evidence

Pop Reminders creates one channel per catalog sound on every launch via
`ensureAlertChannels()` (`createChannel` is described in-code as an idempotent
upsert). Changing the `IMPORTANCE` map from `{ soft: DEFAULT, medium: DEFAULT,
loud: HIGH }` to all-`HIGH` so every alert could raise the lock-screen takeover
had no effect on the developer's existing install; the fix required uninstalling
and reinstalling the dev build so the channels were created fresh at HIGH.
