---
type: Observation
title: A property-manager name is not a property-identity signal
description: One PM runs many buildings, so matching candidates on PM-name similarity makes every building under that PM look identical.
kind: failure-mode
proposed_layer: project
proposed_project: trikin
tags: [matching, entity-resolution, imports, deal-desk]
generated: { by: claude/opus-5-5, at: 2026-09-25T20:00:53Z }
status: draft
sources:
  - id: fix
    resource: projects/trikin/web/src/lib/import/propose-matches.ts
    title: findCandidates / similarityTo (commit acb95f2)
    last_modified: 2026-09-25
  - id: test
    resource: projects/trikin/web/src/lib/import/propose-matches.test.ts
    title: "does not treat two buildings as candidates because one manager runs both"
    last_modified: 2026-09-25
not:
  - term: "similarity = max(sim(name, otherName), sim(managerName, otherManagerName))"
    why: "two different buildings under one PM score 1.00 on the PM term"
    instead: "score on property name and building/PM address; use PM name only when the row carries nothing else"
---

# Observation

In the Trikin staged-import matcher, candidate similarity took the max over property-name
pairs and PM-name pairs. Every pair of buildings under one property manager then scored
1.00 and was offered as a same-property candidate. Candidates are now scored on property
name and address, with the PM name as a fallback only for a row that has no name or address.

# Why it matters

A PM like Greystar manages dozens of Colorado properties. With a shared-PM score of 1.00,
the similarity-only fallback (no Jev key) proposes links at or above 0.92, so a reviewer
would be shown distinct buildings proposed as the same property, and one wrong approval
merges two payors' payment histories into one eligibility decision.

# Evidence

Browser validation of /admin/imports on local D1, 2026-09-25: "Millenium Green Valley
Ranch" and "Millennium Green Valley Ranch" scored 1.00 only because both rows had PM
"Millennium Mgmt". After the fix the misspelling scores 0.98 on the name, and "The
Vixen" under the same PM is no longer a candidate. The unit tests missed it because
every fixture used a distinct PM per property.
