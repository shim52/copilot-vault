---
name: as-me
description: Use whenever drafting ANY text that will be sent or posted under the vault owner's name — chat messages or replies, ticket comments or descriptions, doc comments, PR comments, or text they ask you to "write for me" / "reply for me" / "comment for me". Also when they ask to rewrite something "in my voice". Loads their voice profile + real exemplars so drafts sound like them, not AI-generated.
---

# Write as me

Claude-sounding drafts are the failure mode: too polished, too long, wrong vocabulary. Real voices are shorter, more direct, lightly imperfect.

## Steps

1. **Read** `07-Voice/Voice Profile.md` (rules + never-do list + length caps). If it is still the empty template, say so and offer to run the build steps in `07-Voice/README.md` first; draft plainly in the meantime.
2. **Classify the situation**: quick-ack | opinion-pushback | ask-request | announcement | status-update | ticket-comment. Read that section of `07-Voice/Exemplars.md` and anchor on 3–5 exemplars (rhythm, length, openers — not content).
3. **Pick the language**: {{DRAFT_LANGUAGE}} unless told otherwise. Technical terms stay in English.
4. **Draft.** Match the register's *typical* length, not its cap.
5. **Self-check before showing** — reject and redraft if the draft:
   - contains anything on the profile's Never-do list;
   - exceeds the register's p90 cap (cut content, don't densify);
   - reads "assistant-polished" — every sentence grammatically perfect and joined by transitions;
   - keeps arguing after the answer — cut reassurance clauses and stacked justifications;
   - uses symbols or writerly verbs where plain words would do.
6. **Present the draft in a plain code fence** (never a `>` blockquote — terminals render bars that break copy-paste). Bare URLs and ticket IDs in copy-paste drafts, never chat-specific link markup.
7. **The draft is the last thing in the message.** No tool calls after it (text before a tool call may not render). Ask for the go in the next turn.
8. **Never send or post without an explicit go.** Vault rule, no exceptions.
9. **On "that doesn't sound like me"**: append to `## Misses` in the Voice Profile (date, snippet → correction, why). Never fold misses into the rules yourself — only the owner triggers a re-distill.

## Notes
- Refer to the product as "{{PRODUCT_NAME}}" when naming it formally; in casual internal messages people usually say the feature name.
- Exemplars are style anchors. Never reuse their content or names verbatim.
