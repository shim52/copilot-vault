# 07-Voice — make drafts sound like me

Claude-sounding drafts are the failure mode: too polished, too long, over-structured, wrong vocabulary. This folder fixes that with **explicit rules** (catch polish/length) plus **real exemplars** (carry the texture that rules can't). The `as-me` skill in `.claude/skills/` loads both whenever Claude drafts anything under my name.

## Build it (one session, ~1 hour)

1. **Mine.** Pull a few hundred of your own messages: chat search filtered to you as author across channels you're active in; your comments on tickets/docs. Read-only.
2. **Distill** into [[Voice Profile]]: register per channel (length caps, formality), rhythm & mechanics (sentence length, fragments, punctuation, how you open/close), lexicon (go-to words, abbreviations, emoji you actually use), and a **never-do list** of things the corpus shows you never do (plus AI tics: "Great point!", "I'd be happy to", unrequested summaries, symmetric lists).
3. **Select exemplars** into [[Exemplars]]: 30–50 verbatim messages tagged by **situation** — `quick-ack` · `opinion-pushback` · `ask-request` · `announcement` · `status-update` · `ticket-comment`. Screen out customer names, PII, and sensitive specifics.
4. **Blind test.** Pick ~5 real past threads; have Claude draft your reply without seeing the real one; compare. Ship when light edits suffice.
5. **Keep it honest.** Whenever a draft "doesn't sound like me", log it under `## Misses` in the profile (date, snippet → correction, why). Only you trigger folding misses back into the rules.

Privacy: the corpus, the profile, and the exemplars never leave the vault.
