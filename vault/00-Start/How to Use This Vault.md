---
type: start
tags: [start, playbook]
---

# 🧭 How to Use This Vault

> The moves, on one screen. Three rules under all of them: **you write the conversation, the pass derives the structure** · **everything you owe or are owed is a `- [ ]` at its source** · **only you tick a box**.

## Every day
- **Morning** → open [[Dashboard]] (or the brief at the top of today's `06-Daily/` note). Meetings → your to-dos → team → org signals. Every line links to where the item lives; act there. A mirror, never a source.
- **All day** → today's daily note is your capture surface. Something to raise with someone: `- raise <topic> with [[Person]]` under 📤 To raise. Everything else under 🗒️ Notes & quick capture. A fact worth keeping under 📌 To distill later.
- **Evening** → nothing. The pass distills, files action items, seeds tomorrow's meeting notes, builds tomorrow's brief.

## A 1-1
1. **Before** — the pass creates `03-Meetings/00-Today/<date> <Person>.md` and copies **every unchecked** `📦 Open item` from their page into 🙋 My topics. Missing topic? Add it on the person page (that's the source). No pass: create the note from `99-Templates/1-1.md` yourself.
2. **During** — type under 🗣️ Discussion only. What was said, decided, promised. Don't sort it live.
3. **After** — the pass routes it: your commitments → [[My Tasks]] (one checkbox per ask, tagged `#implement` / `#raise-team` / `#raise-mgr`), theirs → their `📦 Open items`, decisions → the relevant wiki page. The note files itself the next day.
4. **Done with an item** — tick it in the person's `📦 Open items`. That one tick removes it from the next prep, the brief and the Dashboard. Ticking a copy does nothing.

Group meetings work the same way with a 📋 Agenda of shared topics; 1-1 accountability items and unapproved plans are kept off it.

## Your to-dos
- Add as `- [ ]` in [[My Tasks]] under what you'll *do* with it: implement / raise with team / raise with manager. Mention it in a Discussion or quick capture and the pass adds it for you, marked *(derived)*.
- One ask = one checkbox. Person-specific asks live on the person's page. Questions others must answer go in [[Open Questions]].
- Finish by ticking it where it lives. Not happening this quarter: move it to ❄️ Parked with a date. Never delete.

## Weekly, 10 minutes
Scan [[My Tasks]]; tick, park, re-bucket. Read each regular 1-1's `📦 Open items` and make it true. Glance at [[Team Tasks]]. Ask Claude to "lint the vault" now and then.

## Ask Claude in the vault
`claude` in the vault folder knows the rules. Useful: "ingest this" + a doc or thread · "seed the product page from connected sources" (fills an empty page, with citations) · "prep my 1-1 with <Person>" · "refresh the dashboard" · "draft a reply as me" (voice profile, code fence, never sent without your go) · "lint the vault". Something the pass keeps surfacing wrongly → [[Automation Dismissals]].

## 🔗 Related
- Filling the empty pages the first time → [[Seed the Vault]] (already in the role) or [[30-60-90 Plan]] + [[Onboarding Checklist]] (new to it)
- [[Index]] · [[Dashboard]] · [[My Tasks]] · [[Open Questions]]
