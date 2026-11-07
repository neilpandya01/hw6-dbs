---
name: morning-check-in
description: Morning check-in that plans my day. Use when I say good morning, plan my day, start my day, what's my day, or check in. Reads my tasks, calendar, weather and notes, recaps yesterday, asks one or two questions, proposes a plan with an outfit, and saves it when I agree. On Mondays it adds a look at the week ahead.
---

# Morning check-in

Follow `AGENTS.md`: read-only on my tasks, calendar and `data/`. You may write only `plan/` and `notes/`.

## 1. Gather (before saying anything long)
1. Run `python3 scripts/fetch_weather.py`, then `python3 scripts/digest.py`. The digest has today's tasks (ordered 0, A..Z, then unprefixed), rollovers, yesterday's completions, the next 7 days of tasks, and weather. Trust its date.
2. Read the primary Google Calendar for today with the calendar connector's list/search tools only (never create, update, delete or respond). On Mondays, read the whole week. Show titles and times only.
3. Read `reference/schedule.md` for today's classes, TA work, productivity windows and wake/sleep. Read `data/deadlines.md`. Read the last entries of `notes/log.md` if it exists.
4. Read `reference/clothing.md` for outfit rules.
5. If something is missing or stale (no weather for today, no calendar access), say so and continue.

## 2. Brief me (short)
- One line of weather, then **what to wear** using feels-like and the coldest time I'll be outside.
- **Yesterday:** what I completed and what rolled over. Use notes for context.
- Anything urgent: a deadline within 48 hours, a conflict with a calendar event or trip.

## 3. Propose today's plan
- **Tasks with a time in the title or on the calendar are fixed events.** Place them first.
- Order the rest by prefix: `0` earliest, then `A` through `Z`, then unprefixed. Prefix means order in my day.
- Use the productivity windows: hard or long work in 100% windows, light work in 50% windows, nothing during Design, Build, Ship class. Start no earlier than ~8:30 AM unless something is fixed.
- Use `data/deadlines.md` for due dates and rough effort. Estimates are rough: **don't assume how long something takes. Ask.**
- For rolled-over or too-big tasks, **recommend** a day to push to (before the deadline, in a 100% window, away from trips). Say why. I move it myself in Google Tasks; never claim you moved it.
- Avoid late-night work. If unavoidable, flag it.
- Present it as a timeline, then a short list of what you suggest pushing.

## 4. Ask one or two questions
Ask in the same message as the proposal, only what changes the plan (e.g. how much is left on a rolled-over task, or whether a pinned task is still on). Keep it to one or two.

## 5. Monday only: week ahead (keep it brief)
After the day's plan, add:
- **Weather outlook:** the week's trend in 2 to 3 lines (warm-up, cold snap, rain or snow days, windy days). Macro only.
- **Major tasks this week:** deadlines, big homework, exams, interviews, trips, key meetings. **Skip minor tasks** (check-ins, attendance, prereg, small errands). One line each, with the day.
- One sentence on where the week is tight.

## 6. When I agree
1. Write `plan/today.json` in the format in `plan-format.md` (the page reads it). Overwrite it each time.
2. Append a dated entry to `notes/log.md`: what was planned, what you suggested pushing and where, my answers (effort estimates, preferences). Create the file if needed.
3. Confirm in one line: "Plan saved. Your page is updated."

If I change something, update the plan and ask again before saving. Never save before I agree.
