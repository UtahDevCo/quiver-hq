---
type: Observation
title: iOS plays a notification sound once (30s cap); burst notifications to ring longer
description: A UN notification's sound plays once and is capped at 30s with no loop. To ring an alarm for a chosen duration on iOS, schedule a burst of notifications spaced by the sound length.
kind: failure-mode
proposed_layer: project
proposed_project: popreminders.com
tags: [ios, notifications, notifee, alarms]
generated: { by: claude/opus-4-8, at: 2026-09-18T21:31:41Z }
status: draft
sources:
  - id: scheduler
    resource: projects/popreminders.com/src/features/notifications/alarm-scheduler.native.ts
    title: expandForPlatform — iOS repeat burst covering ringSec
    last_modified: 2026-09-18
---

# Observation

On iOS a `UNNotificationSound` plays **once** when the notification is delivered and
is capped at ~30 seconds; there is no loop or "ring for N seconds" option. So an
alarm notification is a single short ping regardless of any intended ring duration.
Android is different: a full-screen-intent takeover can launch a looping audio
player, so the same `ringSec` rings fully there.

To make an iOS alert ring for a chosen duration, schedule a **burst** of
notifications a few seconds apart (each re-fires the sound) covering the duration,
e.g. `count = clamp(round(ringSec / repeatSec), 1, max)` at `fireAt + i*repeatSec`.
Group them under a shared `threadId` so Notification Center collapses the burst into
one expandable stack instead of a row per ping.

# Why it matters

An alarm app that sets a `ringSec` and assumes the sound honors it will silently be
wrong on iOS — the alert is a 1–3 second ping, easy to miss. The fix is a scheduling
pattern, not an audio-length change (a longer bundled sound still caps at 30s and
bloats the binary).

# Evidence

Pop Reminders' on-device scheduler builds logical alarms with a `ringSec`; Android
schedules one notification and rings via a looping player, while
`expandForPlatform` fans each iOS alarm into `IOS_MAX_REPEATS` notifications
`IOS_REPEAT_SEC` apart. iOS keeps only ~64 pending notifications total, so bursts
plus a nudge series can exceed the cap — iOS keeps the soonest, and the foreground
re-sync reschedules as far alarms become imminent; the server APNs push is the
backstop.

not:
  - term: "Set a longer ringSec / bundle a 60s iOS sound so the notification rings longer"
    why: "iOS caps a notification sound at 30s and plays it once; a longer file just gets truncated and bloats the app"
    instead: "schedule a burst of notifications spaced by the sound length to cover the duration"
