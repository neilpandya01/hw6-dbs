# plan/today.json format

The page reads this file. Keep keys exact. Times are 24-hour local `HH:MM`. Use `null` when unknown.

```json
{
  "date": "2026-11-09",
  "weekday": "Monday",
  "saved_at": "2026-11-09T08:45:00-06:00",
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
      "start": "09:30",
      "end": "10:20",
      "title": "Class",
      "kind": "class",
      "effective": 50,
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
    "major_tasks": [{ "day": "Tue", "title": "Assignment due 5:30 PM" }]
  },
  "notes_for_next_time": ["Anything the next check-in should remember."]
}
```

Field rules
- `kind`: one of `task`, `event`, `class`, `ta`, `break`, `travel`.
- `effective`: 100, 50, or 0. Productivity during that block.
- `plan` on a task: `do` (work on it today), `push` (suggest a new day, set `push_to` as `YYYY-MM-DD`, give `reason`), or `skip`.
- `outlook` only on Mondays; otherwise `null`.
- Never include attendee names or emails.
