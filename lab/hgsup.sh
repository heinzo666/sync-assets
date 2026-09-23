#!/bin/bash
export HOME=/tmp XDG_CACHE_HOME=/tmp/.cachex LD_LIBRARY_PATH=/tmp/xl2/lib:/tmp/env/lib PLAYWRIGHT_BROWSERS_PATH=/tmp/pw FONTCONFIG_FILE=/tmp/fonts/fonts.conf
L=/tmp/orch_oz093708.log; D=/tmp/b15
for i in $(seq 80); do
  grep -q '"tok_login": true' "$L" 2>/dev/null && { echo WINNER >> "$L"; break; }
  pkill -f qp_orch5; sleep 2; rm -f "$L"
  /tmp/env/bin/python -u "$D/qp_orch5.py" oz093708 >> "$L" 2>&1
  sleep 425
done
echo HGSUP_EXIT >> "$L"
