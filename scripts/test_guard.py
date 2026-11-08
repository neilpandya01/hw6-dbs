#!/usr/bin/env python3
"""Tests for scripts/guard.py. Run: python3 scripts/test_guard.py"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUARD = ROOT / "scripts" / "guard.py"


def run(event):
    event.setdefault("cwd", str(ROOT))
    p = subprocess.run([sys.executable, "-I", str(GUARD)], input=json.dumps(event), capture_output=True, text=True)
    return "deny" if p.stdout.strip() else "allow"


def tool(name, **inp):
    return {"tool_name": name, "tool_input": inp}


CASES = [
    # (label, event, expected)
    ("Write data/Tasks.json", tool("Write", file_path=f"{ROOT}/data/Tasks.json"), "deny"),
    ("Edit data/deadlines.md (relative path)", tool("Edit", file_path="data/deadlines.md"), "deny"),
    ("Write via ../ into data", tool("Write", file_path="plan/../data/Tasks.json"), "deny"),
    ("Write data/weather.json (script output)", tool("Write", file_path=f"{ROOT}/data/weather.json"), "allow"),
    ("Write plan/today.json", tool("Write", file_path=f"{ROOT}/plan/today.json"), "allow"),
    ("Write notes/log.md", tool("Write", file_path=f"{ROOT}/notes/log.md"), "allow"),
    ("Bash sed -i on Tasks.json", tool("Bash", command="sed -i s/a/b/ data/Tasks.json"), "deny"),
    ("Bash redirect into Tasks.json", tool("Bash", command="echo [] > data/Tasks.json"), "deny"),
    ("Bash rm deadlines", tool("Bash", command="rm data/deadlines.md"), "deny"),
    ("Bash mv over Tasks.json", tool("Bash", command="mv /tmp/x data/Tasks.json"), "deny"),
    ("Bash python open(...,'w')", tool("Bash", command="python3 -c \"open('data/Tasks.json','w').write('x')\""), "deny"),
    ("Bash cat Tasks.json", tool("Bash", command="cat data/Tasks.json | head -c 100"), "allow"),
    ("Bash python read with >=", tool("Bash", command="python3 -c \"import json;d=json.load(open('data/Tasks.json'));print(len(d)>=1)\""), "allow"),
    ("Bash fetch_weather.py", tool("Bash", command="python3 scripts/fetch_weather.py"), "allow"),
    ("Bash digest.py", tool("Bash", command="python3 scripts/digest.py"), "allow"),
    ("MCP create_event", tool("mcp__abc__create_event"), "deny"),
    ("MCP update_event", tool("mcp__abc__update_event"), "deny"),
    ("MCP delete_event", tool("mcp__abc__delete_event"), "deny"),
    ("MCP respond_to_event", tool("mcp__abc__respond_to_event"), "deny"),
    ("MCP create_task", tool("mcp__abc__create_task"), "deny"),
    ("Harness update_plan (not my data)", tool("mcp__ccd_turn__update_plan"), "allow"),
    ("GitHub create_pull_request (not my data)", tool("mcp__abc__create_pull_request"), "allow"),
    ("MCP list_events", tool("mcp__abc__list_events"), "allow"),
    ("MCP search_events", tool("mcp__abc__search_events"), "allow"),
    ("MCP list_calendars", tool("mcp__abc__list_calendars"), "allow"),
]

failed = 0
for label, event, expected in CASES:
    got = run(event)
    ok = got == expected
    failed += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {got:5} {label}")
print(f"\n{len(CASES) - failed}/{len(CASES)} passed")
sys.exit(1 if failed else 0)
