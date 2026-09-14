---
type: Failure Mode
title: firebase-tools Firestore emulator needs JDK 21+; ubuntu-latest ships 17
description: A rules-test CI job that runs firebase emulators:exec fails at emulator start (not on any rule) because firebase-tools dropped Java <21 and GitHub's ubuntu-latest defaults to JDK 17.
kind: failure-mode
tags: [ci, github-actions, firebase, firestore-emulator, java]
generated: { by: claude/opus-4.8, at: 2026-09-03T13:06:03Z }
status: stable
stale_after: 2027-09-14
sources:
  - id: workflow
    resource: projects/popreminders.com/.github/workflows/deploy-firestore.yml
    title: deploy-firestore.yml adds actions/setup-java@v4 temurin 21 before the emulators:exec step
    last_modified: 2026-09-03
  - id: failing-run
    resource: https://github.com/deltaepsilon/popreminders.com/actions/runs/33717592567
    title: CI run that failed at "Run rules tests against the Firestore emulator" with the Java-version error
    last_modified: 2026-09-03
---

# Failure Mode

`firebase-tools` no longer supports Java versions before 21. The Firestore emulator
(started by `firebase emulators:exec ... "node scripts/test-rules.mjs"`) now exits 1
immediately with:

```
Error: firebase-tools no longer supports Java version before 21. Please install a JDK
at version 21 or above to get a compatible runtime.
```

This happens **before any test assertion runs**. GitHub Actions `ubuntu-latest`
defaults to JDK 17, so a rules-test job that only does `setup-node` + `npm ci` +
`npm run test:rules` fails at the emulator-start step.

Fix: add a JDK 21 step before the emulator runs.

```yaml
- uses: actions/setup-java@v4
  with:
    distribution: 'temurin'
    java-version: '21'
```

# Why it matters

The failure surfaces on the same CI step that runs the rules assertions ("Run rules
tests against the Firestore emulator"), so it reads as a rules-test failure — you go
looking at `firestore.rules` and the test script when the error line actually names
Java. Cost here: one wasted CI round and a few minutes of looking in the wrong file.
The tell is in the log text, not the step name.

# Evidence

Run 33717592567 failed at the emulator step with the Java-version error; adding
`setup-java@v4` temurin 21 turned the job green on the next run (rules tests passed in
~1m). Local `npm run test:rules` on a machine without any JDK shows the sibling error
("Unable to locate a Java Runtime"), confirming the emulator needs a JDK present and
≥21, independent of the rules content.

not:
  - term: "setup-node + npm ci + npm run test:rules, trusting ubuntu-latest's default Java"
    why: "ubuntu-latest defaults to JDK 17; firebase-tools' emulator rejects <21 and exits before testing"
    instead: "add actions/setup-java@v4 (temurin, java-version 21) before the emulators:exec step"
