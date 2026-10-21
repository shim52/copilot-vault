#!/bin/zsh
# Build + register CopilotVaultRerun.app — handler for the copilot-vault-rerun:// URL scheme used by
# "🔁 Re-run" buttons in Slack failure alerts (desktop Slack only; custom schemes don't open on phones).
set -u
DIR="${AUTOMATION_DIR:-$HOME/.copilot-vault}"
APP="$DIR/CopilotVaultRerun.app"; SRC="$DIR/.rerun-handler.applescript"
cat > "$SRC" <<'APPLESCRIPT'
on open location this_URL
	set tickPath to (POSIX path of (path to home folder)) & ".copilot-vault/vault-tick.sh"
	do shell script "nohup /bin/bash " & quoted form of tickPath & " --force >/dev/null 2>&1 &"
	display notification "Re-running the vault pass…" with title "🔒 copilot-vault"
end open location
on run
	display notification "This app only handles copilot-vault-rerun:// links." with title "🔒 copilot-vault"
end run
APPLESCRIPT
rm -rf "$APP"; /usr/bin/osacompile -o "$APP" "$SRC" || { echo "FATAL: osacompile failed"; exit 1; }
PLIST="$APP/Contents/Info.plist"; PB=/usr/libexec/PlistBuddy
"$PB" -c "Add :CFBundleURLTypes array" "$PLIST" 2>/dev/null
"$PB" -c "Add :CFBundleURLTypes:0 dict" "$PLIST" 2>/dev/null
"$PB" -c "Add :CFBundleURLTypes:0:CFBundleURLName string copilot-vault.rerun" "$PLIST" 2>/dev/null
"$PB" -c "Add :CFBundleURLTypes:0:CFBundleURLSchemes array" "$PLIST" 2>/dev/null
"$PB" -c "Add :CFBundleURLTypes:0:CFBundleURLSchemes:0 string copilot-vault-rerun" "$PLIST" 2>/dev/null
"$PB" -c "Add :LSUIElement bool true" "$PLIST" 2>/dev/null
"$PB" -c "Add :CFBundleIdentifier string copilot-vault.rerun" "$PLIST" 2>/dev/null || "$PB" -c "Set :CFBundleIdentifier copilot-vault.rerun" "$PLIST"
# PlistBuddy edits invalidate osacompile's ad-hoc signature; TCC blocks Apple Events under an invalid one.
/usr/bin/codesign --sign - --force --deep "$APP" || { echo "FATAL: codesign failed"; exit 1; }
LSREGISTER="/System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/LaunchServices.framework/Versions/A/Support/lsregister"
"$LSREGISTER" -f "$APP"
echo "✓ built + registered $APP — test: open 'copilot-vault-rerun://run'"
echo "  In notify.py, add a Block Kit url button pointing at copilot-vault-rerun://run to failure digests."
