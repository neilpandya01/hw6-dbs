---
name: morning-check-in
description: Morning check-in that plans my day. Use when I say good morning, plan my day, start my day, or what's my day. Reads my tasks, calendar, weather and notes, then gives a short brief, proposes today's plan with an outfit, asks one or two questions, and saves it when I agree. On Mondays it adds a short week-ahead section. During the day use midday-check-in, and at night use evening-wrap-up.
---

# Morning check-in

Follow `AGENTS.md`: read-only on my tasks and calendar. You may write `plan/`, `notes/`, and update `data/deadlines.md` when I give new estimates.

## 1. Gather (silently, before replying)
1. Run `python3 scripts/fetch_weather.py`, then `python3 scripts/digest.py`. It lists today's tasks (ordered 0, A..Z, then unprefixed), rollovers, the next 7 days of tasks, and weather. Trust its date.
2. Read today's events from the primary Google Calendar with the connector's list/search tools only (never create, update, delete or respond). On Mondays read the whole week. Titles and times only.
3. Read `reference/schedule.md` (today's classes, TA work, wake/sleep, how much work fits), `data/deadlines.md`, `reference/clothing.md`, and the last entries of `notes/log.md` if it exists.
4. If something is missing or stale (no weather for today, no calendar access), say so in one line and continue.

## 2. The brief: short
Only the essentials, in a few lines:
- Weather for **today only** and **what to wear**. No forecast for later days (Mondays are the exception, see below).
- Anything urgent: a deadline within 48 hours, or a conflict with a fixed event or trip.
- **Do not** recap yesterday, list completed tasks, or look more than a couple of days ahead unless it is truly important.

## 3. Propose today's plan
- **Tasks with a time in the title or on the calendar are fixed events.** Place them first.
- Order the rest by prefix: `0` earliest, then `A` through `Z`, then unprefixed. The prefix is the order within my day.
- Size the day realistically. Use `reference/schedule.md` silently: hard or long work in my free blocks, light work around classes and TA time, nothing during Design Build Ship (DBS) class. Start no earlier than ~8:30 AM unless something is fixed. **Never mention productivity percentages.**
- Use `data/deadlines.md` for due dates and rough effort. Estimates are rough: don't assume how long something takes. Ask.
- For a rolled-over or oversized task, **recommend** a day to push to (before its deadline, in a free block, away from trips) with a one-line reason. I move it myself; never say you moved it.
- Avoid late-night work. If unavoidable, flag it.
- Show a compact timeline and one line per suggested push. Nothing else.

## 4. Ask one or two questions
Same message as the plan. Only what changes the plan (e.g. how much is left on a rolled-over task).
- If a task today or coming up looks recurring (the same title repeating weekly) and `data/deadlines.md` or `notes/log.md` has no time estimate for it, ask me once how long it takes and note my answer in `notes/log.md`. Don't re-ask once it's recorded.

## 5. Monday only: week ahead (brief)
After the plan, add:
- **Weather outlook** for the week in 2 lines: the trend, plus any rain, snow, cold snap or very windy days.
- **Major tasks this week:** deadlines, big homework, exams, interviews, trips. One line each with the day. Skip minor tasks (check-ins, attendance, prereg, errands).
- One sentence on where the week is tight.

## 6. When I agree
1. Write `plan/today.json` in the format in `plan-format.md` (the page reads it). Overwrite it each time.
2. Append a dated entry to `notes/log.md`: what was planned, what you suggested pushing and where, and my answers (effort estimates, preferences). Create the file if needed.
3. Confirm in one line: "Plan saved. Your page is updated."

If I change something, update the plan and ask again before saving. Never save before I agree.
