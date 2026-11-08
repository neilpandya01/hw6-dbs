#!/usr/bin/env python3
"""Tests for scripts/ledger.py and its use in scripts/digest.py. Uses made-up tasks in a temp dir.
Run: python3 scripts/test_ledger.py
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "scripts" / "ledger.py"
DIGEST = ROOT / "scripts" / "digest.py"
GUARD = ROOT / "scripts" / "guard.py"


def task(title, day, status="needsAction"):
    # local midnight in Chicago (CST) == 06:00Z
    return {
        "kind": "tasks#task", "id": title + day, "title": title, "status": status,
        "scheduled_time": [{"current": True, "start": f"{day}T06:00:00Z"}],
    }


TASKS = [
    task("A: Homework one", "2026-11-08"),
    task("Homework one", "2026-11-15"),          # same title, a different week
    task("B: Project work 11am", "2026-11-08"),
    task("Reading two", "2026-11-09"),
    task("Z: Pay bill", "2026-11-08"),
]

tmp = Path(tempfile.mkdtemp())
(tmp / "tasks_test.json").write_text(json.dumps({"items": [{"items": TASKS}]}))
ENV = {**os.environ, "TASKS_PATH": str(tmp / "tasks_test.json"), "LEDGER_PATH": str(tmp / "status.md")}


def run(*args):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, env=ENV)


def digest():
    return run(DIGEST, "--date", "2026-11-10").stdout


def ledger(*args):
    return run(LEDGER, *args)


results = []


def check(label, ok):
    results.append(ok)
    print(f"{'ok  ' if ok else 'FAIL'} {label}")


# 1. nothing logged: everything shows
d = digest()
check("no ledger: rolled-over tasks appear", "Homework one" in d and "Project work" in d)

# 2. done hides only that week's task
ledger("add", "--status", "done", "--day", "2026-11-08", "--item", "A: Homework one", "--due", "2026-11-13")
d = digest()
rolled = d.split("## Rolled over")[1].split("## Completed")[0]
upcoming = d.split("## Coming up")[1].split("## Weather")[0]
check("done hides that week's task from rollovers", "Homework one" not in rolled.split("(hidden")[0])
check("hidden line names the hidden task", "hidden, marked done" in d and "Homework one (11-08)" in d)
check("same title next week is NOT hidden", "Homework one" in upcoming)

# 3. normalization: prefix and time in the title don't break matching
ledger("add", "--status", "done", "--day", "2026-11-08", "--item", "Project work")
d = digest()
check("matches despite prefix and time in title", "Project work 11am" not in d.split("## Completed")[0].split("hidden")[0])

# 4. upsert replaces instead of duplicating; in-progress shows as a tag
ledger("add", "--status", "done", "--day", "2026-11-09", "--item", "Reading two")
ledger("add", "--status", "in-progress", "--day", "2026-11-09", "--item", "Reading two")
rows = [l for l in ledger("list").stdout.splitlines() if "Reading two" in l]
check("upsert keeps a single row per item and day", len(rows) == 1 and rows[0].startswith("in-progress"))
check("in-progress task still listed with a notes tag", "[notes: in-progress]" in digest())

# 5. pushed shows the new day
ledger("add", "--status", "pushed", "--day", "2026-11-08", "--item", "Pay bill", "--moved-to", "2026-11-12")
check("pushed shows where it moved", "[notes: pushed -> 2026-11-12]" in digest())

# 6. remove undoes a mistake
ledger("remove", "--day", "2026-11-08", "--item", "Homework one")
rolled = digest().split("## Rolled over")[1].split("## Completed")[0]
check("remove brings a task back", "Homework one" in rolled)

# 7. bad input is rejected
check("bad date is rejected", ledger("add", "--status", "done", "--day", "11/08", "--item", "x").returncode != 0)
check("bad status is rejected", ledger("add", "--status", "finished", "--day", "2026-11-08", "--item", "x").returncode != 0)

# 8. the hook allows the ledger command
event = {"tool_name": "Bash", "tool_input": {"command": 'python3 scripts/ledger.py add --status done --day 2026-11-08 --item "x"'}, "cwd": str(ROOT)}
out = subprocess.run([sys.executable, "-I", str(GUARD)], input=json.dumps(event), capture_output=True, text=True).stdout
check("hook allows ledger commands", out.strip() == "")

print(f"\n{sum(results)}/{len(results)} passed")
sys.exit(0 if all(results) else 1)
