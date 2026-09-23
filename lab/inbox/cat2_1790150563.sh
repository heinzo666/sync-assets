#!/bin/bash
set -u
tail -c 1600 /tmp/orch_oz075657.log > /tmp/dl.txt 2>/dev/null
echo '---PS---' >> /tmp/dl.txt
ps -eo pid,etime,comm | grep -Ei 'qp_orch|headless' >> /tmp/dl.txt 2>/dev/null
ls -la /tmp/b12 2>/dev/null | head -3 >> /tmp/dl.txt
/tmp/env/bin/python - <<'PY'
import json,base64
b=open('/tmp/dl.txt','rb').read()
open('/tmp/payload.json','w').write(json.dumps({"message":"dl","content":base64.b64encode(b).decode()}))
PY
T=$(cat /tmp/.ghtok)
timeout 45 curl -s -X PUT -H "Authorization: Bearer $T" -H "Content-Type: application/json" \
 https://api.github.com/repos/heinzo666/sync-assets/contents/lab/outbox/dl_1790150563.json \
 --data-binary @/tmp/payload.json -o /dev/null && echo UPLOADED_OK
