# CLAUDE.md — for the agent working in this repo

This is **copilot-vault**, a bootstrap for a private Obsidian knowledge vault with an AI co-pilot. Nothing here is a user's data; it is a template plus an installer.

- If the person wants to **set up their own vault**, follow `BOOTSTRAP.md` — it is written for you. Ask the questions conversationally, write a config JSON, run `./install.sh --config <file> --yes --json`, then walk them through the next steps the installer prints.
- If the person wants to **change the template**, edit under `vault/` (the template vault) or `automation/` (the daily pass). Placeholders are `{{UPPER_SNAKE}}` and are substituted by `install.py`; keep them in sync with the `QUESTIONS` table there.
- Run `tests/smoke.sh` before claiming anything works. It installs into a temp dir and exercises the runner in dry-run mode without touching the real home directory's schedulers.
- `docs/practices.md` is the why behind every rule in `vault/CLAUDE.md` and `automation/tick-prompt.md`. Read it before changing either; many rules exist because the simpler version failed in production.
- Never put real names, companies, channels, ticket ids, or URLs into the template. Example values live only in `copilot.config.example.json` and are fictional.
