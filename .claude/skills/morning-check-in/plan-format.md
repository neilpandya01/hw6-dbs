# plan/today.json format

The page reads this file. Keep keys exact. Times are 24-hour local `HH:MM`. Use `null` when unknown.

```json
{
  "date": "2026-01-12",
  "weekday": "Monday",
  "saved_at": "2026-01-12T08:45:00-06:00",
  "headline": "One sentence on the shape of the day.",
  "weather": {
    "summary": "Sunny, 37 to 59F, dry",
    "feels_low": 31,
    "feels_high": 52,
    "rain_chance": 0,
    "wind_max": 11,
    "coldest_time": "08:00",
    "wear": ["medium coat", "sweater", "hat"],
    "outfit_note": "Chilly start, mild afternoon. Bring a layer you can take off."
  },
  "schedule": [
    {
      "start": "11:00",
      "end": "11:50",
      "title": "Class",
      "kind": "class",
      "task": null,
      "note": null
    }
  ],
  "tasks": [
    {
      "title": "Databases hw",
      "prefix": "A",
      "plan": "do",
      "push_to": null,
      "reason": null
    }
  ],
  "flags": ["Short warnings: deadline risk, trip conflicts, late-night work."],
  "outlook": {
    "weather": ["Only on Mondays. 2 to 3 short lines."],
    "major_tasks": [{ "day": "Tue", "title": "Assignment due 4:00 PM" }]
  },
  "notes_for_next_time": ["Anything the next check-in should remember."],
  "progress": null,
  "wrapup": null
}
```

Field rules
- `kind`: one of `task`, `event`, `class`, `ta`, `break`, `travel`.
- `plan` on a task: `do` (work on it today), `push` (suggest a new day, set `push_to` as `YYYY-MM-DD`, give `reason`), or `skip`.
- `outlook` only on Mondays; otherwise `null`.
- Never include attendee names or emails.

## wrapup (added by the evening skill, not the morning one)
```json
"wrapup": {
  "saved_at": "2026-01-12T21:30:00-06:00",
  "done": ["Homework A"],
  "pushes": [
    { "title": "Reading B", "push_to": "2026-01-14", "reason": "Not due until later in the week, and Wednesday is free" }
  ],
  "tomorrow": ["First fixed thing: 11:00 AM class", "Assignment due 4:00 PM"],
  "flags": ["Short warnings only."]
}
```
- The morning check-in sets `"wrapup": null`. The evening skill fills it in and keeps everything else in the file.
- If there is no plan for today, the evening skill creates `date`, `weekday`, empty `schedule` and `tasks`, and `wrapup`.

## progress (added by the midday skill)
```json
"progress": {
  "updated_at": "2026-01-12T14:10:00-06:00",
  "done": [{ "title": "Homework A, first pass", "time": "13:55" }],
  "in_progress": [{ "title": "Reading B", "note": "about half left" }],
  "adjustments": ["Moved the rest of Homework A to 19:00 tonight"]
}
```
- The morning check-in sets `"progress": null`. The midday skill creates and updates it, and keeps everything else in the file.
- Add to `done` when I say I finished something. Use the real current time (`HH:MM`).
- `adjustments` are short plain sentences, only for changes I agreed to.
- The evening wrap-up reads `progress` so it doesn't ask about things already logged.
