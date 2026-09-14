---
type: Failure Mode
title: Firebase Hosting ignore glob strips Expo web font assets
description: "**/node_modules/** in hosting.ignore excludes exported /assets/node_modules fonts; the SPA rewrite then serves index.html as a 200 that fails to decode, so prod falls back to Times."
kind: failure-mode
tags: [firebase-hosting, expo-web, fonts, spa-rewrite, deploy]
generated: { by: claude/opus-4.8, at: 2026-09-02T17:16:39Z }
status: stable
stale_after: 2027-09-14
sources:
  - id: fix-commit
    resource: projects/popreminders.com/firebase.json
    title: hosting.ignore changed from ["firebase.json","**/.*","**/node_modules/**"] to ["firebase.json","**/.*"]
    last_modified: 2026-09-02
  - id: font-family-names
    resource: projects/popreminders.com/src/theme/tokens.ts
    title: weight-specific @expo-google-fonts family names (PlusJakartaSans_800ExtraBold etc.)
    last_modified: 2026-09-02
---

# Failure Mode

Firebase Hosting's conventional `hosting.ignore` entry `"**/node_modules/**"` also
matches the Expo/Metro web-export asset path, because `expo export -p web` emits
bundled fonts to `dist/assets/node_modules/@expo-google-fonts/<family>/<weight>/*.ttf`.
The glob excludes every font `.ttf` from the upload. The now-missing font URLs fall
through the SPA catch-all rewrite (`{ "source": "**", "destination": "/index.html" }`)
and return `index.html`: an HTTP **200** with `content-type: text/html` that the
browser cannot decode as a font, so `@font-face` entries end in `status: "error"` and
text falls back to the UA serif (Times) — on production only.

Fix: drop `"**/node_modules/**"` from `hosting.ignore` when `public` is the build
output dir (`dist`), which has no real dependency tree — the glob only ever matched
the exported assets.

# Why it matters

The failure is invisible in every pre-deploy check. It typechecks, builds, and works
on the local dev server (which serves the files straight from disk). It only breaks on
Firebase Hosting, and it breaks quietly: a 200 status looks healthy in the Network
tab, the font row even shows "(disk cache)", and nothing errors in the console. The
only visible symptom is that headings render in Times. Two signals confirm it fast:
`[...document.fonts].map(f => f.status)` shows `"error"` for every face, and the
deploy log's file count drops (here 65 → 17 when the glob was active).

# Evidence

Diagnosis run against `https://pop-reminders.web.app` after a deploy:

```js
// document.fonts: all five faces "error" despite Network showing 200s
["PlusJakartaSans_500Medium:error", ... "JetBrainsMono_600SemiBold:error"]

// fetching the .ttf URL directly:
{ status: 200, contentType: "text/html; charset=utf-8", bytes: 35006, magic: "<!DO" }
// i.e. index.html, not a font. Valid TTF starts with magic bytes 00010000.
```

After removing the glob and redeploying (`firebase deploy --only hosting`):

```
i hosting: found 65 files in dist   // was 17
// same fetch now: { status: 200, contentType: "font/ttf", bytes: 94780, magicHex: "00010000" }
// document.fonts: all five "loaded"; document.fonts.check('16px "PlusJakartaSans_800ExtraBold"') === true
```

`dist/assets/node_modules/@expo-google-fonts/plus-jakarta-sans/800ExtraBold/PlusJakartaSans_800ExtraBold.<hash>.ttf`
existed locally (94780 bytes) the whole time — the deploy skipped it, it did not fail
to build.

not:
  - term: "trust a 200 in the Network tab as proof the font served"
    why: "the SPA catch-all rewrite returns index.html with 200 + text/html for any missing asset path"
    instead: "check content-type is font/* and the magic bytes are 00010000, or check document.fonts status === 'loaded'"
  - term: "keep the default hosting.ignore ['firebase.json','**/.*','**/node_modules/**'] when public is a build dir"
    why: "the glob matches exported /assets/node_modules/** and silently drops those files from the deploy"
    instead: "['firebase.json','**/.*'] — the build output dir has no real dependency tree to exclude"
