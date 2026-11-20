---
type: Observation
title: A force-stopped app gets no data-only FCM; alarm apps must schedule on-device
description: Data-only FCM never reaches a force-stopped Android app, so an alarm can't depend on a push. Schedule locally via AlarmManager (notifee trigger) so it fires killed/offline.
kind: failure-mode
proposed_layer: project
proposed_project: popreminders.com
tags: [android, ios, fcm, notifications, alarms, notifee]
generated: { by: claude/opus-4-8, at: 2026-09-17T00:25:14Z }
status: draft
sources:
  - id: notify
    resource: projects/popreminders.com/functions/src/nudge/notify.ts
    title: pushToUser — Android data-only path (no notification key)
    last_modified: 2026-09-17
  - id: scheduler
    resource: projects/popreminders.com/src/features/notifications/alarm-scheduler.native.ts
    title: on-device AlarmManager scheduling that replaced the push reliance
    last_modified: 2026-09-17
---

# Observation

Pop Reminders sent Android alerts as a **data-only** FCM message (no `notification`
key) so the app's `setBackgroundMessageHandler` could draw a notifee full-screen
takeover. Symptom: a reminder set 2 minutes out produced no alert at fire time, but
opening the app later routed straight to the alert screen.

Root cause: Android does **not** deliver FCM to a **force-stopped** app (swiped away
from recents, or OS-killed). A data-only message has no OS-drawn fallback, so nothing
happens; the message delivers only when the app is next launched, which is why it
"appeared" on open. An app that was merely backgrounded (not force-stopped) still ran
its handler, so the same alarm worked overnight — the difference was force-stop, not
timing.

The fix is to stop depending on a live push for the alert: schedule the alarm
**on the device** with `notifee.createTriggerNotification(..., { type: TIMESTAMP,
alarmManager: { type: SET_ALARM_CLOCK } })`. AlarmManager fires at the exact time even
when the app is force-killed, in Doze, and offline, and can still raise a full-screen
intent. Drive scheduling off the existing Firestore listener and reconcile (cancel
extras, create missing) on snapshot change and on foreground.

iOS has the same shape with weaker guarantees: no AlarmManager and no screen takeover
(Time Sensitive is the ceiling; Critical Alerts denied). Schedule a local
`UNUserNotificationCenter` notification (same notifee call, `alarmManager` ignored)
as the primary, and keep the server APNs push as the backstop that reaches a phone
that was **off and comes back online** — the one case local scheduling misses. A
fully powered-off iPhone at the exact fire time has no third-party fix.

# Why it matters

An alarm/reminder app whose delivery depends on a push silently fails for every user
who swipes it away, which is normal user behavior. The failure is invisible in
testing if you only background the app; it only shows when you force-stop. Getting
this wrong means the product's core promise (fire on time) breaks for a large,
unmeasured fraction of users.

# Evidence

`functions/src/nudge/notify.ts` built the Android message with no `notification`
key and `android: { priority: 'high' }`, relying on the app handler. Replaced the
reliance with `src/features/notifications/alarm-scheduler.native.ts`
(`SET_ALARM_CLOCK` triggers, reconciled against `getTriggerNotificationIds()`).
The server now sets `skipAndroid` on the assignee push to avoid double-alerting the
self-scheduling Android device, while keeping the iOS push as the offline backstop.

# Related

The exact-alarm special access (Android 12+ "Alarms & reminders",
`SCHEDULE_EXACT_ALARM`) must be granted or `SET_ALARM_CLOCK` can't fire exactly; it
is off by default and needs a prompt via `notifee.openAlarmPermissionSettings()`.

not:
  - term: "Add an android.notification payload so a killed app still gets a tray notification"
    why: "the OS then draws the notification for every non-foreground state and never calls the app handler, so the full-screen takeover is lost even when the app is alive-but-backgrounded — a regression of the one case that worked"
    instead: "schedule the alarm on-device with AlarmManager so it fires killed/offline AND still raises the takeover"
