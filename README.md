# copilot-vault

A bootstrap for a **private Obsidian knowledge vault with an AI co-pilot** — for anyone whose job is made of people, meetings, projects and a steady stream of things to remember: managers, engineers, PMs, designers, researchers, founders.

You keep writing the way you already do: a daily note, a few lines during a meeting, a topic you want to raise with someone. A scheduled, sandboxed Claude session does the bookkeeping: files your action items where they belong, keeps a running list of open items per person, preps tomorrow's meetings from those lists, keeps a team board current, and delivers a morning brief wherever you read things. You never lose an ask, and you never close one by accident — only you tick boxes.

It was built over several months of daily use and then stripped of everything specific. What's left is the structure and the rules that survived contact with reality (see `docs/design-history.md` for what didn't).

## What you get

**A vault schema** (`vault/`) — numbered folders with a clear job each: `00-Start` (the *How to Use This Vault* playbook; seed the vault if you're already in the role, or a 30-60-90 plan if you're new; open questions; glossary), `01-Org` (durable knowledge about the place), `02-People` (one page per person with their `📦 Open items`), `03-Meetings` (a `00-Today` inbox that files itself into a date hierarchy), `04-My-Team` (overview, processes, projects, a tracker-fed team board), `05-Knowledge`, `06-Daily`, `07-Voice` (your writing style, so drafts sound like you), templates, and four landmark pages: `Index`, `Dashboard`, `My Tasks`, `Log`.

**Rules that make an AI assistant safe in it** (`vault/CLAUDE.md`) — privacy (never leaves disk, never git), never auto-done / never auto-drop, one ask = one checkbox, the Dashboard is a mirror not a source, a dismissal list that always wins, draft-as-me with explicit go before anything is sent.

**Two skills** — `as-me` (voice profile + exemplars → drafts that sound like you) and `vault-lint` (stale facts, orphans, duplicate asks).

**The daily pass** (`automation/`, opt-in) — a portable runner (`bash`, macOS and Linux), a hardened prompt, a notifier with Slack / Discord / generic webhook / ntfy / desktop / file backends, and scheduler templates for launchd, systemd timers and cron. The agent runs allowlist-only with no shell, no web and no outbound tools; the runner delivers the digest to one fixed destination. Each side of the day (evening builds tomorrow's brief, morning refreshes and delivers it) is stamped separately, so extra scheduled fires are free and a missed one self-heals.

## Quick start

```
git clone https://github.com/<you>/copilot-vault && cd copilot-vault
./install.sh                 # interactive
```
or, driven by an agent / CI:
```
./install.sh --print-questions                       # what it will ask, as JSON
./install.sh --config answers.json --yes --json      # non-interactive
```
Requirements: python3, Obsidian, and for the daily pass the `claude` CLI logged in (subscription auth works headless; no API key needed). An AI agent can run the whole setup for you — point it at `BOOTSTRAP.md`.

Then open the vault in Obsidian, start at `Index.md`, create your manager's page from the Person template, and write today's daily note.

## The daily loop

```
you write                      the pass (evening)                 the pass (morning)
──────────────                 ──────────────────────────         ────────────────────────
daily note capture      ──►    distill → My Tasks / people  ──►   catch up on anything new
meeting 🗣️ Discussion   ──►    derive actions, one per box  ──►   refresh today's brief
"raise X with [[Dana]]" ──►    route onto Dana's 📦 items   ──►   refresh the Dashboard
                               seed tomorrow's 1-1 notes           deliver the FULL brief
                               team board delta (tracker)          (the one you read)
                               build tomorrow's brief
                               short "done" ping
```

## Why opt in to the automation?

Without it, this is a well-organized vault you drive by hand with Claude's help in interactive sessions — still worth it. With it, the vault maintains itself: meeting notes never sit undistilled, every commitment surfaces until you close it, and each 1-1 opens with the list of everything outstanding between you and that person. The cost is one or two model sessions a day and a machine that is awake at the scheduled times.

Two extras are **off by default, opt-in, and recommended**: delivery of the brief as a message (Slack / Discord / webhook / ntfy / desktop / file — without it the brief only lives in the vault's daily note) and waking the machine for scheduled runs (a systemd `WakeSystem` timer on Linux, a generated `pmset` wake-chain hook plus one sudoers line on macOS — without it a sleeping laptop gets its brief when it next wakes). The installer asks about each, explains the benefit, and leaves them off unless you say yes.

## Layout of this repo

| Path | What |
|------|------|
| `install.sh` / `install.py` | Installer: copies the vault, substitutes placeholders, installs the automation and a scheduler. Idempotent. |
| `vault/` | The template vault. `{{PLACEHOLDERS}}` are filled at install time. |
| `automation/` | `vault-tick.sh` (runner), `tick-prompt.md` (the pass), `notify.py`, scheduler templates, optional macOS extras. |
| `docs/` | `practices.md` (every rule and why), `automation.md` (architecture + sandbox), `connectors.md` (plugging in calendar/chat/tracker), `design-history.md` (what we tried and retired). |
| `tests/smoke.sh` | Installs into a temp dir and exercises everything that doesn't need a model. |
| `BOOTSTRAP.md` | Instructions for an AI agent to run the setup for someone. |

## Privacy model

The vault never leaves your disk: its `.gitignore` ignores everything, the rules forbid git and uploads, and the daily-pass agent has no outbound tools at all. The only thing that leaves is the digest, posted by the runner to a destination fixed in your config. Webhook URLs live in a `chmod 600` file. Keep the vault out of synced or OS-protected folders.

MIT licensed. Contributions welcome — keep the template free of anything real.
