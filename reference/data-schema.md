# Data reference

## data/Tasks.json (Google Takeout, one list "My Tasks")
- Path: `items[0].items[]`, one object per task (`kind: tasks#task`). Recurrence rules are in `items[0].recurrences[]`.
- `title`: free text. May start with a prefix `0:` (earliest), then `A:`..`Z:` (order in the day). Times appear only inside titles ("1pm").
- `status`: `needsAction` (open) or `completed`. Completed tasks have `completed` timestamps; use them to recap yesterday.
- **Day to start a task:** `scheduled_time[current=true].start` (UTC). Subtract 6h (CST) or 5h (CDT) to get the local date. There is no `due`, no `notes`, no estimate.
- **Stale data:** ~1,700 open tasks are scheduled in the past, mostly 2020–2022. Ignore open tasks scheduled before ~14 days ago. Treat only recent ones as rolled over.
- Weekly-looking tasks (the same title repeated on a weekly pattern) are separate task entries, not flagged recurring.
- The file is a snapshot; it can be out of date versus my phone.

## Calendar (connector)
- Personal Google account, read through the connector. Use the primary calendar for one-off events. Other calendars on the account are secondary.
- Flights come from Gmail as events (type FROM_GMAIL). They mark fixed constraints.
- Not visible: the weekly class schedule (see `reference/schedule.md`), email, course sites.
- The connector can write. Never call create/update/delete/respond.

## Weather
- `scripts/fetch_weather.py` writes `data/weather.json` (Open-Meteo, °F/mph/inches, America/Chicago). Re-run each check-in.
- Use hourly arrays to split morning / afternoon / evening. Sunset is early in November (~4:35 PM).
