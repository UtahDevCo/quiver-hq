---
type: Failure Mode
title: Android plays a notification-channel sound once — looping needs an app-owned player
description: A notification channel sound fires exactly once at the file's length; to ring for a chosen duration you loop your own audio while foregrounded or in a full-screen takeover.
kind: failure-mode
tags: [android, notifications, fcm, expo-audio, notifee, mobile]
generated: { by: claude/opus-4-8, at: 2026-09-14T18:57:15Z }
status: stable
stale_after: 2027-09-14
sources:
  - id: evidence
    resource: projects/popreminders.com/src/features/notifications/alerts.native.ts
    title: Android channel setup + foreground display path
    last_modified: 2026-09-14
  - id: alarm-player
    resource: projects/popreminders.com/src/features/notifications/alarm-player.native.ts
    title: Singleton looping alarm player
    last_modified: 2026-09-14
  - id: server-ring
    resource: projects/popreminders.com/functions/src/index.ts
    title: Server sends resolved part + ringSec in the push
    last_modified: 2026-09-14
not:
  - term: "createChannel({ ..., sound, importance: HIGH })"
    why: "channel importance/DND affect urgency, not how long the sound plays — Android still plays the file once"
    instead: "loop your own expo-audio player for ringSec while foregrounded or in a full-screen takeover"
---

# Failure Mode

Android plays a notification-channel sound **exactly once**, at the length of the
sound file. There is no channel property that loops it or controls how many
seconds it rings — `AndroidImportance`, `bypassDnd`, and the vibration pattern
change urgency and DND behavior, not sound duration.

To make an alert "ring" for a chosen duration (e.g. 10s / 30s / 60s tiers) the
app must own the audio: a looping player (`expo-audio` `createAudioPlayer` with
`loop = true`, stopped by a `setTimeout` after N seconds) that runs in a context
where audio is allowed:

- **Foregrounded**: start it from the FCM `onMessage` handler.
- **Locked screen**: start it from a full-screen takeover activity raised by a
  full-screen intent (`notifee` `fullScreenAction`) on a data-only push.

A data-only push should carry the desired ring length (Pop Reminders puts
`part` + `ringSec` in `data`) so the device knows how long to loop without
re-reading Firestore. Use one module-scope singleton player so the foreground
arrival ring and a subsequently-tapped takeover don't stack two loops.

A part with no full-screen intent (Pop Reminders' soft pre-warning) can only ring
while the app is foregrounded — on a locked screen it falls back to the single
channel ping, because nothing launches an activity to own the audio.

# Why it matters

The intuitive fix — "make the alert ring longer" — has no knob on the channel,
so time gets spent hunting for a setting that does not exist. On an unlocked
phone during hands-on testing you only ever hear the ~2s channel ping, which
reads as "the alarm feature is broken" when the takeover-only loop simply never
launched (full-screen intents fire over the lock screen, not while in use).

# Evidence

`alerts.native.ts` comment on channel setup: "Android plays one immutable sound
per channel, so the channel id IS the sound id." Channels set importance +
vibration + `bypassDnd`, never duration. The looping lives in
`alarm-player.native.ts` (`player.loop = ringSec > 0`, `setTimeout(stop, ringSec
* 1000)`), invoked from the `onMessage` handler for foreground arrivals and from
the takeover screen's `useTakeoverAlarm` for the locked path. The server resolves
`ringSec` per part and ships it in the push `data` (`functions/src/index.ts`).
