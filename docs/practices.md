# Practices — every rule, and why it exists

Most of these started as a simpler rule that failed in daily use. The failure is noted where it taught something.

## Capture

**Write the conversation, not the structure.** Meeting notes have a prep section (🙋 My topics / 📋 Agenda) and a live section (🗣️ Discussion). Decisions and action items are *derived* from Discussion by the pass afterwards. Earlier templates had "Decisions" and "Action items" sections; in practice they stayed empty while the actions sat in prose, so the pass learned to re-read Discussion for latent to-dos ("I'll…", "let's raise", "need to figure out") and the empty sections were removed.

**Capture topics as `- raise <topic> with [[Person]]`.** One line in the daily note's 📤 To raise. The pass files it onto that person's `📦 Open items`, and it comes back as a seeded topic at the next 1-1. Lines without a resolvable person stay put and are reported — never silently dropped.

**Daily note has fixed capture sections.** 📤 To raise, 🗒️ Notes & quick capture (scratch — never cleared by the pass), ✅ Done today, 📌 To distill later (cleared only for bullets actually filed), ❓ Open questions. The brief lives above them and is machine-owned.

## People

**One page per person, with `📦 Open items`.** Everything outstanding between you and that person — what you owe them, what they owe you, topics to raise — in one checkbox list. This replaced a separate "parking lot" section, which fragmented the same information.

**1-1 prep is mechanical, not editorial.** Every unchecked open item is seeded into the next 1-1 note, one bullet each, linking back `[[Name#📦 Open items]]`. The pass does not get to decide an item "looks resolved" or "reads like an FYI" — it marks those `[fyi]` and seeds them anyway. Early versions curated; items quietly vanished.

**Match people by email local part**, not display name: calendar attendees, chat handles, and page names rarely agree, and domains change after reorgs or acquisitions.

**Pronouns come from the page's `pronouns:` field, never from the name.** Default to they/them.

## Tasks

**My Tasks has exactly three disposition sections** — ⚙️ Implement myself, 👥 Raise with team, 🧭 Raise with managers — plus ❄️ Parked and Done. Each item carries its tag and its source note. Disposition answers "what do I do with this?" and turns out to be the only grouping that survives; grouping by project or priority rotted within weeks.

**Never auto-done, never auto-drop.** The pass may ADD and REWORD checkbox items; it never ticks, deletes, moves between sections, or parks. An item leaves the brief only when you tick its source. Before this rule the pass "helpfully" closed items whose premise looked resolved, and real commitments disappeared.

**One ask = one checkbox.** Distinct asks are never merged, even on a shared theme; the same ask is deduped by adding the new source to the existing line. When unsure, split. Bundled bullets hid individual asks until they were overdue.

**A weekly "pick 5" triage was tried and retired.** It added a ritual and a button and a calendar event, and the owner stopped using it within two months; the brief now simply lists every open item with hard-dated ones first. Don't reintroduce a weekly-pick ritual unless the person asks.

## Dashboard and brief

**The Dashboard is a mirror, never a source.** Every line carries a wikilink to its home. If something actionable has no home, the pass writes it into My Tasks first. Otherwise the Dashboard becomes a second task list that drifts.

**Priority spine, same order everywhere:** 🤝 Meetings & prep → ✅ Your to-dos → 👥 Team → 📡 Org signals. The first version of the brief led with tracker tickets and SLA warnings and was ignored; meetings-first is what the owner actually opens the laptop for.

**Reconcile before rebuild.** The pass reads the current Dashboard first. Checkbox-sourced lines obey never-auto-drop; derived lines ("no person page yet", "prep for <meeting>") re-check their premise and self-resolve. Before this, a stale derived signal resurfaced for days after its cause was fixed.

**Dismissals are a hard gate.** `Automation Dismissals.md` lists items by stable key (message timestamp, ticket id, quoted descriptor). A match always wins over a live re-check, in every section. This is how a wrongly-surfaced signal is killed permanently.

**Org signals are discrete, sourced, linked.** 2–4 lines, each "what's happening → suggested move", each with a clickable source. Never a narrative paragraph.

**Participation guard.** The pass may never say "you haven't replied" or nudge a reply without reading the actual thread and checking the owner's user id among the repliers. Channel reads show reply counts, not who replied; an @-mention in a parent says nothing about replies. This exact mistake shipped twice before the rule was broadened to every nudge framing.

**Group-agenda exclusions.** An attendee's open item is a 1-1 topic by default. It goes on a group agenda only if it is a genuinely shared topic — never a 1-1 accountability item, a precondition-gated item, or an unapproved internal plan (reorgs, ownership changes). Leaking those into a group meeting is a real-world incident waiting to happen.

## Team board

**The tracker feeds only the team board.** No "my tickets" or "team tickets" sections in the brief; personal work is in My Tasks, team work is on `Team Tasks`, and the brief's 👥 section shows only the delta (≤6 lines). Headlines, never alerting: no priority markers, no "at risk", never the string "SLA".

**The board is its own snapshot.** It is diffed against the next night's read; no separate state file. Its header carries the cycle id and "as of" date so the pass can tell a delta night from a cycle-build night.

**Failure honesty.** A failed tracker read leaves the board untouched and writes a "not refreshed (stale as of …)" line. A full-cycle read returning zero issues while a cycle exists is a failure, not a quiet night (an unmatched cycle parameter silently returned empty lists for 19 days once).

## Voice

**Drafts under your name go through a voice profile + exemplars**, are shown in a plain code fence as the last thing in the message, and are never sent without an explicit go. Misses are logged, not silently folded into the rules. Drafts are written in one agreed language; the person translates if needed.

## Knowledge

**Capture → distill → promote.** Rough notes in daily/meeting notes; durable facts promoted to `01-Org`, `04-My-Team`, `05-Knowledge`; the `Log` records what moved where. Knowledge pages carry a `verified:` date; the lint flags ones older than 90 days.

**Durable links over status hashtags.** When a topic has a home page, link it; don't invent a tag.

**Tickets are always links.** Bare ids are dead ends on a phone.

## Working with the assistant interactively

- Ask before outward or destructive actions; reads are always fine; approval in one context does not carry to the next.
- Keep external notes short and factual — state the fact, not how it was found.
- Answer from the vault first and cite pages; say when the vault doesn't know.
- Verify the tagged person is actually in a channel before suggesting a tag.
