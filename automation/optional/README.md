# Optional extras (all off by default)

## `post-run-hook.sh` — macOS wake chain (opt-in: `WAKE_MACHINE=yes`)
launchd fires on time only if the Mac is awake; a sleeping laptop just back-fills on the next wake, which can be hours late. The fix we settled on: each non-delivering attempt arms the **next** hardware wake with `pmset schedule wake`, optionally anchored by one `pmset repeat` on the first evening slot. That needs a narrow NOPASSWD sudoers rule (see `sudoers.example`) and only works from sleep, not from a full shutdown.

Answering **yes** to the installer's "Wake the machine for scheduled runs?" generates `post-run-hook.sh` here with your slot table and prints the one sudoers command to run (the installer never calls `sudo` itself). Answering **no** leaves nothing here and nothing touches power settings. To do it by hand instead: copy `post-run-hook.example.sh` to `post-run-hook.sh`, make it executable, and edit the slot table. The runner calls it after every attempt with `<run_mode> <brief_date> <HHMM> <brief_ok>`; without the sudoers rule it only logs a warning.

Also learned the hard way: on battery with the lid closed, macOS can force sleep regardless of `caffeinate`; `pmset -b disablesleep 1` for the duration of the run (reset in the EXIT trap) is the only reliable way, and it also needs a sudoers rule.

## `rerun-handler/` — a "🔁 Re-run" button in Slack (macOS)
A tiny AppleScript app registered for a custom URL scheme (`copilot-vault-rerun://`) so a Block Kit `url` button in a failure alert can re-run the pass from desktop Slack with one click, over a plain one-way webhook (no Slack app server needed). Build with `install-rerun-handler.sh`. Known failure modes, all hit in production: the app must be re-signed after editing its Info.plist (TCC blocks unsigned Apple Events), and macOS Launch Services forgets apps that live in hidden folders after OS updates — so re-register with `lsregister -f` on every run (the example hook does this).
