# popreminders.com

Project knowledge for `projects/popreminders.com`. Expo SDK 57 dev-build + Firebase (pop-reminders).

Resolve against the [meta layer](../../meta/index.md) — see
[conventions](../../conventions.md) for how `Practice Override` composes.

# Overrides

*Meta practices this project narrows, extends, replaces, or suspends. Empty.*

# Patterns

*Opt-in and portable. Empty.*

# Workflows

*How to run a piece of work here. Empty.*

# Failure modes

* [collectiongroup-query-needs-collection-group-scoped-index](failure-modes/collectiongroup-query-needs-collection-group-scoped-index.md) - Firestore auto-indexes single fields at COLLECTION scope only; a collectionGroup query with a filter fails at runtime until you add a COLLECTION_GROUP fieldOverride.
* [firebase-hosting-ignore-strips-expo-font-assets](failure-modes/firebase-hosting-ignore-strips-expo-font-assets.md) - **/node_modules/** in hosting.ignore excludes exported /assets/node_modules fonts; the SPA rewrite then serves index.html as a 200 that fails to decode, so prod falls back to Times.
* [collectiongroup-query-denied-by-get-based-rule](failure-modes/collectiongroup-query-denied-by-get-based-rule.md) - Firestore can't prove a collectionGroup list is safe if the read rule uses get()/exists(); it 403s even OR'd with a query-safe clause. Use resource.data-only rules, or subscribe per-parent and merge.
* [firebase-rules-deploy-needs-serviceusage-consumer](failure-modes/firebase-rules-deploy-needs-serviceusage-consumer.md) - firebase deploy --only firestore:rules,firestore:indexes runs an API-enabled preflight against serviceusage.googleapis.com, so the SA needs roles/serviceusage.serviceUsageConsumer on top of firebaserules.admin + datastore.indexAdmin, or it 403s before deploying anything.
* [firebase-tools-emulator-needs-jdk-21](failure-modes/firebase-tools-emulator-needs-jdk-21.md) - A rules-test CI job that runs firebase emulators:exec fails at emulator start (not on any rule) because firebase-tools dropped Java <21 and GitHub's ubuntu-latest defaults to JDK 17.
* [android-channel-importance-is-immutable-after-creation](failure-modes/android-channel-importance-is-immutable-after-creation.md) - createChannel cannot raise a channel's importance later; same-id recreate is ignored and delete+recreate restores the old value, so importance bumps only take on a fresh install.
* [android-notification-channel-sound-plays-once](failure-modes/android-notification-channel-sound-plays-once.md) - A notification channel sound fires exactly once at the file's length; to ring for a chosen duration you loop your own audio while foregrounded or in a full-screen takeover.

# Practices

*Project-local rules. Empty.*

# Modules

*What the major pieces are and how they fit. Empty.*

# Invariants

*Rules with an executable check attached. Empty.*

# Decisions

*Why things are the way they are. Empty.*

# Gems

*Project-local patterns worth promoting to meta. Empty.*
