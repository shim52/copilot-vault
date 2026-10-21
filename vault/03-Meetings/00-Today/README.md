# 00-Today — today's meeting inbox (all types)

Today's meeting session notes land **here** so they're easy to find during the day (the `00-` prefix pins this folder to the top of `03-Meetings/`). It is the **shared** inbox for **every** meeting type — 1-1s *and* group meetings.

- The **evening** pass seeds tomorrow's notes here (1-1s from `99-Templates/1-1.md`, substantive group meetings from `99-Templates/Meeting.md`), with your relevant topics pre-filled.
- Drop any note you write by hand here too.

The runner files everything out of this folder into its **scope's** dated home, keyed off two things in each note:

- the `YYYY-MM-DD <…>.md` filename prefix → picks the `<YYYY-MM>/<YYYY-Www>/<YYYY-MM-DD>/` folder
- the `meeting-type:` front-matter → picks the scope: `1-1` → `03-Meetings/1-1s/…`, anything else → `03-Meetings/Group/…`

A note always lands in the folder for *its own* date, and only after that date has passed — so a skipped pass self-heals on the next one, and today's notes stay findable here all day.

## Parsing the note (what the pass extracts)

Meeting notes capture only the **conversation** live — 🗣️ Discussion (plus the pre-meeting 🙋 My topics / 📋 Agenda). The pass reads Discussion and routes the structured bits itself:

- **Action items I own** → [[My Tasks]], tagged with their disposition (`#implement` · `#raise-team` · `#raise-mgr`). One ask = one checkbox.
- **Items someone else owes** → that person's `📦 Open items`.
- **Decisions / durable facts** → the relevant wiki page (`01-Org/`, `04-My-Team/`, `05-Knowledge/`).

This `README.md` has no date prefix, so the filing step ignores it.
