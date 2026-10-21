---
name: vault-lint
description: Use when asked to lint, health-check, or tidy the vault — find stale claims, contradictions, orphan pages, broken or missing cross-links, duplicate action items, and template pages never filled in. Read-only report first; fixes only on request.
---

# Vault lint

Produce a short report, grouped by severity. Never edit during the lint pass itself.

1. **Orphans & dead links.** Grep every `[[wikilink]]`; list targets with no page (grouped by how often they're linked — the top ones are pages worth writing) and pages with zero inbound links outside `Log.md`.
2. **Stale knowledge.** `05-Knowledge/` and `01-Org/` pages whose `verified:` (or `updated:`) is older than 90 days; pages still containing template placeholders (`- ` alone under a heading, `[[ ]]`, `{{`).
3. **Contradictions.** Same fact stated differently on two pages (owners, dates, cadences, names). Quote both.
4. **Task hygiene.** Duplicate `- [ ]` lines across `My Tasks.md`, person pages, and meeting notes (same ask, different wording); items in `My Tasks.md` with no disposition tag; `📦 Open items` older than 60 days with no mention since.
5. **Filing.** Notes left in `03-Meetings/00-Today/` with a past date; daily notes with un-routed `📤 To raise` lines; `📌 To distill later` bullets older than a week.
6. **Privacy.** Anything that looks like a secret, credential, or non-work PII.

End with the 3 fixes that would help most, and ask before applying any.
