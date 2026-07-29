# references

Executable material referenced by `type: Invariant` concepts. Per OKF §10, an
invariant carries a `computation` (what to check) and an `attester` (how to judge
the receipt). Nothing here uses an LLM — attestation is deterministic or it is
worthless.

The receipt shape is fixed in [conventions](../conventions.md):

```json
{ "command": "<the exact command run>", "exit_code": 0, "matches": [] }
```

# Attesters

* [expect_empty.py](expect_empty.py) - Passes when `matches` is empty. Three-valued: 0 PASS, 1 VIOLATED, 2 ERROR — because "the check ran and found a violation" and "the check could not run" are different findings.

# Checks

* [checks/zamp-no-new-deprecated-ui-imports.sh](checks/zamp-no-new-deprecated-ui-imports.sh) - Diff-scoped grep for newly added `@util/ui` and `Rt*` imports in zamp. Enforces [no-new-deprecated-ui-imports](../projects/zamp/invariants/no-new-deprecated-ui-imports.md).
* [checks/zamp-sharded-companyid.py](checks/zamp-sharded-companyid.py) - Brace-matching check that every Prisma call on a sharded table carries `companyId` at depth 1 of `where`/`data`. Derives the model list from `@shardKey` and fails on drift from `SHARDED_TABLES`. Enforces [sharded-tables-companyid](../projects/zamp/invariants/sharded-tables-companyid.md).

# Writing a check

1. **Take both diff ends as parameters.** Project repos are shared working trees;
   a check that requires checking something out to test will never be tested.
2. **Emit the receipt and exit 0.** Signal check failure through the receipt's
   `exit_code` field, not the process exit — otherwise the attester cannot tell a
   violation from a crash.
3. **Validate against real history, both directions.** Find a commit that
   introduced the violation *and* one that removed it. `git log -S` counts
   occurrence changes in either direction, so a commit it reports as "adding" may
   have removed — that alone produced a false negative here.
4. **Write a negative control** for every near-miss the pattern must ignore
   (`@util/ui-templates` vs `@util/ui`).
5. **Never loosen a check to make it pass.** Report "sanctioned check failed to
   run" instead.
6. **Report coverage in the receipt.** Put counts in a `coverage` object; the
   attester prints it. A `PASS` with no coverage figure reads as "checked
   everything" when it may mean "checked almost nothing" —
   [audits-must-report-their-own-coverage](../meta/failure-modes/audits-must-report-their-own-coverage.md).
7. **Three outcomes, not two.** Anything the check cannot *prove* is a violation is
   `skipped`, not `matches`. A check that reports plausible-but-unproven findings
   gets ignored, and then it protects nothing. The shard check's first run produced
   four such false positives.
