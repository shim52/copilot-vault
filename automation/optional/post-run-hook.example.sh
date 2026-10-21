#!/usr/bin/env bash
# Example post-run hook (macOS): arm the next hardware wake when this attempt did not deliver.
# Called by vault-tick.sh as: post-run-hook.sh <run_mode> <brief_date> <HHMM> <brief_ok>
# Requires the sudoers rule in sudoers.example. Edit the slot table to match your schedule.
run_mode="$1"; brief_date="$2"; now=$((10#$3)); ok="$4"
[ "$ok" = 1 ] && exit 0
today="$(date '+%m/%d/%Y')"; tomo="$(date -v+1d '+%m/%d/%Y')"
if   [ "$now" -ge 1700 ] && [ "$now" -lt 2030 ]; then nd="$today 21:00:00"
elif [ "$now" -ge 2030 ];                          then nd="$tomo 06:30:00"
elif [ "$now" -lt 700 ];                           then nd="$today 08:00:00"
elif [ "$now" -lt 830 ];                           then nd="$today 08:45:00"
else exit 0; fi
sudo -n /usr/bin/pmset schedule wake "$nd" && echo "wake-chain: armed $nd" || echo "WARN: could not arm wake (sudoers rule missing?)"
