#!/usr/bin/env python3
"""Morning check-in digest. Read-only: reads the tasks export, weather and the status ledger, prints text.

Usage: python3 scripts/digest.py [--date YYYY-MM-DD] [--stale-days 14] [--ahead 7]
Tasks are ordered by title prefix: 0 first, then A..Z, then unprefixed.
Tasks marked done in notes/status.md are hidden. Env overrides for tests: TASKS_PATH, LEDGER_PATH.
"""
import argparse
import importlib.util
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
TZ = ZoneInfo("America/Chicago")
PREFIX = re.compile(r"^\s*([0A-Za-z]):\s*")
TIME_HINT = re.compile(r"\b\d{1,2}(?::\d{2})?\s?[ap]m?\b|\b\d{1,2}:\d{2}\b", re.I)
HOURS = (8, 10, 12, 14, 16, 18, 20, 22)


def load_ledger():
    spec = importlib.util.spec_from_file_location("ledger", ROOT / "scripts" / "ledger.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def to_local_date(iso):
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(TZ).date()


def start_day(task):
    s = task.get("scheduled_time")
    if not s:
        return None
    cur = [x for x in s if x.get("current")] or s
    return to_local_date(cur[0]["start"])


def prefix_of(title):
    m = PREFIX.match(title or "")
    return m.group(1).upper() if m else None


def sort_key(task):
    p = prefix_of(task["title"])
    if p is None:
        return (2, "")
    return (0, "") if p == "0" else (1, p)


def clean(title):
    return PREFIX.sub("", title or "").strip()


def fmt_task(t):
    p = prefix_of(t["title"]) or "-"
    hint = TIME_HINT.search(t["title"] or "")
    extra = f"  (time in title: {hint.group(0)})" if hint else ""
    row = t.get("_row")
    if row:
        extra += f"  [notes: {row['status']}" + (f" -> {row['moved_to']}" if row["moved_to"] else "") + "]"
    return f"- [{p}] {clean(t['title'])}{extra}"


def tasks_section(tasks, today, stale_days, ahead, ledger):
    rows = ledger.read_rows()
    index = {(ledger.norm(r["item"]), r["task_day"]): r for r in rows}

    open_ = [t for t in tasks if t.get("status") == "needsAction"]
    hidden = []
    visible = []
    for t in open_:
        t["_d"] = start_day(t)
        t["_row"] = index.get((ledger.norm(t["title"]), t["_d"].isoformat())) if t["_d"] else None
        (hidden if t["_row"] and t["_row"]["status"] == "done" else visible).append(t)
    open_ = visible
    out = []

    todays = sorted((t for t in open_ if t["_d"] == today), key=sort_key)
    out.append(f"## Open tasks for today ({today:%A %Y-%m-%d}), in order 0, A..Z, then unprefixed")
    out += [fmt_task(t) for t in todays] or ["- none"]

    cutoff = today - timedelta(days=stale_days)
    rolled = sorted((t for t in open_ if t["_d"] and cutoff <= t["_d"] < today), key=lambda t: (t["_d"], sort_key(t)))
    out.append(f"\n## Rolled over: open, scheduled in the last {stale_days} days")
    out += [f"- was {t['_d']:%a %m-%d}: " + fmt_task(t)[2:] for t in rolled] or ["- none"]
    stale = sum(1 for t in open_ if t["_d"] and t["_d"] < cutoff)
    out.append(f"(ignoring {stale} older open tasks as stale)")
    recent_hidden = [t for t in hidden if t["_d"] and t["_d"] >= cutoff]
    if recent_hidden:
        names = ", ".join(f"{clean(t['title'])} ({t['_d']:%m-%d})" for t in recent_hidden)
        out.append(f"(hidden, marked done in notes/status.md: {names})")

    done = [t for t in tasks if t.get("status") == "completed" and t.get("completed")]
    yday = today - timedelta(days=1)
    for label, day in (("yesterday", yday), ("today so far", today)):
        items = sorted((t for t in done if to_local_date(t["completed"]) == day), key=lambda t: t["completed"])
        out.append(f"\n## Completed {label} ({day:%a %m-%d})")
        out += [f"- {t['title']}" for t in items] or ["- none"]

    out.append(f"\n## Coming up: open tasks, next {ahead} days")
    for i in range(1, ahead + 1):
        d = today + timedelta(days=i)
        day_tasks = sorted((t for t in open_ if t["_d"] == d), key=sort_key)
        out.append(f"### {d:%a %m-%d}")
        out += [fmt_task(t) for t in day_tasks] or ["- (none)"]

    recent = [r for r in rows if r["logged"] >= (today - timedelta(days=7)).isoformat()]
    if recent:
        out.append("\n## Recent entries in notes/status.md (last 7 days)")
        for r in recent:
            moved = f" -> {r['moved_to']}" if r["moved_to"] else ""
            out.append(f"- {r['status']}: {r['item']} (task day {r['task_day']}){moved}")
    return out


def weather_section(today, ahead):
    p = ROOT / "data" / "weather.json"
    if not p.exists():
        return ["## Weather", "- data/weather.json missing. Run: python3 scripts/fetch_weather.py"]
    w = json.loads(p.read_text())
    D, H = w["daily"], w["hourly"]
    days = D["time"]
    key = f"{today:%Y-%m-%d}"
    if key not in days:
        return ["## Weather", f"- weather.json has no forecast for {key}. Run: python3 scripts/fetch_weather.py"]
    i = days.index(key)
    out = [f"## Weather today ({key}, Chicago, F / mph / in)"]
    out.append(
        f"- high {D['temperature_2m_max'][i]}, low {D['temperature_2m_min'][i]}; feels-like {D['apparent_temperature_min'][i]} to "
        f"{D['apparent_temperature_max'][i]}; rain chance max {D['precipitation_probability_max'][i]}%; precip {D['precipitation_sum'][i]} in; "
        f"snow {D['snowfall_sum'][i]} in; wind max {D['wind_speed_10m_max'][i]} mph; sunrise {D['sunrise'][i][11:]}, sunset {D['sunset'][i][11:]}"
    )
    idx = {t: n for n, t in enumerate(H["time"])}
    out.append("- hourly (feels-like / rain% / wind):")
    for hr in HOURS:
        n = idx.get(f"{key}T{hr:02d}:00")
        if n is not None:
            out.append(
                f"  - {hr:02d}:00  temp {H['temperature_2m'][n]}, feels {H['apparent_temperature'][n]}, "
                f"rain {H['precipitation_probability'][n]}%, wind {H['wind_speed_10m'][n]}"
            )
    out.append("\n## Weather, next days")
    for j in range(i + 1, min(i + 1 + ahead, len(days))):
        d = datetime.strptime(days[j], "%Y-%m-%d")
        out.append(
            f"- {d:%a %m-%d}: hi {D['temperature_2m_max'][j]}, lo {D['temperature_2m_min'][j]}, feels {D['apparent_temperature_min'][j]}"
            f" to {D['apparent_temperature_max'][j]}, rain {D['precipitation_probability_max'][j]}%, "
            f"snow {D['snowfall_sum'][j]} in, wind {D['wind_speed_10m_max'][j]}"
        )
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="YYYY-MM-DD (default: today, Chicago)")
    ap.add_argument("--stale-days", type=int, default=14)
    ap.add_argument("--ahead", type=int, default=7)
    a = ap.parse_args()
    today = datetime.strptime(a.date, "%Y-%m-%d").date() if a.date else datetime.now(TZ).date()

    tasks_file = Path(os.environ.get("TASKS_PATH") or ROOT / "data" / "Tasks.json")
    lines = [f"# Digest for {today:%A %Y-%m-%d}" + ("  (MONDAY: include weekly outlook)" if today.weekday() == 0 else "")]
    if tasks_file.exists():
        tasks = json.loads(tasks_file.read_text())["items"][0]["items"]
        lines += tasks_section(tasks, today, a.stale_days, a.ahead, load_ledger())
    else:
        lines.append("Tasks export missing.")
    lines.append("")
    lines += weather_section(today, a.ahead)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
