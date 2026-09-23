#!/bin/bash
export HOME=/tmp XDG_CACHE_HOME=/tmp/.cachex LD_LIBRARY_PATH=/tmp/xl2/lib:/tmp/env/lib PLAYWRIGHT_BROWSERS_PATH=/tmp/pw FONTCONFIG_FILE=/tmp/fonts/fonts.conf
T=$(cat /tmp/.ghtok)
mkdir -p /tmp/lc ; cd /tmp/lc
timeout 40 curl -fsSL -H "Authorization: Bearer $T" "https://api.github.com/repos/heinzo666/sync-assets/contents/lab/qp_login_claim.py?ref=main&t=$RANDOM" | /tmp/env/bin/python -c 'import sys,json,base64;open("c.py","wb").write(base64.b64decode(json.load(sys.stdin)["content"]))'
echo START $(date -u +%T) > /tmp/qclaim.log
/tmp/env/bin/python -u c.py "$1" >> /tmp/qclaim.log 2>&1
echo END $(date -u +%T) >> /tmp/qclaim.log
