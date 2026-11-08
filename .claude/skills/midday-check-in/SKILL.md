---
name: midday-check-in
description: Midday check-in for during the day, between the morning plan and the evening wrap-up. Use when I tell you how the day is going. That means progress ("just finished X", "done with Y", "started Z", "how's my day going?") or trouble ("I'm struggling with this", "running behind", "this is taking longer", "I need more time"). Keeps a running tab of the day, responds briefly, and when I'm behind recommends where the rest should go. Not for planning the morning or wrapping up the night.
---

# Midday check-in

I'll message you throughout the day. **Keep a running tab** and respond briefly. Follow `AGENTS.md`: read-only on my tasks and calendar. You may write `plan/`, `notes/`, and update `data/deadlines.md` when I say to.

## Setup (quick, silently)
1. Get the current local time with `date`.
2. Read `plan/today.json`. If it has today's date, that's the plan and the tab. If not, say once that no plan is saved for today (offer the morning check-in), and still log what I tell you in a minimal file with `date`, `weekday` and `progress`.
3. Read `data/deadlines.md` for due dates and estimates. Read `reference/schedule.md` (rest of today's classes and free blocks) only if you need to reschedule. Run `python3 scripts/digest.py` to see a task's scheduled day, and the next days if pushing a task.

## A. Progress ("just finished X", "started Y", "how's it going?")
1. Match what I said to a task or block in today's plan.
2. **Log it right away** in two places. Logging a fact I told you doesn't need my approval.
   - `progress` in `plan/today.json` (format in `.claude/skills/morning-check-in/plan-format.md`): add to `done` with the time, or set `in_progress` with a short note. Keep the rest of the file as is.
   - The status ledger, so you never remind me about it later: `python3 scripts/ledger.py add --status done --day YYYY-MM-DD --item "title without prefix"` (`--day` is the day the task is scheduled in the task list, shown in the digest; add `--due YYYY-MM-DD` if known). Use `--status in-progress` for partial progress. If I correct myself, undo it with `python3 scripts/ledger.py remove --day ... --item ...`.
3. **Reply in one to three lines.** Acknowledge it plainly (no cheerleading speeches), say what's next on the plan, and whether I'm ahead or behind.
4. If it frees real time, offer **one** suggestion (e.g. pull a later task forward), and only change the plan if I agree.
5. For "how's my day going?": done so far, in progress, what's left today, any risk. Short.
6. If a task took noticeably more or less time than its estimate, add one line to `notes/log.md` (task, actual versus estimate).

## B. Trouble ("struggling", "running behind", "need more time")
1. **Ask one question** unless I already said: how much is left, or how much more time you think you need. Don't guess or assume.
2. Look at the rest of today, my deadlines, and free time today and the next days. Recommend one of:
   - a later free block today,
   - a specific day to push it to, before its deadline,
   - splitting it across days.
   Name what lighter work could slip instead. Say plainly if the deadline is at risk. Prefer a day away from trips and commitments. No late-night catch-up unless something is due before I'd wake up.
3. Keep it short: the recommendation and a one-line reason. I move tasks in Google Tasks myself; never say you did.
4. **Only after I agree:** update the schedule and the task's `plan`/`push_to` in `plan/today.json`, add a line to `progress.adjustments`, and log it in `notes/log.md`. Record the move in the ledger: `python3 scripts/ledger.py add --status pushed --day <its current scheduled day> --item "title" --moved-to YYYY-MM-DD`.
5. If this is a recurring kind of task that keeps running over, ask once if I want its estimate in `data/deadlines.md` updated. Only change it if I say yes.

## Rules
- Never mention productivity percentages.
- Short replies. This is a quick check-in, not a new planning session.
- Don't re-plan the whole day unless I ask.
