#!/usr/bin/env python3
"""PreToolUse hook: keep my tasks and calendar read-only.

Blocks:
  - Write/Edit/NotebookEdit on data/Tasks.json (the Google Tasks export)
  - Bash commands that modify data/Tasks.json (redirects, tee, mv, cp, rm, sed -i, python writes, ...)
    or wipe the data/ folder with a wildcard
  - Calendar/task write tools (create/update/delete/respond to events or tasks)
Allows everything else, including data/deadlines.md (my planning notes), data/weather.json,
and writes to plan/ and notes/.

Reads the hook JSON on stdin; prints a deny decision as JSON when blocking.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROTECTED = {ROOT / "data" / "Tasks.json"}

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
# Only calendar/task write tools, e.g. create_event, update_event, delete_event, respond_to_event, create_task.
MCP_WRITE = re.compile(r"^mcp__.+__(create|update|delete|respond_to|move|patch|insert|add|remove)_(event|events|task|tasks|calendar|calendars)\w*$")

T = r"Tasks\.json"
BASH_MUTATIONS = [
    rf">>?\s*['\"]?\S*{T}",
    rf"\b(tee|mv|cp|rm|truncate|touch|install|chmod|chown|ln|rsync|dd|shred|unlink)\b[^;&|\n]*{T}",
    rf"\b(sed|perl)\b[^;&|\n]*\s-\w*i\w*\b[^;&|\n]*{T}",
    rf"{T}[^;&|\n]*\b(write_text|write_bytes|json\.dump|\.write\()",
    rf"\b(write_text|write_bytes|json\.dump|\.write\()[^\n]*{T}",
    rf"open\([^)\n]*{T}[^)\n]*['\"][wax]\+?b?['\"]",
    # wiping the folder that holds it
    r"\b(rm|mv|truncate|shred)\b[^;&|\n]*\bdata/?\*",
    r"\brm\b[^;&|\n]*\s-\w*r\w*\s+\S*data/?(\s|$|;|&|\|)",
]


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def is_protected(path_str, cwd):
    p = Path(path_str)
    if not p.is_absolute():
        p = Path(cwd or ROOT) / p
    return p.resolve() in PROTECTED


def main():
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool = event.get("tool_name", "")
    inp = event.get("tool_input", {}) or {}
    cwd = event.get("cwd")

    if tool in WRITE_TOOLS:
        target = inp.get("file_path") or inp.get("notebook_path") or inp.get("path") or ""
        if target and is_protected(target, cwd):
            deny(f"Blocked: {target} is my task data and is read-only. Suggest the change and I'll make it myself.")

    elif tool == "Bash":
        cmd = inp.get("command") or ""
        for pat in BASH_MUTATIONS:
            if re.search(pat, cmd):
                deny("Blocked: this command would modify my task data (data/Tasks.json), which is read-only. "
                     "Reading is fine. Suggest the change and I'll make it myself.")

    elif MCP_WRITE.match(tool):
        deny(f"Blocked: {tool} would change my calendar or tasks. My data is read-only. "
             "Suggest the change instead and I'll make it myself.")

    sys.exit(0)


if __name__ == "__main__":
    main()
