#!/usr/bin/env python3
"""Generic OKF attester: a receipt passes when its `matches` list is empty.

Reads a receipt (JSON) from a path argument or stdin. The receipt shape is fixed
by brain/conventions.md:

    { "command": "<the exact command run>", "exit_code": 0, "matches": [] }

Exit codes are three-valued on purpose, because "the check ran and the invariant
is violated" and "the check could not run" are different findings and conflating
them hides real breakage:

    0  PASS      matches is empty
    1  VIOLATED  the check ran and found matches
    2  ERROR     malformed receipt, or the check itself failed (exit_code != 0)

No LLM in the loop. Deterministic.
"""
import json
import sys


def main() -> int:
    raw = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()

    try:
        receipt = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR malformed receipt: {e}", file=sys.stderr)
        return 2

    missing = {"command", "exit_code", "matches"} - receipt.keys()
    if missing:
        print(f"ERROR receipt missing {sorted(missing)}", file=sys.stderr)
        return 2

    command = receipt["command"]

    # A non-zero exit from the check is not a violation — it means the sanctioned
    # check never produced a verdict. Reporting it as a pass would be a lie and
    # as a violation would be a false alarm.
    if receipt["exit_code"] != 0:
        print(
            f"ERROR sanctioned check failed to run (exit {receipt['exit_code']})\n"
            f"  command: {command}",
            file=sys.stderr,
        )
        return 2

    matches = receipt["matches"]
    if not isinstance(matches, list):
        print(f"ERROR matches is {type(matches).__name__}, expected list", file=sys.stderr)
        return 2

    if matches:
        print(f"VIOLATED {len(matches)} match(es)\n  command: {command}")
        for m in matches:
            print(f"  - {m}")
        return 1

    print(f"PASS\n  command: {command}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
