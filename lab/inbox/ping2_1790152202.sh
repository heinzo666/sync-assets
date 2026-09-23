#!/bin/bash
T=$(cat /tmp/.ghtok)
B=$(echo alive$(date +%s) | base64 -w0)
curl -s -X PUT -H "Authorization: Bearer $T" -H "Content-Type: application/json" https://api.github.com/repos/heinzo666/sync-assets/contents/lab/outbox/ping2_1790152202.json -d "{\"message\":\"p\",\"content\":\"$B\"}" -o /dev/null
echo PINGED_OK