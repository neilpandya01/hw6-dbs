#!/usr/bin/env python3
"""Status ledger: what I've told the agent is done, in progress, or pushed.

Writes only notes/status.md (override with LEDGER_PATH). Entries are keyed by
(item, task day), so a homework that repeats weekly under the same title is
tracked per week.

Usage:
  python3 scripts/ledger.py add --status done --day 2026-11-08 --item "Databases hw" [--due 2026-11-13]
  python3 scripts/ledger.py add --status pushed --day 2026-11-08 --item "Reading" --moved-to 2026-11-11
  python3 scripts/ledger.py add --status in-progress --day 2026-11-08 --item "Reading"
  python3 scripts/ledger.py remove --day 2026-11-08 --item "Databases hw"
  python3 scripts/ledger.py list
"""
import argparse
import os
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATUSES = ("done", "in-progress", "pushed")
KEYS = ("status", "task_day", "item", "due", "moved_to", "logged")
PREFIX = re.compile(r"^\s*([0A-Za-z]):\s*")
TIME_HINT = re.compile(r"\b\d{1,2}(?::\d{2})?\s?[ap]m?\b|\b\d{1,2}:\d{2}\b", re.I)
HEADER = (
    "# Status ledger\n\n"
    "What I've told the agent is done, in progress, or pushed. Written by `scripts/ledger.py`.\n"
    "Keyed by item and task day. A `done` row hides that task from reminders.\n\n"
    "| status | task day | item | due | moved to | logged |\n"
    "|---|---|---|---|---|---|\n"
)


def ledger_path():
    return Path(os.environ.get("LEDGER_PATH") or ROOT / "notes" / "status.md")


def norm(title):
    t = PREFIX.sub("", title or "")
    t = TIME_HINT.sub("", t)
    return re.sub(r"\s+", " ", t).strip().lower()


def read_rows(path=None):
    p = path or ledger_path()
    if not p.exists():
        return []
    rows = []
    for line in p.read_text().splitlines():
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != len(KEYS) or cells[0] == "status":
            continue
        rows.append(dict(zip(KEYS, cells)))
    return rows


def write_rows(rows, path=None):
    p = path or ledger_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    body = "".join(
        f"| {r['status']} | {r['task_day']} | {r['item']} | {r['due']} | {r['moved_to']} | {r['logged']} |\n" for r in rows
    )
    p.write_text(HEADER + body)


def clean_item(item):
    return PREFIX.sub("", item or "").replace("|", "/").strip()


def add(status, day, item, due="", moved_to="", logged=None):
    rows = read_rows()
    key = (norm(item), day)
    rows = [r for r in rows if (norm(r["item"]), r["task_day"]) != key]
    rows.append({
        "status": status, "task_day": day, "item": clean_item(item),
        "due": due or "", "moved_to": moved_to or "", "logged": logged or date.today().isoformat(),
    })
    rows.sort(key=lambda r: (r["task_day"], r["item"].lower()))
    write_rows(rows)


def remove(day, item):
    rows = read_rows()
    key = (norm(item), day)
    kept = [r for r in rows if (norm(r["item"]), r["task_day"]) != key]
    write_rows(kept)
    return len(rows) - len(kept)


def valid_date(s):
    if s and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        sys.exit(f"bad date {s!r}; use YYYY-MM-DD")
    return s


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("--status", required=True, choices=STATUSES)
    a.add_argument("--day", required=True, help="the day the task is scheduled in the task list (YYYY-MM-DD)")
    a.add_argument("--item", required=True)
    a.add_argument("--due", default="")
    a.add_argument("--moved-to", default="")
    r = sub.add_parser("remove")
    r.add_argument("--day", required=True)
    r.add_argument("--item", required=True)
    sub.add_parser("list")
    args = ap.parse_args()

    if args.cmd == "add":
        add(args.status, valid_date(args.day), args.item, valid_date(args.due), valid_date(args.moved_to))
        print(f"logged: {args.status} | {args.day} | {clean_item(args.item)}")
    elif args.cmd == "remove":
        n = remove(valid_date(args.day), args.item)
        print(f"removed {n} row(s)")
    else:
        rows = read_rows()
        for row in rows:
            extra = f" -> {row['moved_to']}" if row["moved_to"] else ""
            print(f"{row['status']:12} {row['task_day']}  {row['item']}{extra}  (logged {row['logged']})")
        if not rows:
            print("(ledger is empty)")


if __name__ == "__main__":
    main()
