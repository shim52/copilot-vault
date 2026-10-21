#!/usr/bin/env bash
# Smoke test: install into a temp dir (scheduler=none so the real home is untouched), exercise the
# runner's control flow with NOW_OVERRIDE, and the notifier's renderers. No model calls.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
T="$HERE/tests/.tmp"; rm -rf "$T"; mkdir -p "$T"
pass() { echo "  ✓ $1"; }; fail() { echo "  ✗ $1"; exit 1; }

cat > "$T/answers.json" <<JSON
{"USER_NAME":"Test User","ROLE":"Tester","ORG_NAME":"TestOrg","TEAM_NAME":"QA","MANAGER_NAME":"Boss",
 "PRODUCT_NAME":"TestProduct","VAULT_PATH":"$T/vault","AUTOMATION":"yes","AUTOMATION_DIR":"$T/auto",
 "WORKDAYS":"1,2,3,4,5","NOTIFY_BACKEND":"file","SCHEDULER":"none","CONNECTOR_TOOLS":""}
JSON
echo "1. installer (non-interactive, json)"
"$HERE/install.sh" --config "$T/answers.json" --yes --json > "$T/summary.json" 2> "$T/install.log" || { cat "$T/install.log"; fail "install.sh failed"; }
python3 -I -c "import json,sys; s=json.load(open('$T/summary.json')); assert s['vault_files_written']>30, s; assert s['tick_dry_run_ok'], s" && pass "installed, dry-run self-check ok"
grep -q "Test User" "$T/vault/CLAUDE.md" && pass "placeholders substituted"
[ -f "$T/vault/01-Org/Product/TestProduct.md" ] && pass "placeholder in filename substituted"
! grep -rl '{{[A-Z_]*}}' "$T/vault" --include='*.md' | grep -v 99-Templates | grep -q . && pass "no unsubstituted placeholders outside templates"
grep -q "date:YYYY-MM-DD" "$T/vault/99-Templates/Daily Note.md" && pass "Obsidian template variables left intact"
[ "$(stat -f %Lp "$T/auto/automation.env" 2>/dev/null || stat -c %a "$T/auto/automation.env")" = "600" ] && pass "automation.env is 0600"

echo "2. idempotency"
echo "my edit" >> "$T/vault/My Tasks.md"
"$HERE/install.sh" --config "$T/answers.json" --yes --json > "$T/summary2.json" 2>/dev/null
grep -q "my edit" "$T/vault/My Tasks.md" && pass "re-run keeps existing files"
python3 -I -c "import json; s=json.load(open('$T/summary2.json')); assert s['vault_files_kept']>30" && pass "re-run reports kept files"

echo "3. runner control flow"
TICK="$T/auto/vault-tick.sh"
out="$(NOW_OVERRIDE='2026-01-07 18:05' bash "$TICK" --dry-run)"; grep -q "RUN_MODE=evening" <<<"$out" && grep -q "BRIEF_DATE=2026-01-08" <<<"$out" && pass "evening side → tomorrow"
out="$(NOW_OVERRIDE='2026-01-08 06:35' bash "$TICK" --dry-run)"; grep -q "RUN_MODE=morning" <<<"$out" && grep -q "BRIEF_DATE=2026-01-08" <<<"$out" && pass "morning side → today"
out="$(NOW_OVERRIDE='2026-01-09 18:05' bash "$TICK" --dry-run)"; grep -q "not a workday" <<<"$out" && pass "Friday evening (brief for Saturday) skipped"
out="$(NOW_OVERRIDE='2026-01-11 18:05' bash "$TICK" --dry-run)"; grep -q "RUN_MODE=evening" <<<"$out" && pass "Sunday evening (brief for Monday) runs"
touch "$T/auto/state/morning-done-2026-01-08"
out="$(NOW_OVERRIDE='2026-01-08 08:05' bash "$TICK" --dry-run)"; grep -q "already done" <<<"$out" && pass "stamped side exits instantly"
out="$(NOW_OVERRIDE='2026-01-08 18:05' bash "$TICK" --dry-run)"; grep -q "scenario: evening" <<<"$out" && pass "other side unaffected by the stamp"

echo "4. 00-Today file-away (--file-away mode)"
mkdir -p "$T/vault/03-Meetings/00-Today"
printf -- '---\nmeeting-type: 1-1\n---\n' > "$T/vault/03-Meetings/00-Today/2026-01-05 Dana.md"
printf -- '---\nmeeting-type: team\n---\n' > "$T/vault/03-Meetings/00-Today/2026-01-05 Planning.md"
printf -- '---\nmeeting-type: 1-1\n---\n' > "$T/vault/03-Meetings/00-Today/2026-01-08 Future.md"
bash "$TICK" --file-away 2026-01-08 >/dev/null
[ -f "$T/vault/03-Meetings/1-1s/2026-01/2026-W02/2026-01-05/2026-01-05 Dana.md" ] && pass "1-1 filed to 1-1s/<month>/<week>/<day>"
[ -f "$T/vault/03-Meetings/Group/2026-01/2026-W02/2026-01-05/2026-01-05 Planning.md" ] && pass "team meeting filed to Group/"
[ -f "$T/vault/03-Meetings/00-Today/2026-01-08 Future.md" ] && pass "today's/upcoming note stays in the inbox"
[ -f "$T/vault/03-Meetings/00-Today/README.md" ] && pass "README stays"

echo "5. notifier renderers"
printf '🔒 Morning brief — Thursday 2026-01-08\n🤝 MEETINGS & PREP · 2 events\n- 10:00  Weekly with [[Dana]] · agenda → 2026-01-08 Dana\n  - [open-item] roadmap draft\n- also: standup\n👥 TEAM\n- ▶️ [[Dana]] started [ABC-12](https://x/ABC-12) — thing\n---\n- no person page: Sam\n' > "$T/digest.txt"
NOTIFY_BACKEND=file NOTIFY_FILE="$T/inbox.md" python3 -I "$T/auto/notify.py" "$T/digest.txt" >/dev/null && grep -q "Weekly with Dana" "$T/inbox.md" && pass "file backend"
python3 -I - "$T/auto/notify.py" "$T/digest.txt" <<'PY'
import importlib.util, sys, json
sp=importlib.util.spec_from_file_location("n", sys.argv[1]); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
t=m.read_digest(sys.argv[2]); p=m.slack_payload(t)
assert p["blocks"][0]["type"]=="header"; assert any(b["type"]=="context" for b in p["blocks"]); assert "<https://x/ABC-12|ABC-12>" in json.dumps(p)
assert "[[" not in json.dumps(p); assert "**" not in m.plain_text(t)
PY
pass "slack block kit + plain renderers"
NOTIFY_BACKEND=slack python3 -I "$T/auto/notify.py" "$T/digest.txt" >/dev/null 2>&1 && fail "slack without URL should fail" || pass "missing URL → non-zero (no false stamp)"

echo "6. dry-run install touches nothing"
"$HERE/install.sh" --config "$T/answers.json" --yes --dry-run --set VAULT_PATH="$T/never" >/dev/null 2>&1; [ ! -e "$T/never" ] && pass "dry-run wrote nothing"

echo "7. scheduler file generation (dry, launchd template)"
python3 -I - "$HERE" <<'PY'
import sys, os, re
tpl=open(os.path.join(sys.argv[1],"automation/schedulers/launchd.plist.template")).read()
assert "{{LAUNCHD_INTERVALS}}" in tpl and "{{AUTOMATION_DIR}}" in tpl
PY
pass "templates carry their placeholders"
echo "ALL GREEN"
