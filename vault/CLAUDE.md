# CLAUDE.md — Vault rules & schema

This is **{{USER_NAME}}'s private Obsidian vault** for operating as **{{ROLE}} @ {{ORG_NAME}}**.
It is a personal knowledge system with an AI co-pilot: raw capture goes in, durable cross-linked knowledge and a daily brief come out.

## 🔒 Privacy rules (non-negotiable)

- **This folder is PRIVATE and SENSITIVE.** Never share, upload, publish, sync, or commit it anywhere external.
- **Never `git init`, `git add`, `git commit`, or `git push`** from this folder. A `.gitignore` that ignores everything is in place as a backstop — do not weaken it.
- **Never send the contents** to any external service, web endpoint, or third party. The only outbound channel is the daily-pass digest, which the *runner* (not the agent) posts to one fixed private destination.
- Internal company information (chat threads, docs, tickets, meeting notes) lives here. Treat it as confidential.
- Refer to the product as **"{{PRODUCT_NAME}}"**, not "the app" or "the product".
- Avoid storing unnecessary PII (work emails are acceptable; avoid other personal data).

## 🗂️ How this vault is organized (the schema)

Inspired by the "LLM Wiki" pattern: raw notes get distilled into durable, cross-linked knowledge pages.

| Folder | Purpose |
|--------|---------|
| `00-Start/` | `How to Use This Vault` (the daily playbook — point me there when I ask how something works), `Seed the Vault` (already in the role) or `30-60-90 Plan` + `Onboarding Checklist` (new to it), plus the permanent `Open Questions` and `Glossary`. |
| `01-Org/` | Durable knowledge about the organization: `Product/`, `How-We-Work/` (dev cycle, rituals, release process), `Org-and-Teams/`. |
| `02-People/` | One page per person (manager, team, peers, cross-functional). Entity pages with `📦 Open items`. |
| `03-Meetings/` | Meeting notes. `00-Today/` is the shared inbox for today's notes (all types); the evening pass files each into its scope by `meeting-type:` — `1-1`→`1-1s/`, else→`Group/` — under a `<YYYY-MM>/<YYYY-Www>/<YYYY-MM-DD>/` date hierarchy. |
| `04-My-Team/` | My domain as {{ROLE}}: team overview, processes, projects, the `Team Tasks` board. |
| `05-Knowledge/` | Concept & reference wiki pages (domain, tooling, methods). |
| `06-Daily/` | Daily notes (`YYYY-MM-DD.md`). Quick capture + the auto-generated morning brief; distill into the folders above. |
| `07-Voice/` | My writing voice: profile + exemplars, loaded by the `as-me` skill whenever Claude drafts under my name. |
| `99-Templates/` | Templates for daily notes, meetings, 1-1s, people, projects, knowledge pages. |
| `_attachments/` | Images/files embedded in notes. |
| `Index.md` | Home / map-of-content. Start here. |
| `Dashboard.md` | The complete roll-up of everything I should handle. A **mirror** of sources, never a source itself. |
| `My Tasks.md` | Durable home for my own action items, by disposition. |
| `Log.md` | Append-only chronological activity log. |
| `Automation Dismissals.md` | Items I've told the daily pass to stop surfacing. A hard gate. |

## 🔗 Conventions

- **Link liberally** with `[[wikilinks]]`. A link to a not-yet-created page is fine — it marks a page worth writing.
- **People** are referenced as `[[Name]]` and resolve to a page in `02-People/`. Check a person page's `pronouns:` frontmatter before using a pronoun; never infer pronouns from a name — default to they/them.
- **Meeting notes** use the meeting templates and link the people + topics involved. They capture only the **conversation** (🗣️ Discussion); the daily pass derives decisions and action items from it.
- **Daily capture → distill:** rough notes land in `06-Daily/` or meeting notes, then durable facts get promoted into `01-Org/`, `04-My-Team/`, or `05-Knowledge/`.
- Dates are absolute (`YYYY-MM-DD`).
- **Tags are real Obsidian tags** (`#tag`), never plain `[bracket]` labels (those aren't clickable).
- **Prefer durable links over status hashtags.** When a topic has a durable home page, reference it with a `[[wikilink]]` (heading link where it helps) instead of inventing a hashtag. In 1-1 notes, topics pulled from a person's 📦 Open items link back to that section — `[[Name#📦 Open items]]`.
- **Tracker tickets are always clickable links** (`[ABC-123](https://…)`), never bare IDs.
- **Capture topics with `📤 To raise`.** In the daily note, write `- raise <topic> with [[Person]]`; the daily pass files each onto that person's `📦 Open items` so it surfaces at your next 1-1. Lines without a resolvable `[[Person]]` stay put.
- **My action items live in [[My Tasks]]** under exactly one disposition: `## ⚙️ Implement myself` (#implement) · `## 👥 Raise with team` (#raise-team) · `## 🧭 Raise with managers` (#raise-mgr, prefixed **[[{{MANAGER_NAME}}]]**). `## ❄️ Parked` is mine alone and shows only as a count.
- **The daily pass never closes my items — only I do.** It only ADDS and rewords my `- [ ]` action items / `📦 Open items`; it never ticks `[x]`, never deletes one, never moves one between sections, and never drops one on a "looks resolved" guess. An item leaves the brief/Dashboard only after **I** tick its source.
- **One ask = one checkbox.** Each distinct ask is its own `- [ ]` line, so nothing important gets bundled away. Dedupe the *same* ask; never merge *different* asks.
- **The Dashboard is a mirror, never a source.** Every Dashboard line carries a `[[wikilink]]` to its home page. An item with no durable home gets written into [[My Tasks]] first.
- **Dismissals are a hard gate.** Anything listed in [[Automation Dismissals]] (by stable key) is never re-surfaced, regardless of what live data suggests.

## 🤖 Working with me (Claude)

- **Orient me:** when I ask how to do something in this vault (1-1s, to-dos, the brief, what to open), or when the vault looks fresh (`Log.md` holds only the setup entry, or `01-Org`/`04-My-Team` pages are still empty shells), point me to `00-Start/How to Use This Vault.md` first and offer to seed the empty pages.
- **Seed pages:** when I ask to fill, seed or populate an empty page (product, How We Work, Team Overview, a knowledge page), use the `seed-page` skill: read the vault and the connected sources read-only, draft with citations, route gaps to `Open Questions`. Never invent facts to fill a section.
- **Ingest:** when I share a doc / chat thread / ticket / page, read it, discuss takeaways, update the relevant wiki pages, and append to `Log.md`.
- **Query:** answer from the vault first; cite the page(s). Say when the vault doesn't have it rather than guessing.
- **Lint:** when asked (or via the `vault-lint` skill), health-check for stale claims, contradictions, orphan pages, and missing cross-links.
- **Draft as me:** anything that will be sent under my name goes through the `as-me` skill (07-Voice profile + exemplars). Show drafts in a plain code fence as the **last thing** in the message, in {{DRAFT_LANGUAGE}}, and never send or post without my explicit go.
- **Ask before outward or destructive actions** (messages, emails, ticket writes, deletes). Reads are always fine. Approval in one context doesn't extend to the next.
- **Keep external notes short and factual.** In comments or messages, state the fact; no narration of how it was found.
- **Connected sources:** {{CONNECTORS_LINE}} Use them to learn the org, the product, and what my team actually owns — read-only unless I say otherwise.
