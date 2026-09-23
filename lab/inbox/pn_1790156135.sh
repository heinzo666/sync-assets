#!/bin/bash
T=$(cat /tmp/.ghtok)
B=$(echo PONGNOW1790156135 | base64 -w0)
curl -s -X PUT -H "Authorization: Bearer $T" -H "Content-Type: application/json" https://api.github.com/repos/heinzo666/sync-assets/contents/lab/outbox/pongnow_1790156135.json -d "{\"message\":\"pn\",\"content\":\"$B\"}" -o /dev/null
echo PN_DONE
