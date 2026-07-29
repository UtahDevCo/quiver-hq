#!/usr/bin/env python3
"""Computation for /projects/zamp/invariants/sharded-tables-companyid.md

Every Prisma operation on a sharded table must carry `companyId` at the TOP LEVEL
of `where` (reads/updates/deletes), `data` (create/createMany), or both `where` and
`create` (upsert). A companyId on a nested relation does not route the query.

    usage: zamp-sharded-companyid.py [base-ref] [head-ref]
           defaults: origin/master HEAD

Emits an OKF receipt on stdout; pipe into references/expect_empty.py.

Design notes, because the honest limits are the point:

* Diff-scoped to files under domains/**/*.ts — the authoritative scope from
  .coderabbit.yaml. A violation is only reported when the call site overlaps a line
  the diff added, so pre-existing debt doesn't fail every run.
* The sharded-model list is derived from @shardKey in the Prisma schema AND
  cross-checked against SHARDED_TABLES. Disagreement is an ERROR, not a pass —
  if the two sources have drifted, no verdict from this check is trustworthy.
* A spread at the top level of where/data (`...filter`) is recorded as SKIPPED, not
  as a violation. shard-safety-reviewer permits companyId "via spread of an object
  that provably contains it", and proving that requires type information this check
  does not have. Reporting them as violations would train people to ignore it.
* Raw SQL ($queryRaw/$executeRaw) is out of scope and counted as skipped.

Coverage counts ride along in the receipt so a clean run cannot be mistaken for
full coverage.
"""
import json
import os
import re
import subprocess
import sys

REPO = os.environ.get("ZAMP_REPO", os.path.expanduser("~/dev/quiver-hq/projects/zamp"))

WHERE_OPS = {
    "findFirst", "findFirstOrThrow", "findUnique", "findUniqueOrThrow", "findMany",
    "update", "updateMany", "delete", "deleteMany", "count", "aggregate", "groupBy",
}
DATA_OPS = {"create", "createMany"}
BOTH_OPS = {"upsert"}          # needs companyId in `where` AND in `create`
ALL_OPS = WHERE_OPS | DATA_OPS | BOTH_OPS


def git(*args, check=True):
    r = subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def sharded_models():
    """Return camelCase Prisma accessor names, or raise if the two sources disagree."""
    schema_models = set()
    schema_dir = os.path.join(REPO, "utils/db/prisma/schema")
    for name in os.listdir(schema_dir):
        if not name.endswith(".prisma"):
            continue
        text = open(os.path.join(schema_dir, name)).read()
        current = None
        for line in text.splitlines():
            m = re.match(r"\s*model\s+(\w+)", line)
            if m:
                current = m.group(1)
            elif "@shardKey" in line and current:
                schema_models.add(current)

    ts = open(os.path.join(REPO, "utils/db/test/vitess-config/sharded-tables.ts")).read()
    list_models = set(re.findall(r'"(\w+)"', ts))

    if schema_models != list_models:
        raise RuntimeError(
            "sharded-table sources disagree — "
            f"@shardKey only: {sorted(schema_models - list_models)}, "
            f"SHARDED_TABLES only: {sorted(list_models - schema_models)}"
        )
    return {m[0].lower() + m[1:]: m for m in schema_models}


def added_lines(base, head, path):
    """Line numbers added to `path` between base and head."""
    out = git("diff", "-U0", f"{base}..{head}", "--", path)
    lines, cur = set(), 0
    for line in out.splitlines():
        if line.startswith("@@"):
            m = re.search(r"\+(\d+)", line)
            cur = int(m.group(1)) if m else 0
        elif line.startswith("+") and not line.startswith("+++"):
            lines.add(cur)
            cur += 1
    return lines


def match_object(src, i):
    """Given index of an opening brace/paren, return index just past its match.

    Skips strings, template literals, and comments so a `{` inside a string or a
    `//` comment cannot unbalance the scan.
    """
    opens, closes = "{([", "})]"
    depth, n = 0, len(src)
    while i < n:
        c = src[i]
        if c in "\"'`":
            quote, i = c, i + 1
            while i < n:
                if src[i] == "\\":
                    i += 2
                    continue
                if src[i] == quote:
                    break
                if quote == "`" and src.startswith("${", i):
                    i = match_object(src, i + 1)
                    continue
                i += 1
            i += 1
            continue
        if src.startswith("//", i):
            i = src.find("\n", i)
            if i == -1:
                return n
            continue
        if src.startswith("/*", i):
            j = src.find("*/", i)
            i = n if j == -1 else j + 2
            continue
        if c in opens:
            depth += 1
        elif c in closes:
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return n


def top_level_entries(obj_src):
    """Yield (key_or_None, is_spread) for each depth-1 entry of an object literal."""
    inner = obj_src.strip()
    if not (inner.startswith("{") and inner.endswith("}")):
        return
    body, i, n = inner[1:-1], 0, len(inner) - 2
    body_len = len(body)
    start = 0
    parts = []
    while i < body_len:
        c = body[i]
        if c in "\"'`":
            i = match_string(body, i)
            continue
        if body.startswith("//", i):
            j = body.find("\n", i)
            i = body_len if j == -1 else j
            continue
        if body.startswith("/*", i):
            j = body.find("*/", i)
            i = body_len if j == -1 else j + 2
            continue
        if c in "{([":
            i = match_object(body, i)
            continue
        if c == ",":
            parts.append(body[start:i])
            start = i + 1
        i += 1
    parts.append(body[start:])

    for p in parts:
        p = p.strip()
        if not p:
            continue
        if p.startswith("..."):
            yield None, True
            continue
        m = re.match(r'^["\']?(\w+)["\']?\s*(?::|,|$)', p)
        yield (m.group(1) if m else None), False


def match_string(src, i):
    quote, n = src[i], len(src)
    i += 1
    while i < n:
        if src[i] == "\\":
            i += 2
            continue
        if src[i] == quote:
            return i + 1
        i += 1
    return n


def find_sub_object(args_src, key):
    """Return the object literal source for a top-level `key:` in args, or None."""
    inner = args_src.strip()
    if not (inner.startswith("{") and inner.endswith("}")):
        return None
    body = inner[1:-1]
    i, n = 0, len(body)
    while i < n:
        c = body[i]
        if c in "\"'`":
            i = match_string(body, i)
            continue
        if body.startswith("//", i):
            j = body.find("\n", i)
            i = n if j == -1 else j
            continue
        if c in "{([":
            i = match_object(body, i)
            continue
        m = re.match(r'["\']?' + key + r'["\']?\s*:', body[i:])
        if m and (i == 0 or not (body[i - 1].isalnum() or body[i - 1] in "_$.")):
            j = i + m.end()
            while j < n and body[j] in " \t\r\n":
                j += 1
            if j < n and body[j] == "{":
                return body[j:match_object(body, j)]
            return ""      # present but not an object literal (variable, call, spread)
        i += 1
    return None


def has_top_level_company_id(obj_src, allow_relation_connect=False):
    """(ok, undecidable, reason) for a `where`/`data`/`create` object literal."""
    if obj_src is None:
        return False, False, "absent"
    if obj_src == "":
        return False, True, "not an object literal"
    keys = list(top_level_entries(obj_src))
    if any(k == "companyId" for k, _ in keys):
        return True, False, ""

    # `company: { connect: { id } }` in a write populates the companyId column in
    # the generated INSERT, so the shard key does reach the wire — it just isn't
    # spelled as a scalar. The recorded rule only excludes nested relations inside
    # `where` (a join, which Vitess cannot route by). Treated as undecidable rather
    # than a violation: claiming one here would need a real-DB test to justify.
    if allow_relation_connect:
        rel = find_sub_object(obj_src, "company")
        if rel and "connect" in rel:
            return False, True, "shard key set via `company: { connect }`"

    if any(spread for _, spread in keys):
        return False, True, "uses a spread"
    return False, False, "absent"


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "origin/master"
    head = sys.argv[2] if len(sys.argv) > 2 else "HEAD"
    cmd = f"zamp-sharded-companyid.py {base} {head}"

    def emit(code, matches, coverage=None):
        r = {"command": cmd, "exit_code": code, "matches": matches}
        if coverage is not None:
            r["coverage"] = coverage
        print(json.dumps(r))
        return 0

    try:
        for ref in (base, head):
            git("rev-parse", "--verify", "--quiet", ref)
        models = sharded_models()
    except RuntimeError as e:
        return emit(5, [], {"error": str(e)})

    files = [
        f for f in git("diff", "--name-only", "--diff-filter=d", f"{base}..{head}").splitlines()
        if re.search(r"(^|/)domains/.*\.tsx?$", f)
    ]

    call_re = re.compile(
        r"\b(?:prisma|tx|db)\s*\.\s*(" + "|".join(models) + r")\s*\.\s*(\w+)\s*\("
    )

    matches, scanned, checked, skipped = [], 0, 0, []
    for path in files:
        try:
            src = git("show", f"{head}:{path}")
        except RuntimeError:
            continue
        scanned += 1
        adds = added_lines(base, head, path)

        for m in call_re.finditer(src):
            model, op = m.group(1), m.group(2)
            if op not in ALL_OPS:
                continue
            open_paren = m.end() - 1
            end = match_object(src, open_paren)
            call_src = src[open_paren:end]
            start_line = src.count("\n", 0, m.start()) + 1
            end_line = src.count("\n", 0, end) + 1
            touched = any(start_line <= ln <= end_line for ln in adds)

            args = call_src.strip()[1:-1].strip()          # drop the parens
            if not args.startswith("{"):
                skipped.append(f"{path}:{start_line} {model}.{op} — args not a literal")
                continue
            args = args[:match_object(args, 0)]

            required = (["where"] if op in WHERE_OPS else
                        ["data"] if op in DATA_OPS else ["where", "create"])
            checked += 1
            for key in required:
                sub = find_sub_object(args, key)
                # relation-connect only counts on the write side (data / upsert create)
                ok, undecidable, reason = has_top_level_company_id(
                    sub, allow_relation_connect=(key in ("data", "create"))
                )
                if ok:
                    continue
                if undecidable:
                    skipped.append(f"{path}:{start_line} {model}.{op} — `{key}`: {reason}")
                elif touched:
                    matches.append(f"{path}:{start_line}  {model}.{op} missing companyId in `{key}`")

    return emit(0, matches, {
        "files_changed_in_scope": len(files),
        "files_scanned": scanned,
        "call_sites_checked": checked,
        "call_sites_skipped": len(skipped),
        "skipped_detail": skipped[:20],
        "sharded_models": sorted(models.values()),
        "note": "matches are limited to call sites overlapping added lines; raw SQL is out of scope",
    })


if __name__ == "__main__":
    sys.exit(main())
