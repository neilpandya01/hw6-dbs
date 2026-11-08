---
name: evening-wrap-up
description: Evening wrap-up, the counterpart to the morning check-in. Use when I say wrap up, end of day, good night, evening check-in, or that I'm done for today. Finds what is still open today, asks what got done, recommends which tasks to push to another day (never moves them), previews tomorrow's fixed commitments, and saves the wrap-up when I agree. Do not use it for planning the morning.
---

# Evening wrap-up

Morning plans the day ahead. **This closes the day out:** what got done, what didn't, and where unfinished work should go. Follow `AGENTS.md`: read-only on my tasks and calendar. You may write `plan/`, `notes/`, and update `data/deadlines.md` when I give new estimates.

## 1. Gather (silently)
1. Run `python3 scripts/digest.py`. "Open tasks for today" and "Rolled over" are what may still be unfinished. "Completed today so far" is what's already done. "Coming up" shows the next days.
2. If `plan/today.json` exists with today's date, read it: that's what I planned this morning, and its `progress` section is what I told you during the day (done, in progress, adjustments).
3. Read tomorrow's events from the primary Google Calendar with the connector's list/search tools only (never create, update, delete or respond). Titles and times only.
4. Read `reference/schedule.md` (tomorrow's classes and free blocks), `data/deadlines.md`, and the last entries of `notes/log.md`.

## 2. Ask first
Show today's still-open tasks (and anything planned but not done) as a short list. **Skip anything already logged as done in `progress`.** Then ask:
- Which are done, and for anything partly done, **how much is left**.
Keep it to that one question. Wait for my answer. Don't assume how long things take.

## 3. Recommend pushes
For each unfinished task, **recommend** a new day (I move it myself; never say you did):
- Before its deadline. Use `data/deadlines.md`.
- In a free block that fits what I said is left, not on a day already packed.
- Away from trips and fixed commitments; earlier if a trip is coming.
- Pinned tasks don't move without asking.
- One line each: task → day, and why. If a task is at risk of missing its deadline, say so plainly.
- Prefer tomorrow only if it genuinely fits. Otherwise the next day that does.
- Late-night work is fine when it's needed to make a deadline. Say so plainly, without warnings.

## 4. Tomorrow, in a few lines
- The first fixed thing tomorrow, anything due, and what tonight's pushes add.
- No weather. No productivity numbers. No recap of the day beyond what got done.

## 5. When I agree
1. Add a `wrapup` object to `plan/today.json` (format in `.claude/skills/morning-check-in/plan-format.md`), keeping the rest of today's plan as it is. **Also set each pushed task's `plan` to `push`, with `push_to` and `reason`, in `tasks`**: the page shows tasks, not the wrap-up. If there is no plan for today, create a minimal file with `date`, `weekday` and `wrapup`.
2. Record each outcome in the status ledger so I'm never reminded about finished work: `python3 scripts/ledger.py add --status done|in-progress|pushed --day <the task's scheduled day, from the digest> --item "title without prefix"` (add `--due` if known, and `--moved-to YYYY-MM-DD` for pushes). The digest already hides tasks marked done.
3. Append a dated "Evening" entry to `notes/log.md`: done, left, suggested pushes, and what I told you about how long things took.
4. Confirm in one line: "Wrap-up saved. Your page is updated."

If I change something, revise and ask again before saving. Never save before I agree.
