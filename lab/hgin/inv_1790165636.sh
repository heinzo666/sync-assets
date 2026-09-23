#!/bin/bash
echo "HOST=$(hostname) UID=$(id)"
for t in python3 python /usr/bin/python3 /usr/local/bin/node node npm php git curl unzip crontab; do printf '%-22s %s\n' "$t" "$(command -v $t || echo MISSING)"; done
python3 -V 2>&1 | head -1 ; node -v 2>&1 | head -1 ; php -v 2>/dev/null | head -1
ls ~ | head -12 ; df -h ~ | tail -1
