---
type: start
tags: [start, playbook]
---

# 🧭 How to Use This Vault — the daily playbook

> The one page that explains the moves. Everything else in the vault is a place; this is what you *do* there. Three rules underneath all of it: **you write the conversation, the pass derives the structure** · **everything you owe or are owed lives as a `- [ ]` at its source** · **only you tick a box**.

## The three pages you actually open

| When | Open | Why |
|------|------|-----|
| Start of the day | [[Dashboard]] (or today's note in `06-Daily/`) | Everything to handle today, in priority order: meetings → your to-dos → team → org signals. It is a **mirror**: every line links to where the item lives. Act there, not here. |
| All day | today's daily note `06-Daily/YYYY-MM-DD.md` | Your capture surface: 📤 To raise, 🗒️ quick notes, ✅ done, 📌 to distill, ❓ questions. |
| Any time you commit to something | [[My Tasks]] | Durable home for your own to-dos, grouped by what you'll do with them. |

Setting an item aside is fine. Pretending it's done is not; nothing leaves the Dashboard or brief until *you* tick it at its source.

## ☀️ Morning (5 minutes)
1. Read the brief at the top of today's daily note (the daily pass writes it; without the pass, read the [[Dashboard]]).
2. For each meeting line, the agenda link opens the seeded note in `03-Meetings/00-Today/`. Skim 🙋 My topics so nothing surprises you.
3. Anything under ✅ Your to-dos that you will do today: start on it. Anything you *won't*: leave it. It stays until done. If it's honestly not happening this quarter, move it to ❄️ Parked in [[My Tasks]] with a date.

## 🤝 A 1-1, start to finish
**Before.** The pass seeds `03-Meetings/00-Today/<date> <Person>.md` from the 1-1 template, pulling **every unchecked item** from that person's `📦 Open items` into 🙋 My topics, each linked back `[[Person#📦 Open items]]`. It does not curate. If a topic is missing, it's because the person page didn't have it: add it there, not only in the meeting note. No pass installed? Create the note from `99-Templates/1-1.md` yourself and copy the open items over.

**During.** Type under 🗣️ Discussion only. Write what was said, decided and promised ("she'll send the doc Thursday", "I'll raise the budget with Sam", "agreed to drop X"). Don't sort it into sections live; that's the pass's job.

**After.** The evening pass reads Discussion and routes:
- things *you* took on → [[My Tasks]] under a disposition (`#implement` / `#raise-team` / `#raise-mgr`), marked *(derived)*, one checkbox per ask
- things *they* took on, or topics that came back → that person's `📦 Open items`
- decisions and durable facts → the relevant page in `01-Org/`, `04-My-Team/`, `05-Knowledge/`
- the note itself → filed under `1-1s/<month>/<week>/<day>/` the next day

**Closing items.** When something between you and that person is resolved, open their page and tick it in `📦 Open items`. That single tick is what removes it from the next 1-1 prep, the brief and the Dashboard. Ticking it in the meeting note or the Dashboard does nothing, because those are copies.

**Between 1-1s.** Something comes up you want to raise next time: in today's daily note write
```
- raise <topic> with [[Person]]
```
under 📤 To raise. The pass files it onto their `📦 Open items`; it surfaces at the next 1-1. Or add it on their page directly. Lines without a resolvable `[[Person]]` stay where they are and the digest tells you.

## 👥 Group meetings
Same shape, lighter prep: the pass seeds a note from `99-Templates/Meeting.md` with 🧭 Background and a 📋 Agenda built from genuinely shared topics. 1-1 accountability items, anything gated on an unmade decision, and unapproved plans are deliberately kept out of group agendas. Capture under 🗣️ Discussion; the pass routes action items the same way.

## ✅ Adding and finishing your own to-dos
- **Add:** write it as `- [ ]` in [[My Tasks]] under the section that says what you'll do with it: implement it yourself, raise it with the team, or raise it with your manager. Mention it in a meeting's Discussion or 🗒️ quick capture and the pass will add it for you, tagged *(derived)*; re-bucket if it guessed wrong.
- **One ask = one checkbox.** Never bundle two asks into one line; the pass won't either.
- **Finish:** tick it where it lives. That's it. The pass may later move ticked lines to the page's Done section; it never ticks for you.
- **Person-specific asks** go on the person's `📦 Open items`, not in My Tasks. **Questions someone else must answer** go in [[Open Questions]]; they're seeded into the right 1-1 too.
- **Park, don't delete.** `- [ ] item *(parked 2026-10-22: waiting for budget)*` under ❄️ Parked keeps it out of the brief but on the record.

## 🌙 End of day (2 minutes)
1. Anything still in your head → 📤 To raise (person topics), 🗒️ Notes & quick capture (everything else), ✅ Done today (optional, it feeds the [[Log]]).
2. A fact worth keeping (a decision, how a system works, who owns what) → 📌 To distill later. The pass promotes it to a durable page and clears the bullet. Or promote it yourself and clear it.
3. Nothing else. The evening pass distills, files, seeds tomorrow's meetings, builds tomorrow's brief and (if you turned delivery on) pings you when done.

## 🗓️ Weekly (10 minutes)
- Scan [[My Tasks]] top to bottom. Tick what's done, park what's stalled, re-bucket what's drifted.
- Open the person pages of your regular 1-1s; `📦 Open items` should read true. Stale items you'll never raise: tick them with a note, don't leave them to haunt every prep.
- Glance at [[Team Tasks]] for the team's board and at the ❓ section of [[Open Questions]] for anything you can now resolve.
- Ask Claude in the vault to "lint the vault" occasionally; it flags stale pages, orphans and duplicate items.

## 🤖 Asking Claude inside the vault
Run `claude` in the vault folder; `CLAUDE.md` teaches it the schema. Useful asks:
- "ingest this" + a pasted doc, thread or ticket → takeaways filed to the right pages, Log updated
- "what do I know about <topic / person>?" → answered from the vault, with page links
- "prep my 1-1 with <Person>" → seeded topics on demand, without waiting for the pass
- "refresh the dashboard" → the mirror rebuilt by hand
- "draft a reply as me" → goes through [[Voice Profile]] + [[Exemplars]], shown in a code fence, never sent without your go
- "lint the vault" → health report, fixes only on request

When the pass surfaces something you never want to see again, add it to [[Automation Dismissals]]. That gate always wins.

## 🔗 Related
- First time here → [[Seed the Vault]] (already in the role) or [[30-60-90 Plan]] + [[Onboarding Checklist]] (new to it)
- [[Index]] · [[Dashboard]] · [[My Tasks]] · [[Open Questions]]
